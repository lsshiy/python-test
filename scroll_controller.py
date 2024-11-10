import time
from selenium import webdriver
import pyautogui

class ScrollController:
    def enable_scroll(self, entry):
        if entry["type"] == "web":
            # Seleniumを使用してブラウザを操作
            driver = webdriver.Chrome()
            driver.get(entry["file_path"])

            # スクロールのための設定
            scroll_pause_time = 0.1  # 各スクロールの間隔（秒）
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            scroll_step = 10  # スクロール量

            # 少しずつスクロール
            while current_position < scroll_height:
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                current_position += scroll_step
                time.sleep(scroll_pause_time)  # スクロールをゆっくり実行

            # 最後にページの一番下にスクロール
            driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        elif entry["type"] == "excel":
            # Excel操作を実行（pywin32などを使う）
            pass
        else:
            # 一般的なスクロール
            pyautogui.scroll(10)  # 上にスクロール