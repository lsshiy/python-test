import pandas as pd
import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import keyboard
import tempfile

CSV_FILE = "data.csv"
SCROLL_SPEED = 0.02  # s単位
WAIT_BEFORE_SCROLL = 3  # 待時間

HTML_FILE = "table_view.html"
CURRENT_DIR = os.getcwd()

# HTMLテンプレート生成
def generate_html(df):
    rows = ""
    for row in df.itertuples(index=False):
        row_class = "highlight" if str(row[2]).strip() else ""
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        rows += f'<tr class="{row_class}">{cells}</tr>\n'

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: sans-serif;
                padding: 20px;
                margin: 0;
                background: #f9f9f9;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background: white;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}
            tr.highlight {{
                background-color: yellow;
            }}
            .scroll-container {{
                height: 90vh;
                overflow-y: auto;
                scroll-behavior: smooth;
                padding: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="scroll-container" id="container">
            <table>
                <thead>
                    <tr>{"".join(f"<th>{col}</th>" for col in df.columns)}</tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <script>
            const container = document.getElementById("container");
            const scrollSpeed = {int(SCROLL_SPEED * 1000)};
            const waitBeforeScroll = {WAIT_BEFORE_SCROLL * 1000};
            let scrollInterval = null;
            let manualScrollTimeout = null;
            let lastScrollTop = container.scrollTop;

            function startScroll() {{
                if (scrollInterval) return;
                scrollInterval = setInterval(() => {{
                    if (container.scrollTop + container.clientHeight >= container.scrollHeight) {{
                        clearInterval(scrollInterval);
                        scrollInterval = null;
                        setTimeout(() => {{
                            location.reload();
                        }}, 3000);
                    }} else {{
                        container.scrollTop += 1;
                        lastScrollTop = container.scrollTop;  // 自動スクロール時も更新
                    }}
                }}, scrollSpeed);
            }}

            function stopScroll() {{
                if (scrollInterval) {{
                    clearInterval(scrollInterval);
                    scrollInterval = null;
                }}
            }}

            container.addEventListener('scroll', () => {{
                const currentScrollTop = container.scrollTop;
                if (currentScrollTop < lastScrollTop) {{  // 上スクロール時のみ
                    stopScroll();
                    if (manualScrollTimeout) clearTimeout(manualScrollTimeout);
                    manualScrollTimeout = setTimeout(() => {{
                        startScroll();
                    }}, 3000);
                }}
                lastScrollTop = currentScrollTop;
            }});

            setTimeout(startScroll, waitBeforeScroll);
        </script>

    </body>
    </html>
    """
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

# WebDriver起動
def launch_browser():
    edge_options = Options()
    service = Service(executable_path=fr"F:\python-test\chromedriver.exe")
    temp_profile = tempfile.mkdtemp()
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option("useAutomationExtension", False)
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=service, options=edge_options)
    driver.get("file://" + os.path.abspath(HTML_FILE))
    return driver

# CSV監視 再読込
class CSVHandler(FileSystemEventHandler):
    def __init__(self, driver):
        self.driver = driver

    def on_modified(self, event):
        if event.src_path.endswith(CSV_FILE):
            print("CSV更新検出 再読込")
            try:
                df = pd.read_csv(CSV_FILE)
                generate_html(df)
                self.driver.refresh()
            except Exception as e:
                print("読み込みエラー:", e)

driver = None

# エスケープキーで終了
def esc_listener():
    print("ESCキーで終了")
    while True:
        if keyboard.is_pressed("esc"):
            print("終了中...")
            if driver:
                driver.quit()  # ブラウザを閉じる
            os._exit(0)

        time.sleep(0.1)

def main():
    global driver
    if not os.path.exists(CSV_FILE):
        print(f"{CSV_FILE} が見つかりません")
        return

    df = pd.read_csv(CSV_FILE)
    generate_html(df)
    driver = launch_browser()

    event_handler = CSVHandler(driver)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    threading.Thread(target=esc_listener, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
