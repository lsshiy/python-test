import os
import tkinter as tk
from tkinter import filedialog
import re
import subprocess
import sys


class FileCard(tk.Frame):
    def __init__(self, master, remove_callback):
        super().__init__(master, bd=2, relief="groove", padx=5, pady=5)
        self.remove_callback = remove_callback
        self.folder_path = tk.StringVar()
        self.filter_text = tk.StringVar()
        self.regex_enabled = tk.BooleanVar(value=False)
        self.file_list = []

        # 上部UI
        tk.Entry(self).pack(fill="both")
        path_frame = tk.Frame(self)
        path_frame.pack(fill="x", pady=2)

        tk.Entry(path_frame, textvariable=self.folder_path).pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="参照", command=self.browse_folder).pack(side="left", padx=3)

        # ファイル表示リスト
        self.listbox = tk.Listbox(self, height=10)
        self.listbox.pack(fill="both", expand=True, pady=2)
        self.listbox.bind("<Double-1>", self.open_selected_file)

        # 下部UI
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill="x", pady=2)

        filter_entry = tk.Entry(filter_frame, textvariable=self.filter_text)
        filter_entry.pack(side="left", fill="x", expand=True)
        filter_entry.bind("<KeyRelease>", lambda e: self.apply_filter())

        tk.Checkbutton(filter_frame, text="正規表現", variable=self.regex_enabled,
                       command=self.apply_filter).pack(side="left", padx=3)

        tk.Button(filter_frame, text="削除", command=self.delete_card).pack(side="left", padx=3)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.load_files()

    def load_files(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            return
        self.file_list = [os.path.join(folder, f) for f in os.listdir(folder)
                          if os.path.isfile(os.path.join(folder, f))]
        self.apply_filter()

    def apply_filter(self):
        pattern = self.filter_text.get()
        if self.regex_enabled.get() and pattern:
            try:
                re.compile(pattern)
            except re.error:
                return  # 無効な正規表現なら更新しない

        self.listbox.delete(0, tk.END)
        for file_path in self.file_list:
            name = os.path.basename(file_path)
            if not pattern:
                match = True
            else:
                if self.regex_enabled.get():
                    match = re.search(pattern, name) is not None
                else:
                    match = pattern in name
            if match:
                self.listbox.insert(tk.END, name)

    def open_selected_file(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        visible_name = self.listbox.get(index)
        full_path = next((p for p in self.file_list if os.path.basename(p) == visible_name), None)
        if full_path:
            if sys.platform == "win32":
                os.startfile(full_path)
            else:
                subprocess.Popen(["xdg-open", full_path])

    def delete_card(self):
        self.remove_callback(self)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("フォルダビューア")
        self.geometry("1000x400")

        self.card_container = tk.Frame(self)
        self.card_container.pack(fill="both", expand=True)

        self.add_button = tk.Button(self, text="追加", command=self.add_card)
        self.add_button.pack(side="bottom", pady=5)

        self.cards = []

    def add_card(self):
        card = FileCard(self.card_container, self.remove_card)
        card.pack(side="left", fill="both", expand=True, padx=5, pady=5)  # 横方向に広がる
        self.cards.append(card)

    def remove_card(self, card):
        card.destroy()
        self.cards.remove(card)


if __name__ == "__main__":
    app = App()
    app.mainloop()
