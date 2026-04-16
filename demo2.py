import sys
import cv2
import numpy as np
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, 
                             QFileDialog, QCheckBox, QGroupBox, QFormLayout, 
                             QRadioButton, QTextEdit, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

# --- 幾何計算ユーティリティ ---
def get_dist_point_to_line(px, py, l):
    x1, y1, x2, y2 = l
    line_vec = np.array([x2 - x1, y2 - y1])
    p_vec = np.array([px - x1, py - y1])
    line_len_sq = np.dot(line_vec, line_vec)
    if line_len_sq == 0: return np.linalg.norm(p_vec)
    t = max(0, min(1, np.dot(p_vec, line_vec) / line_len_sq))
    projection = line_vec * t
    return np.linalg.norm(p_vec - projection)

def get_angle_between_lines(l1, l2):
    v1 = (l1[2]-l1[0], l1[3]-l1[1])
    v2 = (l2[2]-l2[0], l2[3]-l2[1])
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 * mag2 == 0: return 0
    cos_theta = dot / (mag1 * mag2)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_theta))))

# --- クリックイベント対応ラベル ---
class ClickableLabel(QLabel):
    clicked = pyqtSignal(int, int)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(int(event.position().x()), int(event.position().y()))

class UltimateMeasureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.selected_items = [] 
        self.detected_lines = []
        self.detected_circles = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OpenCV 統合測定プラットフォーム v2.1')
        self.setGeometry(100, 100, 1450, 950)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- 左側：コントロールパネル ---
        sidebar = QVBoxLayout()
        
        # 1. 画像操作
        g1 = QGroupBox("1. 画像操作")
        l1 = QVBoxLayout(); btn = QPushButton("画像を開く"); btn.clicked.connect(self.load_image)
        l1.addWidget(btn); g1.setLayout(l1); sidebar.addWidget(g1)

        # 2. 表示背景切り替え
        g2 = QGroupBox("2. 表示背景")
        l2 = QVBoxLayout()
        self.rad_ori = QRadioButton("元画像"); self.rad_pre = QRadioButton("前処理"); self.rad_bin = QRadioButton("2値化")
        self.rad_ori.setChecked(True)
        for r in [self.rad_ori, self.rad_pre, self.rad_bin]: r.toggled.connect(self.update_display); l2.addWidget(r)
        g2.setLayout(l2); sidebar.addWidget(g2)

        # 3. 検出・オーバーレイ
        g3 = QGroupBox("3. 検出トグル")
        l3 = QVBoxLayout()
        self.chk_line = QCheckBox("直線 (青)"); self.chk_circle = QCheckBox("円 (赤)")
        self.chk_contour = QCheckBox("輪郭 (緑)"); self.chk_edge = QCheckBox("エッジ (黄)")
        for c in [self.chk_line, self.chk_circle, self.chk_contour, self.chk_edge]: 
            c.stateChanged.connect(self.update_display); l3.addWidget(c)
        g3.setLayout(l3); sidebar.addWidget(g3)

        # 4. パラメータ (数値入力ボックス付き同期スライダー)
        g4 = QGroupBox("4. パラメータ調整")
        l4 = QFormLayout()
        
        # ぼかし (0-31)
        self.sld_blur, self.spn_blur = self.create_sync_widgets(0, 15, 2, 31)
        # 2値化 (0-255)
        self.sld_thresh, self.spn_thresh = self.create_sync_widgets(0, 255, 127, 255)
        # 直線尤度 (10-500)
        self.sld_l_line, self.spn_l_line = self.create_sync_widgets(10, 200, 50, 1000)
        # 円尤度 (10-200)
        self.sld_l_circle, self.spn_l_circle = self.create_sync_widgets(10, 100, 30, 500)
        
        l4.addRow("ぼかし:", self.wrap_layout(self.sld_blur, self.spn_blur))
        l4.addRow("2値化:", self.wrap_layout(self.sld_thresh, self.spn_thresh))
        l4.addRow("直線尤度:", self.wrap_layout(self.sld_l_line, self.spn_l_line))
        l4.addRow("円尤度:", self.wrap_layout(self.sld_l_circle, self.spn_l_circle))
        
        g4.setLayout(l4); sidebar.addWidget(g4)

        # 5. 測定結果
        g5 = QGroupBox("5. 測定結果")
        l5 = QVBoxLayout()
        self.txt_res = QTextEdit(); self.txt_res.setReadOnly(True); l5.addWidget(self.txt_res)
        btn_clr = QPushButton("選択解除"); btn_clr.clicked.connect(self.clear_selection); l5.addWidget(btn_clr)
        g5.setLayout(l5); sidebar.addWidget(g5)

        sidebar.addStretch()
        main_layout.addLayout(sidebar, 1)

        # --- 右側：メイン画像表示 ---
        self.lbl_img = ClickableLabel("画像を開いてください。")
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img.setStyleSheet("background-color: #1e1e1e; color: #888;")
        self.lbl_img.clicked.connect(self.handle_click)
        main_layout.addWidget(self.lbl_img, 4)

    def create_sync_widgets(self, min_v, max_v, def_v, spin_max):
        """スライダーとスピンボックスを作成し同期させる"""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(def_v)
        
        spin = QSpinBox()
        spin.setRange(min_v, spin_max)
        spin.setValue(def_v)
        spin.setFixedWidth(60)
        
        # 同期設定
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        # どちらが変わっても再処理
        slider.valueChanged.connect(self.process_logic)
        spin.valueChanged.connect(self.process_logic)
        
        return slider, spin

    def wrap_layout(self, w1, w2):
        """ウィジェットを横並びのレイアウトにラップする"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(w1)
        layout.addWidget(w2)
        return container

    def load_image(self):
        f, _ = QFileDialog.getOpenFileName(self, "画像選択", "", "Images (*.jpg *.png)")
        if f:
            # 日本語パス対応の読み込み
            n = np.fromfile(f, np.uint8)
            self.original_image = cv2.imdecode(n, cv2.IMREAD_COLOR)
            
            if self.original_image is not None:
                self.process_logic() # 先に処理して self.base を作る
                self.clear_selection()

    def clear_selection(self):
        self.selected_items = []; self.txt_res.clear(); self.update_display()

    def process_logic(self):
        if self.original_image is None: return
        
        # 表示倍率計算
        h, w = self.original_image.shape[:2]
        self.sc = 850 / max(w, h)
        self.base = cv2.resize(self.original_image, None, fx=self.sc, fy=self.sc)
        
        self.gray = cv2.cvtColor(self.base, cv2.COLOR_BGR2GRAY)
        # ぼかし (スピンボックスの値をそのまま使用)
        k = self.spn_blur.value() * 2 + 1
        self.blur = cv2.GaussianBlur(self.gray, (k, k), 0)
        
        # 2値化
        _, self.thresh = cv2.threshold(self.blur, self.spn_thresh.value(), 255, cv2.THRESH_BINARY)
        self.edges = cv2.Canny(self.blur, 50, 150)

        # 直線検出 (データ保持)
        self.detected_lines = []
        ls = cv2.HoughLinesP(self.edges, 1, np.pi/180, self.spn_l_line.value(), 50, 10)
        if ls is not None: self.detected_lines = [l[0] for l in ls]

        # 円検出 (データ保持)
        self.detected_circles = []
        # 大量検出を防ぐため minDist を少し広めに設定
        cs = cv2.HoughCircles(self.blur, cv2.HOUGH_GRADIENT, 1.2, 80, 100, self.spn_l_circle.value(), 10, 250)
        if cs is not None: self.detected_circles = cs[0]
        
        self.update_display()

    def update_display(self):
        # Attribute内存在チェック (クラッシュ回避)
        if self.original_image is None or not hasattr(self, 'base'): 
            return

        # 背景選択
        if self.rad_ori.isChecked(): out = self.base.copy()
        elif self.rad_pre.isChecked(): out = cv2.cvtColor(self.blur, cv2.COLOR_GRAY2BGR)
        else: out = cv2.cvtColor(self.thresh, cv2.COLOR_GRAY2BGR)

        # オーバーレイ描画
        if self.chk_edge.isChecked(): out[self.edges > 0] = [0, 255, 255]
        if self.chk_line.isChecked():
            for l in self.detected_lines: cv2.line(out, (l[0], l[1]), (l[2], l[3]), (255, 100, 0), 1)
        if self.chk_circle.isChecked():
            for c in self.detected_circles: cv2.circle(out, (int(c[0]), int(c[1])), int(c[2]), (100, 100, 255), 1)
        if self.chk_contour.isChecked():
            cnts, _ = cv2.findContours(self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in cnts:
                if cv2.contourArea(cnt) > 500:
                    x, y, wb, hb = cv2.boundingRect(cnt); cv2.rectangle(out, (x, y), (x+wb, y+hb), (0, 255, 0), 1)

        # 選択図形の強調
        for it in self.selected_items:
            if len(it) == 4: cv2.line(out, (it[0], it[1]), (it[2], it[3]), (255, 255, 0), 3)
            else: cv2.circle(out, (int(it[0]), int(it[1])), int(it[2]), (255, 0, 255), 3)

        # 表示更新
        rgb = cv2.cvtColor(out, cv2.COLOR_BGR2RGB); h, w, ch = rgb.shape
        self.lbl_img.setPixmap(QPixmap.fromImage(QImage(rgb.data, w, h, w*ch, QImage.Format.Format_RGB888)))

    def handle_click(self, x, y):
        target = None
        # 円のヒット判定
        for c in self.detected_circles:
            if abs(math.sqrt((x-c[0])**2 + (y-c[1])**2) - c[2]) < 10: target = c; break
        # 直線のヒット判定
        if target is None:
            for l in self.detected_lines:
                if get_dist_point_to_line(x, y, l) < 10: target = l; break
        
        if target is not None:
            if len(self.selected_items) >= 2: self.selected_items.pop(0)
            self.selected_items.append(target); self.calculate_all(); self.update_display()

    def calculate_all(self):
        self.txt_res.clear()
        if not self.selected_items: return
        
        it1 = self.selected_items[0]
        self.txt_res.append("【選択1】" + ("円" if len(it1)==3 else "直線"))
        if len(it1)==3: self.txt_res.append(f" 直径: {it1[2]*2:.1f} px")
        else: self.txt_res.append(f" 長さ: {math.sqrt((it1[2]-it1[0])**2 + (it1[3]-it1[1])**2):.1f} px")
        
        if len(self.selected_items) < 2: return
        it2 = self.selected_items[1]
        self.txt_res.append("\n【選択2】" + ("円" if len(it2)==3 else "直線"))
        
        # 複合計算
        if len(it1)==4 and len(it2)==4: # 線 vs 線
            self.txt_res.append(f"\n★解析結果\n 角度: {get_angle_between_lines(it1, it2):.1f} °")
        elif len(it1)==3 and len(it2)==3: # 円 vs 円
            d = math.sqrt((it1[0]-it2[0])**2 + (it1[1]-it2[1])**2)
            self.txt_res.append(f"\n★解析結果\n 中心距離: {d:.1f} px\n 最短距離: {max(0, d-it1[2]-it2[2]):.1f} px")
        else: # 線 vs 円
            l = it1 if len(it1)==4 else it2; c = it2 if len(it1)==4 else it1
            d = get_dist_point_to_line(c[0], c[1], l)
            self.txt_res.append(f"\n★解析結果\n 中心-線距離: {d:.1f} px\n 表面-線距離: {max(0, d-c[2]):.1f} px")

if __name__ == '__main__':
    app = QApplication(sys.argv); win = UltimateMeasureApp(); win.show(); sys.exit(app.exec())