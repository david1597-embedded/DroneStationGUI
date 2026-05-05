from config import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    Qt
)
from widgets.ipwidget import IpWidget
class TopLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ip_widget = IpWidget()
        self.ip_widget.ip_changed.connect(self._on_ip_changed)
        self.ip_widget.status_changed.connect(self._on_status_changed)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
        """)

        # ── 좌측 : IP 상태 영역 ──────────────────────
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_widget.setLayout(left_layout)

        ip_title = QLabel("IP 연결 상태")
        ip_title.setStyleSheet("font-weight: bold; border: none;")
        left_layout.addWidget(ip_title)

        self.ip_address_label = QLabel("IP: 미설정")
        self.ip_address_label.setStyleSheet("border: none;")
        left_layout.addWidget(self.ip_address_label)

        self.ip_status_label = QLabel("● 연결 안됨")
        self.ip_status_label.setStyleSheet("color: red; border: none;")
        left_layout.addWidget(self.ip_status_label)

        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("연결 시작")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                border: none;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:pressed { background-color: #2a6099; }
        """)
        self.ip_input_btn = QPushButton("IP 주소 입력")
        self.ip_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                border: none;
            }
            QPushButton:hover { background-color: #357abd; }
            QPushButton:pressed { background-color: #2a6099; }
        """)
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.ip_input_btn)
        left_layout.addLayout(btn_layout)

        main_layout.addWidget(left_widget)
        self.connect_btn.clicked.connect(self.ip_widget.on_connect_clicked)
        self.ip_input_btn.clicked.connect(self.ip_widget.on_ip_input_clicked)
        # ── 중앙 : 타이틀 라벨 ───────────────────────
        self.center_label = QLabel("DRONE STATION LOG VIEWER")
        self.center_label.setAlignment(Qt.AlignCenter)
        self.center_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: 1px dashed #aaa;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
        """)
        main_layout.addWidget(self.center_label)

        # ── 우측 : 저장 경로 ──────────────────────────
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_widget.setLayout(right_layout)

        save_title = QLabel("저장 경로")
        save_title.setStyleSheet("font-weight: bold; border: none;")
        right_layout.addWidget(save_title)

        self.save_path_label = QLabel("경로가 설정되어 있지 않습니다.")
        self.save_path_label.setStyleSheet("color: #4a90d9; border: none;")
        right_layout.addWidget(self.save_path_label)

        main_layout.addWidget(right_widget)

        # ── IP 입력 완료 시 라벨 업데이트 ────────────

    def _on_ip_changed(self, ip: str):
        self.ip_address_label.setText(f"IP : {ip}")

        # ── 연결 상태 업데이트 ────────────────────────

    def _on_status_changed(self, status: str):
        if status == "connecting":
            self.ip_status_label.setText("● 연결 시도 중...")
            self.ip_status_label.setStyleSheet("color: orange;")
        elif status == "connected":
            self.ip_status_label.setText("● 연결됨")
            self.ip_status_label.setStyleSheet("color: #4a90d9;")
        elif status == "failed":
            self.ip_status_label.setText("● 연결 실패")
            self.ip_status_label.setStyleSheet("color: red;")