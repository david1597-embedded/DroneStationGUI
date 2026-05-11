from config import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    pyqtSignal,
)
from widgets import BottomWidget

class BottomLayout(QWidget):
    save_path_changed = pyqtSignal(str)  # 저장 경로 변경 → top_layout 라벨 업데이트

    def __init__(self, mid_layout, parent=None):
        super().__init__(parent)
        self.mid_layout    = mid_layout   # mid_layout 참조
        self.bottom_widget = BottomWidget()
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(8)
        self.setLayout(main_layout)

        self.save_path_btn   = QPushButton("🗁  저장 경로 선택")
        self.save_btn        = QPushButton("💾  PC에 저장")
        self.clear_btn       = QPushButton("🗑  내용 지우기")
        self.flash_clear_btn = QPushButton("⚠  플래시 메모리 지우기")

        normal_style = """
            QPushButton {
                background-color: #606060;
                color: #1a1a1a;
                border: 1px solid #888;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover   { background-color: #707070; }
            QPushButton:pressed { background-color: #4a90d9; color: white; }
        """
        danger_style = """
            QPushButton {
                background-color: #606060;
                border: 1px solid #e08080;
                border-radius: 4px;
                padding: 6px 12px;
                color: red;
            }
            QPushButton:hover   { background-color: #707070; }
            QPushButton:pressed { background-color: #cc0000; color: white; }
        """

        self.save_path_btn.setStyleSheet(normal_style)
        self.save_btn.setStyleSheet(normal_style)
        self.clear_btn.setStyleSheet(danger_style)
        self.flash_clear_btn.setStyleSheet(danger_style)

        main_layout.addWidget(self.save_path_btn)
        main_layout.addWidget(self.save_btn)
        main_layout.addWidget(self.clear_btn)
        main_layout.addWidget(self.flash_clear_btn)

    def _connect_signals(self):
        self.save_path_btn.clicked.connect(self._on_save_path_clicked)
        self.save_btn.clicked.connect(self._on_save_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.flash_clear_btn.clicked.connect(self._on_flash_clear_clicked)

    # ── 슬롯 ─────────────────────────────────────
    def _on_save_path_clicked(self):
        path = self.bottom_widget.on_save_path_clicked(self)
        if path:
            self.save_path_changed.emit(path)

    def _on_save_clicked(self):
        self.bottom_widget.on_save_clicked(
            self,
            self.mid_layout.get_table_data()
        )

    def _on_clear_clicked(self):
        self.bottom_widget.on_clear_clicked(
            self,
            self.mid_layout.clear_output
        )

    def _on_flash_clear_clicked(self):
        self.bottom_widget.on_flash_clear_clicked(self)