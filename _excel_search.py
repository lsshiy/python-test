# -*- coding: utf-8 -*-
"""
Excel文字列検索ツール (Tkinter)
- .xls / .xlsx のセル文字列に部分一致 or 正規表現検索
- 左リスト: ファイル名のみ表示
- 右リスト: 選択ファイル内ヒット詳細（シート!セル:値）
- 左リストのコピー機能
- ダブルクリックでファイルを開く
- 複製機能あり
"""

import os
import sys
import threading
import queue
import traceback
import shutil
import re
from tkinter import (
    Tk, StringVar, BooleanVar, IntVar, Frame, Label, Entry, Button, Checkbutton,
    Listbox, Scrollbar, END, SINGLE, filedialog, messagebox
)

_missing = []
try:
    import openpyxl
except Exception:
    _missing.append("openpyxl (for .xlsx)")
try:
    import xlrd
except Exception:
    _missing.append("xlrd (for .xls)")

def colnum_to_letters(n: int) -> str:
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

class ExcelSearcherApp:
    def __init__(self, root: Tk):
        self.root = root
        root.title("Excel 文字列検索ツール")

        # 変数
        self.query_var = StringVar()
        self.folder_var = StringVar()
        self.dest_folder_var = StringVar()
        self.regex_var = BooleanVar(value=False)
        self.display_mode = IntVar(value=0)  # 左リストは常にファイル名のみ
        self.include_subdirs = BooleanVar(value=True)

        self.results = []

        # 上段：検索文字列
        top = Frame(root)
        top.pack(fill="x", padx=8, pady=6)
        Label(top, text="検索文字列:").pack(side="left")
        Entry(top, textvariable=self.query_var, width=40).pack(side="left", padx=6)
        Button(top, text="検索", command=self.start_search).pack(side="left", padx=4)
        Checkbutton(top, text="正規表現", variable=self.regex_var).pack(side="left", padx=(0,12))
        Checkbutton(top, text="サブフォルダを含める", variable=self.include_subdirs).pack(side="left", padx=(0,12))
        

        # 中段：検索フォルダ + 参照
        mid = Frame(root)
        mid.pack(fill="x", padx=8, pady=6)
        Label(mid, text="検索フォルダ:").pack(side="left")
        Entry(mid, textvariable=self.folder_var, width=50).pack(side="left", padx=6, fill="x", expand=True)
        Button(mid, text="参照...", command=self.browse_folder).pack(side="left", padx=4)

        # オプション
        opt = Frame(root)
        opt.pack(fill="x", padx=8, pady=6)
        
        # 出力ボックス（左右2列）
        out = Frame(root)
        out.pack(fill="both", expand=True, padx=8, pady=6)

        # 左：ファイルリスト
        left_frame = Frame(out)
        left_frame.pack(side="left", fill="both", expand=True)
        Label(left_frame, text="検索結果（ファイル名のみ）").pack(anchor="w")

        left_frame_sub = Frame(left_frame)
        left_frame_sub.pack(fill="both", expand=True)

        self.file_listbox = Listbox(left_frame_sub, selectmode=SINGLE)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        yscroll1 = Scrollbar(left_frame_sub, orient="vertical", command=self.file_listbox.yview)
        yscroll1.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=yscroll1.set)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.file_listbox.bind("<Double-Button-1>", self.open_selected_file)

        left_frame_sub2 = Frame(left_frame)
        left_frame_sub2.pack(side="bottom", fill="x")
        Label(left_frame_sub2, text="すべてコピー：").pack(side="left")
        Button(left_frame_sub2, text="絶対パス", command=self.copy_results_to_clipboard_abspath).pack(side="left", padx=3)
        Button(left_frame_sub2, text="ファイル名", command=self.copy_results_to_clipboard_filename).pack(side="left", padx=3)
        Button(left_frame_sub2, text="ファイル名（拡張子無し）", command=self.copy_results_to_clipboard_filename_without_extension).pack(side="left", padx=3)

        # 右：セル詳細リスト
        right_frame = Frame(out)
        right_frame.pack(side="left", fill="both", expand=True, padx=(10,0))
        Label(right_frame, text="ヒット詳細（シート!セル:値）").pack(anchor="w")

        right_frame_sub = Frame(right_frame)
        right_frame_sub.pack(fill="both", expand=True)

        self.detail_listbox = Listbox(right_frame_sub, selectmode=SINGLE)
        self.detail_listbox.pack(side="left", fill="both", expand=True)
        yscroll2 = Scrollbar(right_frame_sub, orient="vertical", command=self.detail_listbox.yview)
        yscroll2.pack(side="right", fill="y")
        self.detail_listbox.config(yscrollcommand=yscroll2.set)
        self.detail_listbox.bind("<Double-Button-1>", self.open_selected_detail)

        right_frame_sub2 = Frame(right_frame)
        right_frame_sub2.pack(side="bottom", fill="x")
        Label(right_frame_sub2, text="すべてコピー：").pack(side="left")
        Button(right_frame_sub2, text="値", command=self.copy_result_values_to_clipboard).pack(side="left", padx=3)

        # 複製先 + 実行
        dup = Frame(root)
        dup.pack(fill="x", padx=8, pady=(0,8))
        Label(dup, text="ファイル複製先:").pack(side="left")
        Entry(dup, textvariable=self.dest_folder_var, width=45).pack(side="left", padx=6, fill="x", expand=True)
        Button(dup, text="参照...", command=self.browse_dest_folder).pack(side="left", padx=4)
        Button(dup, text="複製実行", command=self.duplicate_files).pack(side="left", padx=8)

        # ステータス
        self.status_var = StringVar(value="準備完了")
        Label(root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8, pady=(0,6))

        self.queue = queue.Queue()
        self.worker = None
        self.root.after(100, self._poll_queue)

        if _missing:
            messagebox.showwarning("ライブラリ不足", "以下をインストールしてください:\n- " + "\n- ".join(_missing))

    # ====== UI操作 ======
    def browse_folder(self):
        d = filedialog.askdirectory(title="検索フォルダを選択")
        if d:
            self.folder_var.set(d)

    def browse_dest_folder(self):
        d = filedialog.askdirectory(title="複製先フォルダを選択")
        if d:
            self.dest_folder_var.set(d)

    def copy_results_to_clipboard_abspath(self):
        lines = [os.path.abspath(r["path"]) for r in self.results]
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"ファイル名リストをコピーしました（{len(lines)} 件）")
    def copy_results_to_clipboard_filename(self):
        lines = [os.path.basename(r["path"]) for r in self.results]
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"ファイル名リストをコピーしました（{len(lines)} 件）")
    def copy_results_to_clipboard_filename_without_extension(self):
        lines = [os.path.splitext(os.path.basename(r["path"]))[0] for r in self.results]
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"ファイル名リストをコピーしました（{len(lines)} 件）")
    def copy_result_values_to_clipboard(self):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        lines = [h["value"] for h in self.results[idx].get("hits", [])]
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(f"値リストをコピーしました（{len(lines)} 件）")
        
            

    # ====== 左選択で右リスト更新 ======
    def on_file_select(self, event=None):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        hits = self.results[idx].get("hits", [])
        self.detail_listbox.delete(0, END)
        for h in hits:
            line = f"{h['detail']}: {h['value']}"
            self.detail_listbox.insert(END, line)

    # ====== 右リストダブルクリックで Excel 開く ======
    def open_selected_file(self, event=None):
        sel_file_idx = self.file_listbox.curselection()
        if not sel_file_idx:
            return
        idx = sel_file_idx[0]
        file_path = self.results[idx]['path']  # files は Listbox に入れたフルパスのリスト
        print(f"{file_path=}")
        os.startfile(file_path)  # Windows で標準アプリで開く

    def open_selected_detail(self, event=None):
        sel_file_idx = self.file_listbox.curselection()
        sel_detail_idx = self.detail_listbox.curselection()
        if not sel_file_idx or not sel_detail_idx:
            return
        file_path = self.results[sel_file_idx[0]]["path"]
        try:
            if sys.platform.startswith("win"):
                os.startfile(file_path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", file_path])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを開けませんでした:\n{file_path}\n\n{e}")

    # ====== 検索 ======
    def start_search(self):
        query = self.query_var.get().strip()
        folder = self.folder_var.get().strip()
        if not query:
            messagebox.showwarning("入力不足", "検索文字列を入力してください。")
            return
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("入力不足", "有効な検索フォルダを指定してください。")
            return
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("実行中", "前回の検索がまだ実行中です。")
            return

        self.results.clear()
        self.file_listbox.delete(0, END)
        self.detail_listbox.delete(0, END)
        self.status_var.set("検索中…")

        regex_mode = self.regex_var.get()
        pattern = None
        if regex_mode:
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error as e:
                messagebox.showerror("正規表現エラー", f"正規表現が無効です:\n{e}")
                return

        self.worker = threading.Thread(
            target=self._search_worker,
            args=(query, folder, regex_mode, pattern),
            daemon=True
        )
        self.worker.start()

    def _enqueue(self, kind, payload=None):
        self.queue.put((kind, payload))

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "append":
                    # payload: {"path": str, "hit": {"detail": str, "value": str}}
                    file_path = payload["path"]
                    hit = payload["hit"]
                    # ファイル単位で results にまとめる
                    found = next((r for r in self.results if r["path"] == file_path), None)
                    if not found:
                        found = {"path": file_path, "hits": []}
                        self.results.append(found)
                        self.file_listbox.insert(END, os.path.abspath(file_path))
                    found["hits"].append(hit)
                    self.status_var.set(f"ヒット: {sum(len(r['hits']) for r in self.results)} 件")
                elif kind == "status":
                    self.status_var.set(payload)
                elif kind == "done":
                    self.status_var.set(payload or f"完了: ヒット {len(self.results)} ファイル,  {sum(len(r['hits']) for r in self.results)} セル")
                elif kind == "error":
                    messagebox.showerror("エラー", payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

    # ====== 検索ワーカー ======
    def _search_worker(self, query, folder, regex_mode, pattern):
        q_lower = query.lower()
        try:
            if self.include_subdirs.get():
                for rootdir, _, files in os.walk(folder):
                    for i, name in enumerate(files):
                        self._enqueue("status", f"検索中…： {i}/{len(files)} {rootdir}")
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in (".xlsx", ".xls"):
                            continue
                        full = os.path.join(rootdir, name)
                        try:
                            if ext == ".xlsx" and "openpyxl" in sys.modules:
                                self._scan_xlsx(full, q_lower, regex_mode, pattern)
                            elif ext == ".xls" and "xlrd" in sys.modules:
                                self._scan_xls(full, q_lower, regex_mode, pattern)
                        except Exception:
                            self._enqueue("error", f"{full}\n{traceback.format_exc(limit=1)}")
            else:
                files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
                file_count = len(files)
                for i, f in enumerate(files, 1):  # 1始まりにすると進捗表示が自然
                    full = os.path.join(folder, f)
                    self._enqueue("status", f"検索中： {i}/{file_count} {folder}")
                    ext = os.path.splitext(name)[1].lower()
                    if ext not in (".xlsx", ".xls"):
                        continue
                    try:
                        if ext == ".xlsx" and "openpyxl" in sys.modules:
                            self._scan_xlsx(full, q_lower, regex_mode, pattern)
                        elif ext == ".xls" and "xlrd" in sys.modules:
                            self._scan_xls(full, q_lower, regex_mode, pattern)
                    except Exception:
                        self._enqueue("error", f"{full}\n{traceback.format_exc(limit=1)}")

            self._enqueue("done", None)
        except Exception as e:
            self._enqueue("error", str(e))

    def _scan_xlsx(self, path, q_lower, regex_mode, pattern):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            for ws in wb.worksheets:
                for row in ws.iter_rows(values_only=False):
                    for cell in row:
                        v = cell.value
                        if v is None:
                            continue
                        v_str = str(v)
                        hit = False
                        if regex_mode:
                            if pattern.search(v_str):
                                hit = True
                        else:
                            if q_lower in v_str.lower():
                                hit = True
                        if hit:
                            coord = cell.coordinate
                            self._enqueue("append", {"path": path, "hit": {"detail": f"{ws.title}!{coord}", "value": v_str}})
        finally:
            wb.close()

    def _scan_xls(self, path, q_lower, regex_mode, pattern):
        import xlrd
        book = xlrd.open_workbook(path, on_demand=True)
        try:
            for sh_name in book.sheet_names():
                sh = book.sheet_by_name(sh_name)
                for r in range(sh.nrows):
                    for c in range(sh.ncols):
                        v = sh.cell_value(r, c)
                        if v is None:
                            continue
                        v_str = str(v)
                        hit = False
                        if regex_mode:
                            if pattern.search(v_str):
                                hit = True
                        else:
                            if q_lower in v_str.lower():
                                hit = True
                        if hit:
                            coord = f"{colnum_to_letters(c+1)}{r+1}"
                            self._enqueue("append", {"path": path, "hit": {"detail": f"{sh_name}!{coord}", "value": v_str}})
        finally:
            book.release_resources()

    # ====== 複製 ======
    def duplicate_files(self):
        dest = self.dest_folder_var.get().strip()
        if not dest or not os.path.isdir(dest):
            messagebox.showwarning("入力不足", "有効な複製先フォルダを指定してください。")
            return
        if not self.results:
            messagebox.showinfo("情報", "複製対象がありません（検索結果が空です）。")
            return

        unique_paths = sorted({r["path"] for r in self.results})
        copied = 0
        errors = []

        for src in unique_paths:
            try:
                fname = os.path.basename(src)
                base, ext = os.path.splitext(fname)
                dst = os.path.join(dest, fname)
                counter = 1
                while os.path.exists(dst):
                    dst = os.path.join(dest, f"{base} ({counter}){ext}")
                    counter += 1
                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                errors.append(f"{src} -> {dest}\n{e}")

        msg = f"複製完了: {copied} ファイル"
        if errors:
            msg += f"\nエラー {len(errors)} 件あり"
        self.status_var.set(msg)
        if errors:
            error_text = "\n".join(errors)
            messagebox.showerror("複製エラー詳細", error_text)

def main():
    root = Tk()
    app = ExcelSearcherApp(root)
    root.geometry("1000x600")
    root.mainloop()

if __name__ == "__main__":
    main()
