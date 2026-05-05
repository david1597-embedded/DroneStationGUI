from config import (
    QWidget,
    QFileDialog,
    QMessageBox,
)
from logic.file_saver import FileSaver

class BottomWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_saver = FileSaver()

    # ── 저장 경로 선택 ────────────────────────────
    def on_save_path_clicked(self, parent_widget) -> str:
        try:
            path = QFileDialog.getExistingDirectory(
                parent_widget,
                "저장 경로 선택",
                "",
            )
            if path:
                self.file_saver.set_save_path(path)
                return path
            return ""
        except (OSError, RuntimeError) as e:
            print(f"[BottomWidget] 경로 선택 오류 : {e}")
            return ""

    # ── PC에 저장 ─────────────────────────────────
    def on_save_clicked(self, parent_widget, table_data: list):
        try:
            success, message = self.file_saver.save(table_data)
            if success:
                QMessageBox.information(
                    parent_widget,
                    "저장 완료",
                    f"저장되었습니다.\n{message}"
                )
            else:
                QMessageBox.warning(
                    parent_widget,
                    "저장 실패",
                    message
                )
        except (OSError, RuntimeError) as e:
            print(f"[BottomWidget] 저장 오류 : {e}")
            QMessageBox.warning(parent_widget, "저장 오류", str(e))

    # ── 내용 지우기 ───────────────────────────────
    def on_clear_clicked(self, parent_widget, clear_callback):
        try:
            reply = QMessageBox.question(
                parent_widget,
                "내용 지우기",
                "테이블 내용을 모두 지우시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                clear_callback()
        except (RuntimeError, AttributeError) as e:
            print(f"[BottomWidget] 내용 지우기 오류 : {e}")

    # ── 플래시 메모리 지우기 ──────────────────────
    def on_flash_clear_clicked(self, parent_widget):
        try:
            reply = QMessageBox.question(
                parent_widget,
                "플래시 메모리 지우기",
                "플래시 메모리를 지우시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # 추후 TCP/IP 커맨드 포맷 확정 시 구현
                QMessageBox.information(
                    parent_widget,
                    "플래시 메모리 지우기",
                    "추후 구현 예정입니다."
                )
        except (RuntimeError, AttributeError) as e:
            print(f"[BottomWidget] 플래시 메모리 지우기 오류 : {e}")