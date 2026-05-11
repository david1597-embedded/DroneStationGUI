from PyQt5.QtWidgets import QLineEdit

from config import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialog,
    QPushButton,
    QDialogButtonBox,
    Qt,
)

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IP 연결 설정")

        layout = QVBoxLayout()

        self.ip_input = QLineEdit(self)
        # IP 입력 필드
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("예: 127.0.0.1")
        layout.addWidget(QLabel("IP 주소:"))
        layout.addWidget(self.ip_input)

        # 포트 입력 필드
        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("예: 8080")
        layout.addWidget(QLabel("포트 번호:"))
        layout.addWidget(self.port_input)

        # 확인/취소 버튼 (QDialogButtonBox 사용 시 표준 버튼 배치가 적용됨)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)  # 확인 누르면 accept() 호출
        buttons.rejected.connect(self.reject)  # 취소 누르면 reject() 호출
        layout.addWidget(buttons)

    def get_inputs(self):
        return self.ip_input.text(), self.port_input.text()
