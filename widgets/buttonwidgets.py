from PyQt5.QtCore import pyqtSignal

from config import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    Qt,
)
from network.tcp_client import TcpClient
from logic.log_parser import LogParser
from widgets.loading_dialog import LoadingDialog

# ── 각 버튼별 데이터 정의 (텍스트, 전송코드) ─────
EVENT_ITEMS = [
    ("사용자 커맨드 입력 이벤트",  "[LOG000]"),
    ("DOOR OPEN 이벤트",          "[LOG001]"),
    ("DOOR CLOSE 이벤트",         "[LOG002]"),
    ("LIFT UP 이벤트",            "[LOG003]"),
    ("LIFT DOWN 이벤트",          "[LOG004]"),
    ("스테이션 초기화 이벤트",     "[LOG005]"),
    ("무선 통신 송신 이벤트",      "[LOG006]"),
    ("무선 통신 수신 이벤트",      "[LOG007]"),
    ("충전 시작 이벤트",           "[LOG008]"),
    ("충전 정지 이벤트",           "[LOG009]"),
    ("드론 이륙 이벤트",           "[LOG00A]"),
    ("드론 착륙 이벤트",           "[LOG00B]"),
    ("출격 가능 판단 이벤트",      "[LOG00C]"),
    ("에어컨 시작 이벤트",         "[LOG00D]"),
    ("히터 시작 이벤트",           "[LOG00E]"),
    ("냉 난방기 정지 이벤트",      "[LOG00F]"),
]

ERROR_ITEMS = [
    ("온도 관련 에러",             "[LOG100]"),
    ("모션 센서 비정상 에러",      "[LOG101]"),
    ("냉 난방기 지속 시간 에러",   "[LOG102]"),
    ("강수량 에러",                "[LOG103]"),
    ("풍속량 에러",                "[LOG104]"),
    ("출격 준비 에러",             "[LOG105]"),
    ("배터리 충전 속도 이상 에러", "[LOG106]"),
    ("rssi 기준치 이하 에러",      "[LOG107]"),
    ("저전압 이상 에러",           "[LOG108]"),
    ("패킷 수신 실패 에러",        "[LOG109]"),
    ("초기화 비정상 에러",         "[LOG10A]"),
]

MOTION_ITEMS = [
    ("DOOR OPEN",  "[LOG200]"),
    ("DOOR CLOSE", "[LOG201]"),
    ("LIFT UP",    "[LOG203]"),
    ("LIFT DOWN",  "[LOG204]"),
]

SAVE_COUNT_ITEMS = [
    ("에러",   "[LOG300]"),
    ("이벤트", "[LOG301]"),
]

ALL_ITEMS = [
    ("에러",   "[LOG400]"),
    ("이벤트", "[LOG401]"),
]

class ButtonWidget(QWidget):
    log_received = pyqtSignal(dict)

    def __init__(self, list_view: QListWidget, ip: str = "", port: int = 5000, parent=None):
        super().__init__(parent)
        self.list_view = list_view
        self.ip        = ip
        self.port      = port
        self.tcp_client = None
        self.is_connected = False

    def on_event_clicked(self):
        self._populate_list(EVENT_ITEMS)

    def on_error_clicked(self):
        self._populate_list(ERROR_ITEMS)

    def on_motion_clicked(self):
        self._populate_list(MOTION_ITEMS)

    def on_save_count_clicked(self):
        self._populate_list(SAVE_COUNT_ITEMS)

    def on_all_clicked(self):
        self._populate_list(ALL_ITEMS)

    #Flash Log Button
    def on_flash_read_btn_clicked(self, parent_widget):
        code = self.get_selected_code()
        dialog = LoadingDialog(parent_widget)

        if not self.is_connected:
            dialog.set_not_connected(code if code else "선택된 항목 없음")
            dialog.show()
            return

        if code is None:
            dialog.set_not_connected("선택된 항목 없음")
            dialog.show()
            return

        dialog.set_loading(code)
        dialog.show()
        self._send_log_request(code, dialog)

    # ── ListView 채우기 ───────────────────────────
    def _populate_list(self, items: list):
        self.list_view.clear()
        for text, code in items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, code)
            self.list_view.addItem(item)

        self.list_view.setStyleSheet("""
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #888;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
        """)

    def get_selected_code(self) -> str | None :
        selected = self.list_view.currentItem()
        if selected:
            return selected.data(Qt.UserRole)  # ex) "[LOG000]"
        return None

    def update_connection(self, connected: bool):
        self.is_connected = connected

    # ── IP 업데이트 ───────────────────────────────
    def update_ip(self, ip: str):
        self.ip = ip
    # ── TCP 송신 ──────────────────────────────────
    def _send_log_request(self, code: str, dialog: LoadingDialog):
        try:
            if self.tcp_client is not None:
                self.tcp_client.stop()
                self.tcp_client.deleteLater()
                self.tcp_client = None

            self.tcp_client = TcpClient(ip=self.ip, port=self.port)

            self.tcp_client.data_received.connect(
                lambda packet: self._on_data_received(packet, dialog)
            )
            self.tcp_client.receive_done.connect(
                lambda: dialog.set_complete(code)
            )
            self.tcp_client.receive_failed.connect(
                lambda err: dialog.set_not_connected(f"{code} | {err}")
            )

            self.tcp_client.request_log(code)

        except Exception as e:
            print(f"[ButtonWidget] 송신 오류 : {e}")
            dialog.set_not_connected(code)

    # ── 수신 데이터 파싱 ──────────────────────────
    def _on_data_received(self, packet: dict, dialog):
        try:
            parsed = LogParser.parse(packet)
            if parsed:
                self.log_received.emit(parsed)
        except Exception as e:
            print(f"[ButtonWidget] 데이터 파싱 오류 : {e}")


