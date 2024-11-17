import customtkinter as ctk
from datetime import datetime, timedelta, date

# font="BIZ UDPゴシック"
font="Meiryo"

class CalendarApp:
    def __init__(self, root, schedule_data=[], year=None, month=None):
        self.root = root
        self.current_year = datetime.now().year if year is None else year
        self.current_month = datetime.now().month if month is None else month
        self.schedule_data = schedule_data
        
        # メインレイアウト
        self.create_header()
        self.create_calendar()

    def create_header(self):
        # ヘッダーフレームを作成
        header_frame = ctk.CTkFrame(self.root)
        header_frame.grid(row=0, column=0, columnspan=7, pady=(10, 5), sticky="nsew")
        
        # 前月ボタン
        prev_button = ctk.CTkButton(header_frame, text="<", command=self.prev_month, fg_color="#CFCFCF")
        prev_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # 月と年のラベル
        self.month_label = ctk.CTkLabel(header_frame, text="", font=(font, 40, "bold"))
        self.month_label.grid(row=0, column=1, pady=10)
        
        # 次月ボタン
        next_button = ctk.CTkButton(header_frame, text=">", command=self.next_month, fg_color="#CFCFCF")
        next_button.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        header_frame.grid_propagate(True)  # サイズの自動調整を無効化
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)
        header_frame.grid_rowconfigure(0, weight=1)
        

        # 初期ラベルの設定
        self.update_month_label()

    def create_calendar(self):
        # カレンダーの日付部分を表示
        days = ["日", "月", "火", "水", "木", "金", "土"]
        for col, day in enumerate(days):
            fg_color = "#DBDBDB"
            text_color = "#020406"
            if (datetime.now().weekday()+1)%7 == col:
                fg_color = "#03045E"
                text_color = "#FAFAFA"
            label = ctk.CTkLabel(self.root, text=day, font=(font, 28, "bold"), fg_color=fg_color, text_color=text_color, corner_radius=10, justify="center")
            label.grid(row=1, column=col, sticky="nsew", padx=2, ipady=5)

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
        start_day = (start_date.weekday()+1)%7  # 月の開始曜日
        days_in_month = (start_date.replace(month=self.current_month % 12 + 1, day=1) - timedelta(days=1)).day
        print(f"start_date:{start_date} start_day:{start_day}")
        # カレンダーに日付を配置
        day = 1
        row = 2
        for col in range(start_day, 7):
            print("col:",col)
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

        day_label_color = "#CFCFCF"       
        text_color = "black"
        frame_color = "#dbdbdb"
        if datetime.strptime(date_str, "%Y-%m-%d").date() == date.today():
            # 今日
            day_label_color = "#3B64A1"
            text_color = "#ecf0f1"
            frame_color = "#d1e0ee"
        elif col == 0 or col == 6:
            # 土日
            frame_color = "#9E9E9E"
            day_label_color = "#757575"
        

        # フレーム
        day_frame = ctk.CTkFrame(self.root, fg_color=frame_color)
        day_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        day_frame.grid_propagate(False)  # サイズの自動調整を無効化

        # 日付フレーム
        day_label_frame = ctk.CTkFrame(day_frame, fg_color=day_label_color)
        day_label_frame.grid(row=0, column=0, padx=3, pady=2, sticky="nsew")
        day_label = ctk.CTkLabel(day_label_frame, text=str(day), font=(font, 25, "bold"), text_color=text_color)
        day_label.grid(row=0, column=0, sticky="nw", padx=5, pady=0)
        day_frame.grid_rowconfigure(0, weight=0)

        day_frame.grid_columnconfigure(0, weight=1)  # 列は1列のみで均等に

        # 予定アイテムを表示
        for i, data in enumerate([entry for entry in self.schedule_data if entry["date"].date() == datetime.strptime(date_str, "%Y-%m-%d").date()]):
            self.display_event(day_frame, data, i + 1)


    def display_event(self, day_frame, data, row):
        event_frame = ctk.CTkFrame(day_frame, corner_radius=6, fg_color="#03045E")
        event_frame.grid(row=row, column=0, padx=3, pady=2, sticky="nsew")
        day_frame.grid_rowconfigure(row, weight=1)
        # イベントテキスト
        # event_label = ctk.CTkLabel(event_frame, text=data[0], font=("LINESeedJP_TTF_0", 20), anchor="w")
        event_label = ctk.CTkLabel(event_frame, text=f"{data["id"]}\n {data["phase"]}{data["time"]}  {data["count"]}機", font=(font, 20, "bold"), anchor="nw", text_color="#ecf0f1", justify="left")
        event_label.pack(fill="both", expand=True, padx=7, pady=3)

    def update_month_label(self):
        self.month_label.configure(text=f"{self.current_year}年　{self.current_month:02}月")

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

if __name__ == "__main__":
    # メインウィンドウの設定
    ctk.set_appearance_mode("light")  # Light or Dark
    ctk.set_default_color_theme("blue")  # テーマカラーの設定

    root = ctk.CTk()
    root.title("カレンダー")
    root.geometry("750x600")

    # カレンダーアプリを起動
    app = CalendarApp(root)

    root.mainloop()
