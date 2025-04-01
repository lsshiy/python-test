import win32com.client
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Excelファイルのパス
file_path = r"C:\path\to\your\file.xlsx"

# === Excelを開いてPower Queryとピボットテーブルを更新 ===
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False  # Excelを非表示で開く
wb = excel.Workbooks.Open(file_path)

# Power Queryとピボットテーブルの更新
wb.RefreshAll()
excel.CalculateUntilAsyncQueriesDone()  # 非同期更新が終わるまで待機

# 保存して閉じる
wb.Save()
wb.Close()
excel.Quit()

# === データの取得 ===
df = pd.read_excel(file_path, sheet_name="PivotTableSheet")  # シート名を指定
df.columns = ["名前", "合計"]  # A列：名前, B列：合計

# === グラフの作成 ===
plt.figure(figsize=(10, 6))
sns.barplot(x="合計", y="名前", data=df, palette="Blues_r")  # 横棒グラフ（名前順）
plt.xlabel("合計")
plt.ylabel("名前")
plt.title("ピボットテーブルのデータ可視化")
plt.grid(axis="x", linestyle="--", alpha=0.7)  # 軽いグリッド線

# グラフを表示
plt.show()