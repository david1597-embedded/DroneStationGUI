from config import QThread, pyqtSignal
import socket
from network.protocol import Protocol

class TcpClient(QThread):
    data_received  = pyqtSignal(dict)   # 파싱된 패킷 → log_parser로 전달
    receive_done   = pyqtSignal()        # 수신 완료
    receive_failed = pyqtSignal(str)     # 수신 실패 (오류 메시지)

    def __init__(self, ip: str, port: int = 5000):
        super().__init__()
        self.ip       = ip
        self.port     = port
        self.sock     = None
        self.command  = ""
        self.running  = False

    # ── 송신 + 수신 시작 ──────────────────────────
    def request_log(self, command: str):
        self.command = command  # ex) "[LOG104]"
        self.start()

    def run(self):
        self.running = True
        try:
            # 소켓 연결
            self.sock = socket.create_connection((self.ip, self.port), timeout=5)

            # 커맨드 송신
            self.sock.sendall(self.command.encode("ascii"))
            print(f"[TcpClient] 송신 : {self.command}")

            # 데이터 수신 (16바이트씩)
            self._receive_loop()

        except socket.timeout:
            self.receive_failed.emit("연결 시간 초과")
        except ConnectionRefusedError:
            self.receive_failed.emit("연결 거부됨")
        except Exception as e:
            self.receive_failed.emit(str(e))
        finally:
            self._close_socket()

    def _receive_loop(self):
        buffer = b""
        try:
            while self.running:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break  # 연결 종료

                buffer += chunk

                # 16바이트씩 파싱
                while len(buffer) >= Protocol.PACKET_SIZE:
                    packet = buffer[:Protocol.PACKET_SIZE]
                    buffer = buffer[Protocol.PACKET_SIZE:]

                    parsed = Protocol.parse_packet(packet)
                    if parsed:
                        self.data_received.emit(parsed)

            self.receive_done.emit()

        except Exception as e:
            self.receive_failed.emit(str(e))

    def _close_socket(self):
        try:
            if self.sock:
                self.sock.close()
                self.sock = None
        except Exception as e:
            print(f"[TcpClient] 소켓 종료 오류 : {e}")

    def stop(self):
        self.running = False
        self._close_socket()
        self.quit()
        self.wait(2000)