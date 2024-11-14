import customtkinter as ctk
from datetime import datetime, timedelta

# サンプルの予定データ
events = {
    "2024-11-14": ["Meeting with team", "Lunch with client"],
    "2024-11-15": ["Project deadline", "Yoga class"],
    "2024-11-16": ["Family dinner"],
}

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.current_year = 2024
        self.current_month = 11
        
        # メインレイアウト
        self.create_header()
        self.create_calendar()

    def create_header(self):
        # ヘッダーフレームを作成
        header_frame = ctk.CTkFrame(self.root)
        header_frame.grid(row=0, column=0, columnspan=7, pady=(10, 5), sticky="nsew")
        
        # 前月ボタン
        prev_button = ctk.CTkButton(header_frame, text="<", command=self.prev_month)
        prev_button.grid(row=0, column=0, padx=5, pady=5)

        # 月と年のラベル
        self.month_label = ctk.CTkLabel(header_frame, text="", font=("Helvetica", 16))
        self.month_label.grid(row=0, column=1, columnspan=5, padx=20)
        
        # 次月ボタン
        next_button = ctk.CTkButton(header_frame, text=">", command=self.next_month)
        next_button.grid(row=0, column=6, padx=5, pady=5)

        # 初期ラベルの設定
        self.update_month_label()

    def create_calendar(self):
        # カレンダーの日付部分を表示
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for col, day in enumerate(days):
            ctk.CTkLabel(self.root, text=day, font=("Helvetica", 12, "bold")).grid(row=1, column=col, padx=5, pady=5)

        # 各列と行のweightを設定（動的リサイズ対応）
        for i in range(7):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(2, 10):
            self.root.grid_rowconfigure(i, weight=1)

        # 日付セルを作成
        self.display_days()

    def display_days(self):
        # 日付セルをクリア
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) >= 2:
                widget.grid_forget()
                
        # 月の最初と最後の日付を取得
        start_date = datetime(self.current_year, self.current_month, 1)
        start_day = start_date.weekday()  # 月の開始曜日
        days_in_month = (start_date.replace(month=self.current_month % 12 + 1, day=1) - timedelta(days=1)).day

        # カレンダーに日付を配置
        day = 1
        row = 2
        for col in range(start_day, 7):
            self.display_day(day, row, col)
            day += 1

        while day <= days_in_month:
            row += 1
            for col in range(7):
                if day > days_in_month:
                    break
                self.display_day(day, row, col)
                day += 1

    def display_day(self, day, row, col):
        date_str = f"{self.current_year}-{self.current_month:02}-{day:02}"
        day_frame = ctk.CTkFrame(self.root, corner_radius=8, border_width=1)
        day_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        # 日付ラベル
        day_label = ctk.CTkLabel(day_frame, text=str(day), font=("Helvetica", 10, "bold"))
        day_label.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # 予定アイテムを表示
        if date_str in events:
            for i, event in enumerate(events[date_str]):
                self.display_event(day_frame, event, i + 1)

    def display_event(self, day_frame, event_text, row):
        event_frame = ctk.CTkFrame(day_frame, corner_radius=4, fg_color="lightgray", width=90, height=20)
        event_frame.grid(row=row, column=0, padx=3, pady=2, sticky="nw")

        # イベントテキスト
        event_label = ctk.CTkLabel(event_frame, text=event_text, font=("Helvetica", 8), anchor="w")
        event_label.pack(fill="both", expand=True, padx=5, pady=2)

    def update_month_label(self):
        self.month_label.configure(text=f"{self.current_year}-{self.current_month:02}")

    def prev_month(self):
        # 前月に切り替え
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_month_label()
        self.display_days()

    def next_month(self):
        # 翌月に切り替え
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_month_label()
        self.display_days()

# メインウィンドウの設定
ctk.set_appearance_mode("light")  # Light or Dark
ctk.set_default_color_theme("blue")  # テーマカラーの設定
root = ctk.CTk()
root.title("カレンダー")
root.geometry("750x600")

# カレンダーアプリを起動
app = CalendarApp(root)

root.mainloop()
