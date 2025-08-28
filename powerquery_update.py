import win32com.client as win32
import pandas as pd
import time
import os

excel_path = fr"C:\path\to\file.xlsx"
sheet_name = "シート名"

# Excel起動
excel = win32.Dispatch("Excel.Application")
excel.Visible = False

try:
    # 編集用で開こうとする
    wb = excel.Workbooks.Open(excel_path, UpdateLinks=0, ReadOnly=False)

    # 成功したら → Power Query 更新
    wb.RefreshAll()

    # クエリ更新が終わるまで待つ
    while excel.CalculateUntilAsyncQueriesDone() != 0:
        time.sleep(1)

    wb.Save()
    wb.Close()
    excel.Quit()

    print("更新してから読み込みました")

except Exception as e:
    print("編集ロック中のため、読み取り専用で開きます:", e)

    # 読み取り専用で開く
    wb = excel.Workbooks.Open(excel_path, ReadOnly=True)
    wb.Close()
    excel.Quit()

# pandasでDataFrameに変換（1行目を列名にする）
df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

print(df.head())
