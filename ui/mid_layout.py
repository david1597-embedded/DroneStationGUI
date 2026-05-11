from config import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    Qt,
    QTableWidget,
    QTableWidgetItem,
    QButtonGroup,
    QHeaderView,
    QListWidget
)

from widgets import ButtonWidget

class MidLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)
        self.setLayout(main_layout)

        # ── 맨 좌측 : 버튼 4개 ───────────────────────
        btn_style = """
            QPushButton {
                background-color: #e8e8e8;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                text-align: center;
            }
            QPushButton:hover   { background-color: #d0d0d0; }
            QPushButton:pressed { background-color: #4a90d9; color: white; }
            QPushButton:checked { background-color: #4a90d9; color: white; }
        """
        btn_layout = QVBoxLayout()

        self.btn1 = QPushButton("이벤트")
        self.btn2 = QPushButton("에러")
        self.btn3 = QPushButton("모션 횟수")
        self.btn4 = QPushButton("로그 저장가능 횟수")
        self.btn5 = QPushButton("전체 코드")
        self.btn_group = QButtonGroup()
        self.btn_group.setExclusive(True)
        for btn in [self.btn1, self.btn2, self.btn3, self.btn4, self.btn5]:
            btn.setStyleSheet(btn_style)
            btn.setCheckable(True)
            self.btn_group.addButton(btn)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ── 좌측 두번째 : ListView ────────────────────
        list_layout = QVBoxLayout()

        list_title = QLabel("항목 선택")
        list_title.setStyleSheet("font-weight: bold;")
        list_layout.addWidget(list_title)

        self.list_view = QListWidget()
        self.list_view.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
        """)
        list_layout.addWidget(self.list_view)
        main_layout.addLayout(list_layout, 1)

        # ── 우측 두번째 : 플래시 버튼 ────────────────
        flash_layout = QVBoxLayout()

        self.flash_btn = QPushButton("플래시 메모리\n로그 불러오기")
        self.flash_btn.setStyleSheet("""
            QPushButton {
                background-color: #e8e8e8;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover   { background-color: #d0d0d0; }
            QPushButton:pressed { background-color: #4a90d9; color: white; }
        """)
        flash_layout.addWidget(self.flash_btn)
        flash_layout.addStretch()
        main_layout.addLayout(flash_layout)

        # ── 맨 우측 : 테이블 출력 ─────────────────────
        output_layout = QVBoxLayout()

        self.output_table = QTableWidget()
        self.output_table.setColumnCount(3)
        self.output_table.setHorizontalHeaderLabels(["태그", "내용", "날짜"])
        self.output_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.output_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.output_table.verticalHeader().setVisible(False)
        self.output_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: white;
                padding: 4px;
                border: none;
                border-right: 1px solid #555;
            }
            QTableWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
        """)

        header = self.output_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setStretchLastSection(True)

        output_layout.addWidget(self.output_table)
        main_layout.addLayout(output_layout, 2)

        # ── ButtonWidget 생성 ─────────────────────────
        self.button_widget = ButtonWidget(self.list_view)

        # ── 버튼 클릭 → ButtonWidget 함수 연결 ────────
        self.btn1.clicked.connect(self.button_widget.on_event_clicked)
        self.btn2.clicked.connect(self.button_widget.on_error_clicked)
        self.btn3.clicked.connect(self.button_widget.on_motion_clicked)
        self.btn4.clicked.connect(self.button_widget.on_save_count_clicked)
        self.btn5.clicked.connect(self.button_widget.on_all_clicked)
        self.flash_btn.clicked.connect(
            lambda: self.button_widget.on_flash_read_btn_clicked(self)
        )

        # ── 로그 수신 → 테이블 출력 ───────────────────
        self.button_widget.log_received.connect(self._on_log_received)

    def connect_ip_widget(self, ip_widget):
        """
        TopLayout 생성 후 외부(main.py)에서 한 번만 호출.
        IpWidget 의 시그널을 ButtonWidget 에 연결합니다.
        """
        # 연결 상태 변경 → button_widget.is_connected 갱신
        ip_widget.status_changed.connect(self._on_status_changed)
        # IP 변경 → button_widget.ip 갱신
        ip_widget.ip_changed.connect(self.button_widget.update_ip)

    def _on_status_changed(self, status: str):
        """IpWidget 상태를 ButtonWidget 의 is_connected 에 반영"""
        if status == "connected":
            self.button_widget.update_connection(True)
        elif status in ("failed", "connecting"):
            self.button_widget.update_connection(False)

    def _on_log_received(self, parsed: dict):
        self.add_log_row(
            tag=parsed["tag"],
            content=parsed["content"],
            date=parsed["date"],
        )

    def add_log_row(self, tag: str, content: str, date: str):
        row = self.output_table.rowCount()
        self.output_table.insertRow(row)
        self.output_table.setItem(row, 0, QTableWidgetItem(tag))
        self.output_table.setItem(row, 1, QTableWidgetItem(content))
        self.output_table.setItem(row, 2, QTableWidgetItem(date))

    def clear_output(self):
        try:
            self.output_table.setRowCount(0)
        except (RuntimeError, AttributeError) as e:
            print(f"[MidLayout] 테이블 초기화 오류 : {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        total = self.output_table.width()
        self.output_table.setColumnWidth(0, int(total * 0.1))
        self.output_table.setColumnWidth(1, int(total * 0.6))
        self.output_table.setColumnWidth(2, int(total * 0.3))

    def get_table_data(self) -> list:
        data = []
        for row in range(self.output_table.rowCount()):
            try:
                tag_item     = self.output_table.item(row, 0)
                content_item = self.output_table.item(row, 1)
                date_item    = self.output_table.item(row, 2)
                data.append({
                    "tag":     tag_item.text()     if tag_item     else "",
                    "content": content_item.text() if content_item else "",
                    "date":    date_item.text()    if date_item    else "",
                })
            except (AttributeError, RuntimeError) as e:
                print(f"[MidLayout] 테이블 데이터 읽기 오류 : {e}")
                continue
        return data