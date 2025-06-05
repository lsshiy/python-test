import tkinter as tk
import subprocess
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

TARGET_URL = "https://www.google.com"

def kill_edge_processes():
    # subprocess.call('taskkill /F /IM msedge.exe /T', shell=True)
    subprocess.call('taskkill /F /IM chromedriver.exe /T', shell=True)
    time.sleep(1.5)

def open_url_with_retry():
    driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    options = webdriver.ChromeOptions()
    # options.add_argument("--inprivate")
    # options.add_argument("--no-first-run")

    service = Service(executable_path=driver_path)

    for attempt in range(2):  # 最大2回までリトライ
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(5)  # 5秒でタイムアウト
            driver.get(TARGET_URL)
            if TARGET_URL in driver.current_url:
                print("正常にアクセスできました。")
                return
            else:
                raise Exception("想定外のURLにアクセスしました")
        except Exception as e:
            print(f"[{attempt+1}回目] エラー発生: {e}")
            kill_edge_processes()
        time.sleep(1)

    print("再試行してもアクセスできませんでした。")

# GUI
root = tk.Tk()
root.title("Edge 自動起動とリトライ")

btn = tk.Button(root, text="URL にアクセス", command=open_url_with_retry)
btn.pack(padx=20, pady=20)

root.mainloop()
