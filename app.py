from config_handler import ConfigHandler
from window_checker import WindowChecker
from scroll_controller import ScrollController
from entry_manager import EntryManager
from main_controller import MainController

def main():
    # 設定ファイルを読み込む
    config_handler = ConfigHandler()
    entries = config_handler.load_config("config.json")
    
    # EntryManagerを使ってエントリーデータを管理
    entry_manager = EntryManager()
    entry_manager.entries = entries
    
    # メインコントローラーでシステムのフローを制御
    main_controller = MainController(entry_manager)
    main_controller.start()

if __name__ == "__main__":
    main()
