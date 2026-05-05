from config import (
    QWidget,
    QLabel,
    pyqtSignal,
)
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from network.ip_monitor import IpMonitor

class IpWidget(QWidget):
    ip_changed     = pyqtSignal(str)   # IP 입력 완료 → top_layout 라벨 업데이트
    status_changed = pyqtSignal(str)  # 연결 상태 → top_layout 상태 라벨 업데이트

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ip         = ""
        self.ip_monitor = None

    # ── IP 주소 입력 버튼 ─────────────────────────
    def on_ip_input_clicked(self):
        ip, ok = QInputDialog.getText(
            self,
            "IP 주소 입력",
            "연결할 IP 주소를 입력하세요\n(예: 192.168.0.10)",
            text=self.ip  # 이전에 입력한 IP 기본값으로 표시
        )
        if ok and ip:
            if self._validate_ip(ip):
                self.ip = ip
                self.ip_changed.emit(ip)  # top_layout 라벨 업데이트
            else:
                QMessageBox.warning(self, "입력 오류", "올바른 IP 주소 형식이 아닙니다.\n(예: 192.168.0.10)")

    def on_connect_clicked(self):
        try:
            if not self.ip:
                QMessageBox.warning(self, "연결 오류", "IP 주소를 먼저 입력해주세요.")
                return

            # 이전 스레드 완전히 종료 후 새로 생성
            if self.ip_monitor is not None:
                self.ip_monitor.stop()
                self.ip_monitor.deleteLater()  # 이전 객체 메모리 해제
                self.ip_monitor = None

            # 매번 새로 생성
            self.ip_monitor = IpMonitor(ip=self.ip)
            self.ip_monitor.status_changed.connect(self._on_status_changed)
            self.ip_monitor.start()
            self.status_changed.emit("connecting")

        except Exception as e:
            print(f"[IpWidget] 연결 시작 오류 : {e}")
            self.status_changed.emit("failed")

    def _on_status_changed(self, connected: bool):
        try:
            if connected:
                self.status_changed.emit("connected")
            else:
                self.status_changed.emit("failed")
        except Exception as e:
            print(f"[IpWidget] 상태 업데이트 오류 : {e}")
    # ── IP 형식 유효성 검사 ───────────────────────
    @staticmethod
    def _validate_ip(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            if not 0 <= int(part) <= 255:
                return False
        return True

    # ── button_widget 연결 상태 업데이트 ─────────
    def get_is_connected(self) -> bool:
        return self.ip_monitor is not None and not self.ip_monitor.isRunning()

