from config import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialog,
    QPushButton,
    Qt,
)


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("로그 불러오기")
        self.setFixedSize(250, 120)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # 닫기버튼 제거
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.status_label = QLabel("로그 불러오는 중...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.status_label)

        # 선택 항목 코드 출력 라벨 (항상 표시)
        self.code_label = QLabel("")
        self.code_label.setAlignment(Qt.AlignCenter)
        self.code_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        layout.addWidget(self.code_label)

        self.close_btn = QPushButton("닫기")
        self.close_btn.setVisible(False)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

    def set_loading(self, code: str = ""):
        self.status_label.setText("로그 불러오는 중...")
        self.status_label.setStyleSheet("font-size: 14px; color: white;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(False)

    def set_complete(self, code: str = ""):
        self.status_label.setText("로그 불러오기 완료!")
        self.status_label.setStyleSheet("font-size: 14px; color: #4a90d9;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(True)

    def set_not_connected(self, code: str = ""):
        self.status_label.setText("IP 연결이 되어있지 않습니다.")
        self.status_label.setStyleSheet("font-size: 14px; color: red;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(True)