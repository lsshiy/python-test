import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, 
                             QFileDialog, QCheckBox, QGroupBox, QFormLayout, QRadioButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

class MeasuringDemoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OpenCV 測定デモ（検出感度調整付）')
        self.setGeometry(100, 100, 1300, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- コントロールパネル ---
        controls = QVBoxLayout()
        
        # 1. 画像操作
        file_group = QGroupBox("1. 画像操作")
        file_layout = QVBoxLayout()
        self.btn_open = QPushButton('画像を開く')
        self.btn_open.clicked.connect(self.load_image)
        file_layout.addWidget(self.btn_open)
        file_group.setLayout(file_layout)
        controls.addWidget(file_group)

        # 2. 表示モード切替 (背景)
        view_group = QGroupBox("2. 表示モード (背景)")
        view_layout = QVBoxLayout()
        self.rad_ori = QRadioButton("元画像")
        self.rad_pre = QRadioButton("前処理 (Gray/Blur)")
        self.rad_bin = QRadioButton("2値化 (Threshold)")
        self.rad_ori.setChecked(True)
        for rad in [self.rad_ori, self.rad_pre, self.rad_bin]:
            rad.toggled.connect(self.process_image)
            view_layout.addWidget(rad)
        view_group.setLayout(view_layout)
        controls.addWidget(view_group)

        # 3. 検出項目 (表示ON/OFF)
        detect_group = QGroupBox("3. 検出項目")
        detect_layout = QVBoxLayout()
        self.chk_contour = QCheckBox("輪郭・矩形 (緑)")
        self.chk_circle = QCheckBox("円検出 (赤)")
        self.chk_line = QCheckBox("直線検出 (青)")
        self.chk_edge = QCheckBox("エッジ強調 (黄)")
        for chk in [self.chk_contour, self.chk_circle, self.chk_line, self.chk_edge]:
            chk.stateChanged.connect(self.process_image)
            detect_layout.addWidget(chk)
        detect_group.setLayout(detect_layout)
        controls.addWidget(detect_group)

        # 4. 検出感度（尤度ボーダー）の調整
        sensitivity_group = QGroupBox("4. 検出感度 (尤度)")
        sensitivity_layout = QFormLayout()
        
        # 直線検出のしきい値 (HoughLinesP: threshold)
        self.sld_line_val = self.create_slider(10, 200, 50)
        # 円検出のしきい値 (HoughCircles: param2)
        self.sld_circle_val = self.create_slider(10, 100, 30)
        
        sensitivity_layout.addRow("直線尤度:", self.sld_line_val)
        sensitivity_layout.addRow("円尤度:", self.sld_circle_val)
        sensitivity_group.setLayout(sensitivity_layout)
        controls.addWidget(sensitivity_group)

        # 5. 前処理パラメータ
        param_group = QGroupBox("5. 前処理パラメータ")
        param_layout = QFormLayout()
        self.sld_blur = self.create_slider(0, 15, 2)
        self.sld_thresh = self.create_slider(0, 255, 127)
        param_layout.addRow("ぼかし:", self.sld_blur)
        param_layout.addRow("2値化:", self.sld_thresh)
        param_group.setLayout(param_layout)
        controls.addWidget(param_group)

        controls.addStretch()
        main_layout.addLayout(controls, 1)

        # --- 画像表示エリア ---
        self.lbl_image = QLabel('画像を読み込んでください')
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: #222; border-radius: 5px;")
        main_layout.addWidget(self.lbl_image, 4)

    def create_slider(self, min_v, max_v, default):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(default)
        slider.valueChanged.connect(self.process_image)
        return slider

    def load_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, '画像選択', '', 'Images (*.jpg *.png)')
        if fname:
            self.original_image = cv2.imread(fname)
            self.process_image()

    def process_image(self):
        if self.original_image is None: return

        # 基本処理
        h, w = self.original_image.shape[:2]
        scale = 800 / max(w, h)
        img_base = cv2.resize(self.original_image, None, fx=scale, fy=scale)
        gray = cv2.cvtColor(img_base, cv2.COLOR_BGR2GRAY)
        k = self.sld_blur.value() * 2 + 1
        blurred = cv2.GaussianBlur(gray, (k, k), 0)
        _, thresh = cv2.threshold(blurred, self.sld_thresh.value(), 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(blurred, 50, 150)

        # 背景の選択
        if self.rad_ori.isChecked():
            display_img = img_base.copy()
        elif self.rad_pre.isChecked():
            display_img = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
        else:
            display_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        # 1. 直線検出 (青) - 尤度反映
        if self.chk_line.isChecked():
            line_thresh = self.sld_line_val.value()
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=line_thresh, minLineLength=50, maxLineGap=10)
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(display_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # 2. 円検出 (赤) - 尤度反映
        if self.chk_circle.isChecked():
            circle_param2 = self.sld_circle_val.value()
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1.2, 30, param1=100, param2=circle_param2, minRadius=10)
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    cv2.circle(display_img, (i[0], i[1]), i[2], (0, 0, 255), 2)
                    cv2.putText(display_img, f"R:{i[2]}", (i[0]-20, i[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # 3. 輪郭・エッジ（略）
        if self.chk_edge.isChecked():
            display_img[edges > 0] = [0, 255, 255]
        if self.chk_contour.isChecked():
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 500:
                    x, y, wb, hb = cv2.boundingRect(cnt)
                    cv2.rectangle(display_img, (x, y), (x+wb, y+hb), (0, 255, 0), 2)

        # 表示
        display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        h, w, ch = display_img.shape
        q_img = QImage(display_img.data, w, h, w * ch, QImage.Format.Format_RGB888)
        self.lbl_image.setPixmap(QPixmap.fromImage(q_img))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MeasuringDemoApp(); win.show()
    sys.exit(app.exec())