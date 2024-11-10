import json

class EntryManager:
    def __init__(self):
        self.entries = []
    
    def load_entries(self, file_path):
        """設定ファイルからエントリーデータを読み込む"""
        try:
            with open(file_path, "r") as file:
                self.entries = json.load(file)
        except FileNotFoundError:
            print(f"{file_path} が見つかりません。空のエントリーリストを読み込みます。")
            self.entries = []
    
    def save_entries(self, file_path):
        """エントリーデータを設定ファイルに保存する"""
        with open(file_path, "w") as file:
            json.dump(self.entries, file, indent=4)
    
    def add_entry(self, file_path, app_name, window_title, display_time, scroll_enabled=False):
        """新しいエントリーを追加する"""
        entry = {
            "file_path": file_path,
            "app_name": app_name,
            "window_title": window_title,
            "display_time": display_time,
            "scroll_enabled": scroll_enabled
        }
        self.entries.append(entry)
    
    def remove_entry(self, window_title):
        """指定したウィンドウタイトルのエントリーを削除する"""
        self.entries = [entry for entry in self.entries if entry["window_title"] != window_title]
    
    def update_entry(self, window_title, file_path=None, app_name=None, display_time=None, scroll_enabled=None):
        """指定したウィンドウタイトルのエントリーを更新する"""
        for entry in self.entries:
            if entry["window_title"] == window_title:
                if file_path: entry["file_path"] = file_path
                if app_name: entry["app_name"] = app_name
                if display_time is not None: entry["display_time"] = display_time
                if scroll_enabled is not None: entry["scroll_enabled"] = scroll_enabled
