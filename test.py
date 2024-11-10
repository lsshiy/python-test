import config_handler as ch
import window_checker as wc
import scroll_controller as sc
import main_controller as mc
import time

# def test_config_handler():
#     config_handler = ch.ConfigHandler()
    
#     # 設定ファイルが空の状態で読み込み
#     config = config_handler.load_config("test_config.json")
#     assert isinstance(config, list), "Config should be a list"
    
#     # 設定ファイルにエントリを追加して保存
#     config.append({"file_path": "test.txt", "app_name": "Notepad"})
#     config_handler.save_config("test_config.json", config)
    
#     # 設定ファイルの内容が正しく保存されたか確認
#     loaded_config = config_handler.load_config("test_config.json")
#     assert len(loaded_config) == 1, "Config should contain one entry"
#     assert loaded_config[0]["file_path"] == "test.txt", "File path mismatch"


def test_main_controller():
    main_controller = mc.MainController()
    main_controller.load_entries()
    
    # 最初のウィンドウ切り替え
    main_controller.switch_to_next_window()
    
    # 一定時間経過後に次のウィンドウに切り替わることを確認
    time.sleep(2)  # ウィンドウが切り替わる時間
    current_entry = main_controller.entries[main_controller.current_index]
    assert current_entry["window_title"] == "test.txt", "Expected Notepad to be active"
    
    # スクロール機能が有効な場合にスクロールが実行されるか確認
    if current_entry["scroll_enabled"]:
        assert current_entry["file_path"] in current_entry["window_title"], "Scroll should be performed"

# test_config_handler()
test_main_controller()