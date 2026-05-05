# ── 헤더 코드 ─────────────────────────────────────
HEADER_CODE = 0x4A  # 'J'

# ── 이벤트 코드 맵 ────────────────────────────────
EVENT_CODE_MAP = {
    0x00: "사용자 커맨드 입력 이벤트",
    0x01: "DOOR OPEN 이벤트",
    0x02: "DOOR CLOSE 이벤트",
    0x03: "LIFT UP 이벤트",
    0x04: "LIFT DOWN 이벤트",
    0x05: "스테이션 초기화 이벤트",
    0x06: "무선 통신 송신 이벤트",
    0x07: "무선 통신 수신 이벤트",
    0x08: "충전 시작 이벤트",
    0x09: "충전 정지 이벤트",
    0x0A: "드론 이륙 이벤트",
    0x0B: "드론 착륙 이벤트",
    0x0C: "출격 가능 판단 이벤트",
    0x0D: "에어컨 시작 이벤트",
    0x0E: "히터 시작 이벤트",
    0x0F: "냉 난방기 정지 이벤트",
}

# ── 에러 코드 맵 (0x10~) ──────────────────────────
ERROR_CODE_MAP = {
    0x10: "온도 관련 에러",
    0x11: "모션 센서 비정상 에러",
    0x12: "냉 난방기 지속 시간 에러",
    0x13: "강수량 에러",
    0x14: "풍속량 에러",
    0x15: "출격 준비 에러",
    0x16: "배터리 충전 속도 이상 에러",
    0x17: "rssi 기준치 이하 에러",
    0x18: "저전압 이상 에러",
    0x19: "패킷 수신 실패 에러",
    0x1A: "초기화 비정상 에러",
}

# ── 로그코드별 DATA 크기 (바이트) ─────────────────
# 0 → DATA 없음 (날짜가 [2]부터 시작)
# n → DATA n바이트 (날짜가 [2+n]부터 시작)
LOG_DATA_SIZE = {
    # 이벤트
    0x00: 6,  # 사용자 커맨드 입력 → ASCII 6바이트
    0x01: 0,  # DOOR OPEN
    0x02: 0,  # DOOR CLOSE
    0x03: 0,  # LIFT UP
    0x04: 0,  # LIFT DOWN
    0x05: 0,  # 스테이션 초기화
    0x06: 0,  # 무선 통신 송신
    0x07: 0,  # 무선 통신 수신
    0x08: 0,  # 충전 시작
    0x09: 0,  # 충전 정지
    0x0A: 0,  # 드론 이륙
    0x0B: 0,  # 드론 착륙
    0x0C: 0,  # 출격 가능 판단
    0x0D: 0,  # 에어컨 시작
    0x0E: 0,  # 히터 시작
    0x0F: 0,  # 냉 난방기 정지
    # 에러
    0x10: 0,  # 온도 관련 에러
    0x11: 0,  # 모션 센서 비정상 에러
    0x12: 0,  # 냉 난방기 지속 시간 에러
    0x13: 0,  # 강수량 에러
    0x14: 0,  # 풍속량 에러
    0x15: 0,  # 출격 준비 에러
    0x16: 0,  # 배터리 충전 속도 이상
    0x17: 0,  # rssi 기준치 이하
    0x18: 0,  # 저전압 이상
    0x19: 0,  # 패킷 수신 실패
    0x1A: 0,  # 초기화 비정상
}

class Protocol:
    PACKET_SIZE = 16

    @staticmethod
    def parse_packet(data: bytes) -> dict | None:
        try:
            if len(data) != Protocol.PACKET_SIZE:
                print(f"[Protocol] 패킷 크기 오류 : {len(data)} bytes")
                return None

            header     = data[0]
            event_code = data[1]

            # 헤더 확인
            if header != HEADER_CODE:
                print(f"[Protocol] 헤더 오류 : {hex(header)}")
                return None

            # CRC 검증
            if not Protocol._verify_crc(data):
                print("[Protocol] CRC 오류")
                return None

            # DATA 크기에 따라 날짜 시작 위치 결정
            data_size  = LOG_DATA_SIZE.get(event_code, 0)
            date_start = 2 + data_size

            # DATA 추출
            raw_data = data[2:date_start] if data_size > 0 else b""

            # 날짜 추출
            year   = data[date_start]     + 2000
            month  = data[date_start + 1]
            day    = data[date_start + 2]
            hour   = data[date_start + 3]
            minute = data[date_start + 4]
            second = data[date_start + 5]

            date_str = (
                f"{year:04d}-{month:02d}-{day:02d} "
                f"{hour:02d}:{minute:02d}:{second:02d}"
            )

            return {
                "header"     : header,
                "event_code" : event_code,
                "raw_data"   : raw_data,
                "date"       : date_str,
            }

        except Exception as e:
            print(f"[Protocol] 파싱 오류 : {e}")
            return None

    @staticmethod
    def _verify_crc(data: bytes) -> bool:
        try:
            crc_msb = data[14]
            crc_lsb = data[15]
            calc    = sum(data[:14]) & 0xFFFF
            return ((calc >> 8) == crc_msb) and ((calc & 0xFF) == crc_lsb)
        except Exception as e:
            print(f"[Protocol] CRC 검증 오류 : {e}")
            return False