from config import QThread, pyqtSignal
import socket


class IpMonitor(QThread):
    status_changed = pyqtSignal(bool)

    def __init__(self, ip: str, port: int = 5000):
        super().__init__()
        self.ip      = ip
        self.port    = port
        self.running = False
        self.is_busy = False

    def set_busy(self, busy: bool):
        self.is_busy = busy

    def run(self):
        self.running = True

        # ── 최초 연결 시도만 담당 (10초) ──────────────
        elapsed = 0
        while self.running and elapsed < 20:
            try:
                if self._check_connection():
                    self.status_changed.emit(True)
                    return   # 연결 성공 후 스레드 종료
                             # 이후 연결 감시는 TcpClient 결과로 판단
            except Exception as e:
                print(f"[IpMonitor] 연결 시도 중 오류 : {e}")

            self.msleep(500)
            elapsed += 1

        # 실패
        self.status_changed.emit(False)

    def notify_disconnected(self):
        """
        TcpClient 가 연결 실패(ConnectionRefusedError 등)를 감지했을 때
        외부에서 직접 호출해서 끊김을 알림
        """
        self.status_changed.emit(False)

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
            self.quit()
            self.wait(2000)
        except Exception as e:
            print(f"[IpMonitor] stop 오류 : {e}")