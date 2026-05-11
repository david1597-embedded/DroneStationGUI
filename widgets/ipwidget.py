from config import (
    QWidget,
    QLabel,
    pyqtSignal,
)
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from network.ip_monitor import IpMonitor


class IpWidget(QWidget):
    ip_changed     = pyqtSignal(str)   # IP 입력 완료 → top_layout 라벨 업데이트
    status_changed = pyqtSignal(str)   # 연결 상태 → top_layout 상태 라벨 업데이트

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
            text=self.ip
        )
        if ok and ip:
            if self._validate_ip(ip):
                self.ip = ip
                self.ip_changed.emit(ip)
            else:
                QMessageBox.warning(self, "입력 오류", "올바른 IP 주소 형식이 아닙니다.\n(예: 192.168.0.10)")

    def on_connect_clicked(self):
        try:
            if not self.ip:
                QMessageBox.warning(self, "연결 오류", "IP 주소를 먼저 입력해주세요.")
                return

            if self.ip_monitor is not None:
                self.ip_monitor.stop()
                self.ip_monitor.deleteLater()
                self.ip_monitor = None

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

    def get_is_connected(self) -> bool:
        return self.ip_monitor is not None and self.ip_monitor.isRunning()

    def get_monitor(self) -> IpMonitor | None:
        """ButtonWidget 이 busy 플래그를 설정할 수 있도록 monitor 반환"""
        return self.ip_monitor

