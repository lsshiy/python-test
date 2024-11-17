import test2
import customtkinter as ctk
from datetime import datetime, timedelta, date
import time
import threading

# サンプルデータ
schedule_data = [
    {"id":"ABCD1234", "name":"甲乙イロハニホヘト", "phase":"チリヌルヲ", "time":"①", "date":datetime(2024,11,17,0,0,0), "count":"123"},
]

# メインウィンドウの作成
root = ctk.CTk()
root.geometry("400x300")
root.title("Main Window")


# サブウィンドウの設定
ctk.set_appearance_mode("light")  # Light or Dark
ctk.set_default_color_theme("blue")  # テーマカラーの設定

sub = ctk.CTkToplevel(root)
sub.title("カレンダー")
sub.geometry("750x600")
sub2 = ctk.CTkToplevel(root)
sub2.title("カレンダー")
sub2.geometry("750x600")

# カレンダーアプリを起動
app = test2.CalendarApp(sub, schedule_data)
app2 = test2.CalendarApp(sub2, schedule_data, 2024, 12)

# メインループの開始
root.mainloop()
