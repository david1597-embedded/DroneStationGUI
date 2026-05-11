import sys
from config import QApplication, QMainWindow, QWidget, QVBoxLayout
from ui.top_layout import TopLayout
from ui.mid_layout import MidLayout
from ui.bottom_layout import BottomLayout

DARK_STYLE = """
    QMainWindow, QWidget {
        background-color: #4a4a4a;
        color: #1a1a1a;
    }
    QPushButton {
        background-color: #606060;
        color: #1a1a1a;
        border: 1px solid #888;
        border-radius: 4px;
        padding: 6px 12px;
    }
    QPushButton:hover   { background-color: #707070; }
    QPushButton:pressed { background-color: #4a90d9; color: white; }
    QPushButton:checked { background-color: #4a90d9; color: white; }
    QLabel {
        color: #1a1a1a;
        background-color: transparent;
    }
    QListWidget {
        background-color: #606060;
        color: #1a1a1a;
        border: 1px solid #888;
        border-radius: 4px;
    }
    QListWidget::item {
        padding: 4px;
        border-bottom: 1px solid #707070;
    }
    QListWidget::item:selected {
        background-color: #4a90d9;
        color: white;
    }
    QTableWidget {
        background-color: #606060;
        color: #1a1a1a;
        border: 1px solid #888;
        gridline-color: #707070;
    }
    QHeaderView::section {
        background-color: #707070;
        color: #1a1a1a;
        padding: 4px;
        border: none;
        border-right: 1px solid #888;
    }
    QTableWidget::item:selected {
        background-color: #4a90d9;
        color: white;
    }
"""

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)  # 전체 앱에 적용

    window = QMainWindow()
    window.setWindowTitle("DroneStation Log Viewer")
    window.resize(1000, 700)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(6)
    central_widget.setLayout(main_layout)

    top_layout  = TopLayout()
    mid_layout = MidLayout()
    bottom_layout = BottomLayout(mid_layout)
    # top_layout의 ip_widget 시그널 → mid_layout button_widget 업데이트
    mid_layout.connect_ip_widget(top_layout.ip_widget)
    bottom_layout.save_path_changed.connect(top_layout.save_path_label.setText)

    # IP 변경 시 button_widget IP 업데이트
    top_layout.ip_widget.ip_changed.connect(
        mid_layout.button_widget.update_ip
    )


    main_layout.addWidget(top_layout)
    main_layout.addWidget(mid_layout,    1)  # 중단이 가장 많은 공간 차지
    main_layout.addWidget(bottom_layout)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()