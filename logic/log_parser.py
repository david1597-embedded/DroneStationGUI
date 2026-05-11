from network.protocol import EVENT_CODE_MAP, ERROR_CODE_MAP

class LogParser:

    @staticmethod
    def parse(packet: dict) -> dict | None:
        try:
            event_code = packet["event_code"]
            date       = packet["date"]
            raw_data   = packet["raw_data"]

            # 이벤트 (0x00 ~ 0x0F)
            if event_code in EVENT_CODE_MAP:
                content = LogParser._parse_data(event_code, raw_data, EVENT_CODE_MAP)
                return {
                    "tag"     : "[EVENT]",
                    "content" : content,
                    "date"    : date,
                }

            # 에러 (0x10 ~ 0x1A)
            if event_code in ERROR_CODE_MAP:
                content = LogParser._parse_data(event_code, raw_data, ERROR_CODE_MAP)
                return {
                    "tag"     : "[ERROR]",
                    "content" : content,
                    "date"    : date,
                }

            return {
                "tag"     : "[UNKNOWN]",
                "content" : f"알 수 없는 코드 : {hex(event_code)}",
                "date"    : date,
            }

        except Exception as e:
            print(f"[LogParser] 파싱 오류 : {e}")
            return None

    @staticmethod
    def _parse_data(event_code: int, raw_data: bytes, code_map: dict) -> str:
        base = code_map.get(event_code, "알 수 없음")

        # DATA 없으면 텍스트만 반환
        if not raw_data:
            return base

        # 사용자 커맨드 입력 → ASCII 디코딩
        if event_code == 0x00:
            try:
                cmd = raw_data.decode("ascii").strip("\x00")
                return f"{base} : {cmd}"
            except Exception:
                return base

        # 나머지는 HEX로 표시 (추후 로그별 확정 시 분기 추가)
        hex_str = " ".join(f"0x{b:02X}" for b in raw_data)
        return f"{base} : {hex_str}"