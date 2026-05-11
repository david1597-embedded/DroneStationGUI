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
        self.list_view    = list_view
        self.ip           = ip
        self.port         = port
        self.tcp_client   = None
        self.is_connected = False
        self.ip_monitor   = None   # IpWidget 에서 주입받음

    # ── IpMonitor 주입 (mid_layout → connect_ip_widget 에서 호출) ─
    def set_ip_monitor(self, monitor):
        self.ip_monitor = monitor

    # ── 목록 버튼 핸들러 ──────────────────────────────────────────
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

    # ── 플래시 로그 읽기 버튼 ─────────────────────────────────────
    def on_flash_read_btn_clicked(self, parent_widget):
        code   = self.get_selected_code()
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

    # ── TCP 송신 ──────────────────────────────────────────────────
    def _send_log_request(self, code: str, dialog: LoadingDialog):
        try:
            if self.tcp_client is not None:
                self.tcp_client.stop()
                self.tcp_client.deleteLater()
                self.tcp_client = None

            # TcpClient 통신 시작 전 IpMonitor busy 설정
            self._set_monitor_busy(True)

            self.tcp_client = TcpClient(ip=self.ip, port=self.port)

            self.tcp_client.data_received.connect(
                lambda packet: self._on_data_received(packet)
            )
            self.tcp_client.receive_done.connect(
                lambda: self._on_receive_done(code, dialog)
            )
            self.tcp_client.receive_failed.connect(
                lambda err: self._on_receive_failed(code, err, dialog)
            )

            self.tcp_client.request_log(code)

        except Exception as e:
            print(f"[ButtonWidget] 송신 오류 : {e}")
            self._set_monitor_busy(False)
            dialog.set_not_connected(code)

    # ── 수신 완료 ─────────────────────────────────────────────────
    def _on_receive_done(self, code: str, dialog: LoadingDialog):
        self._set_monitor_busy(False)
        dialog.set_complete(code)

    # ── 수신 실패 ─────────────────────────────────────────────────
    def _on_receive_failed(self, code: str, err: str, dialog: LoadingDialog):
        self._set_monitor_busy(False)

        # 연결 자체가 끊긴 경우에만 IpMonitor 에 알림
        if "refused" in err or "연결 거부" in err:
            if self.ip_monitor is not None:
                self.ip_monitor.notify_disconnected()
            dialog.set_not_connected(f"{code} | {err}")
        # 타임아웃·데이터 없음은 연결은 유지된 상태
        elif "timed out" in err or "연결 시간 초과" in err:
            dialog.set_no_data(code)
        else:
            dialog.set_no_data(code)
    # ── 수신 데이터 파싱 ──────────────────────────────────────────
    def _on_data_received(self, packet: dict):
        try:
            parsed = LogParser.parse(packet)
            if parsed:
                self.log_received.emit(parsed)
        except Exception as e:
            print(f"[ButtonWidget] 데이터 파싱 오류 : {e}")

    # ── IpMonitor busy 플래그 설정 헬퍼 ──────────────────────────
    def _set_monitor_busy(self, busy: bool):
        if self.ip_monitor is not None:
            self.ip_monitor.set_busy(busy)

    # ── 리스트 뷰 채우기 ──────────────────────────────────────────
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

    def get_selected_code(self) -> str | None:
        selected = self.list_view.currentItem()
        if selected:
            return selected.data(Qt.UserRole)
        return None

    def update_connection(self, connected: bool):
        self.is_connected = connected

    def update_ip(self, ip: str):
        self.ip = ip


