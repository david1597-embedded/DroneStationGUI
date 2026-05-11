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
        self.setFixedSize(320, 130)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)  # 닫기버튼 제거
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.status_label = QLabel("로그 불러오는 중...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.status_label)

        self.code_label = QLabel("")
        self.code_label.setAlignment(Qt.AlignCenter)
        self.code_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        self.code_label.setWordWrap(True)
        layout.addWidget(self.code_label)

        self.close_btn = QPushButton("닫기")
        self.close_btn.setVisible(False)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

    def set_loading(self, code: str = ""):
        """전송 시작 시"""
        self.status_label.setText("로그 불러오는 중...")
        self.status_label.setStyleSheet("font-size: 14px; color: white;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(False)

    def set_complete(self, code: str = ""):
        """수신 완료 시"""
        self.status_label.setText("로그 불러오기 완료!")
        self.status_label.setStyleSheet("font-size: 14px; color: #4a90d9;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(True)

    def set_not_connected(self, code: str = ""):
        """IP 연결 안 된 상태에서 시도 시"""
        self.status_label.setText("IP 연결이 되어있지 않습니다.")
        self.status_label.setStyleSheet("font-size: 14px; color: red;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(True)

    def set_no_data(self, code: str = ""):
        """연결은 됐지만 수신 데이터 없을 시"""
        self.status_label.setText("수신된 데이터가 없습니다.")
        self.status_label.setStyleSheet("font-size: 14px; color: orange;")
        self.code_label.setText(f"FLASH LOG CODE : {code}")
        self.close_btn.setVisible(True)