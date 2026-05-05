import os
from datetime import datetime

class FileSaver:

    def __init__(self):
        self.save_path = ""

    def set_save_path(self, path: str):
        self.save_path = path

    def save(self, table_data: list[dict]) -> tuple[bool, str]:
        """
        table_data : [{"tag": ..., "content": ..., "date": ...}, ...]
        반환 : (성공여부, 메시지)
        """
        try:
            if not self.save_path:
                return False, "저장 경로가 설정되지 않았습니다."

            if not table_data:
                return False, "저장할 데이터가 없습니다."

            # 파일명 : log_날짜.txt
            file_name = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
            file_path = os.path.join(self.save_path, file_name)

            # 기존 파일 있으면 마지막 줄 뒤에 이어쓰기 (append)
            mode = "a" if os.path.exists(file_path) else "w"

            with open(file_path, mode, encoding="utf-8") as f:
                # 이어쓰기 시 구분선 추가
                if mode == "a":
                    f.write("\n")

                # 저장 시각 헤더
                f.write(f"=== 저장 시각 : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"{'태그':<12} {'내용':<40} {'날짜'}\n")
                f.write("-" * 70 + "\n")

                for row in table_data:
                    tag     = row.get("tag",     "")
                    content = row.get("content", "")
                    date    = row.get("date",    "")
                    f.write(f"{tag:<12} {content:<40} {date}\n")

            return True, file_path

        except PermissionError:
            return False, "파일 저장 권한이 없습니다."
        except OSError as e:
            return False, f"파일 저장 오류 : {e}"