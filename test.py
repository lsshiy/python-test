from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from openpyxl import load_workbook
import os

# Excelファイルのパス
file_path = 'リスト.xlsx'

# Excelファイルを読み込む
workbook = load_workbook(file_path)

# シート名を指定してシートを取得
sheet = workbook['シート1']  # シート名を指定

# A列のすべての値をリストに格納
column_a_values = [cell.value for cell in sheet['A'] if cell.value is not None]

# 結果を表示
print(column_a_values)

###############################

# Edgeのオプション設定
options = Options()
options.add_argument("start-maximized")  # ブラウザを最大化して起動

# EdgeのWebDriverのパスを指定してサービスを起動
service = Service("msedgedriver.exe")  # msedgedriverのパスを指定

# Edgeブラウザを起動
driver = webdriver.Edge(service=service, options=options)

# Googleニュースにアクセス
driver.get("file://" + os.path.abspath("index.html"))

# 明示的な待機を設定（例: ページ下部のフッターが読み込まれるまで待機）
try:
    footer = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))  # 例: bodyの読み込みまで待機
    )
    print("ページが読み込まれました。スクロールを開始します。")
except:
    print("ページ読み込みに失敗しました。")


# すべてのtr要素を取得
tr_elements = driver.find_elements("tag name", "tr")
# 各行（tr要素）を確認
for tr in tr_elements:
    # 行内のすべてのセル（td要素）を取得
    td_elements = tr.find_elements("tag name", "td")
    # 各セルをチェックして一致するか確認
    for td in td_elements:
        td_text = td.text.strip().lower()  # テキストを小文字化して前後の空白を除去
        if td_text in map(str.lower, column_a_values):  # リストの値と一致するかチェック
            # JavaScriptを使って行全体の背景色を黄色に設定
            driver.execute_script("arguments[0].style.backgroundColor = 'yellow';", tr)
            break  # 一致が見つかったら、その行は処理済みとして次の行へ移る



# スクロールするためのJavaScriptコード
scroll_speed = 1  # スクロール速度（ピクセル単位）
interval = 10      # スクロール間隔（ミリ秒）

scroll_script = """
window.scrollComplete = false;
const scrollSpeed = arguments[0];
const interval = arguments[1];


function smoothScroll() {
    const scrollPosition = window.scrollY;
    window.scrollBy(0, scrollSpeed);
    const newScrollPosition = window.scrollY;

    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight || scrollPosition === newScrollPosition) {
        clearInterval(scrollInterval);
        window.scrollComplete = true;  // スクロール完了を示すフラグ
    }
}

const scrollInterval = setInterval(smoothScroll, interval);
"""

# JavaScriptを実行
driver.execute_script(scroll_script, scroll_speed, interval)

# スクロールが完了するまで待機
while not driver.execute_script("return window.scrollComplete;"):
    sleep(0.1)  # 少し待機して再度チェック

print("スクロールが完了しました。")

# 終了処理
driver.quit()  # 処理が終わったらブラウザを閉じる