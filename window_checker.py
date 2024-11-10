import psutil
import os
import win32gui # type: ignore

class WindowChecker:
    def is_window_open(self, entry):
        for proc in psutil.process_iter(['pid', 'name']):
            if entry["app_name"].lower() in proc.info['name'].lower():
                return True
        return False
    
    def launch_window(self, entry):
        os.startfile(entry["file_path"])
    
    def verify_all_windows(self, entries):
        for entry in entries:
            if not self.is_window_open(entry):
                print(f"Launching {entry['app_name']}...")
                self.launch_window(entry)

    def activate_window(self, entry):
        def enum_callback(hwnd, lParam):
            if win32gui.GetWindowText(hwnd) == entry["window_title"]:
                win32gui.SetForegroundWindow(hwnd)
        
        win32gui.EnumWindows(enum_callback, None)