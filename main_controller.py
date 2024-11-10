import time
import entry_manager as em
import window_checker as wc
import scroll_controller as sc
import config_handler as ch

class MainController:
    def __init__(self):
        self.entries = []
        self.current_index = 0
        self.entry_manager = em.EntryManager()
        self.window_checker = wc.WindowChecker()
        self.scroll_controller = sc.ScrollController()
        self.config_handler = ch.ConfigHandler()

    def load_entries(self):
        self.entries = self.config_handler.load_config("config.json")
    
    def save_entries(self):
        self.config_handler.save_config("config.json", self.entries)
    
    def switch_to_next_window(self):
        current_entry = self.entries[self.current_index]
        self.window_checker.verify_all_windows(self.entries)
        
        # ウィンドウ切り替え
        self.window_checker.activate_window(current_entry)
        if current_entry["scroll_enabled"]:
            self.scroll_controller.enable_scroll(current_entry)
        
        # 次のウィンドウに切り替え
        self.current_index = (self.current_index + 1) % len(self.entries)

    def start(self):
        while True:
            self.switch_to_next_window()
            time.sleep(self.entries[self.current_index]["display_time"])
