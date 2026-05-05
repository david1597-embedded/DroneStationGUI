from config import QThread, pyqtSignal
import socket

class IpMonitor(QThread):
    status_changed = pyqtSignal(bool)

    def __init__(self, ip: str, port: int = 5000):
        super().__init__()
        self.ip      = ip
        self.port    = port
        self.running = False

    def run(self):
        self.running = True
        elapsed = 0

        while self.running and elapsed < 10:
            try:
                connected = self._check_connection()
                if connected:
                    self.status_changed.emit(True)
                    return
            except Exception as e:
                print(f"[IpMonitor] 연결 시도 중 오류 : {e}")

            self.msleep(500)
            elapsed += 1

        # 10초 내 연결 실패
        try:
            self.status_changed.emit(False)
        except Exception as e:
            print(f"[IpMonitor] 시그널 전송 오류 : {e}")

    def _check_connection(self) -> bool:
        try:
            sock = socket.create_connection((self.ip, self.port), timeout=1)
            sock.close()
            return True
        except OSError:
            return False
        except Exception as e:
            print(f"[IpMonitor] 소켓 오류 : {e}")
            return False

    def stop(self):
        try:
            self.running = False
            self.quit()  # 스레드 이벤트 루프 종료
            self.wait(2000)  # 최대 2초 대기
        except Exception as e:
            print(f"[IpMonitor] stop 오류 : {e}")