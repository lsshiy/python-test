import json

class ConfigHandler:
    def load_config(self, file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # 設定ファイルがない場合は空のリストを返す
    
    def save_config(self, file_path, entries):
        with open(file_path, "w") as file:
            json.dump(entries, file, indent=4)
