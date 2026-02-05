import socket
import struct
from PyQt5.QtCore import QThread, pyqtSignal


class UDPReceiver(QThread):
    data_received = pyqtSignal(int, int)

    def __init__(self, ip="192.168.0.3", port=8080):
        super().__init__()
        self.ip = ip
        self.port = port
        self.running = True
        self.is_active = False

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, self.port))
        sock.settimeout(0.5)

        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
                if not self.is_active:
                    continue

                for i in range(0, len(data), 4):
                    chunk = data[i:i + 4]
                    if len(chunk) < 4:
                        continue
                    value = struct.unpack('>I', chunk)[0]

                    # 解析 FPGA 数据: {sin2_do[11:0],4'd0,ad_in[11:0],4'd0}
                    sin_val = (value >> 20) & 0xFFF
                    ad_val = (value >> 4) & 0xFFF

                    # 转为有符号 12-bit
                    if sin_val & 0x800: sin_val -= 0x1000
                    if ad_val & 0x800: ad_val -= 0x1000

                    self.data_received.emit(sin_val, ad_val)
            except socket.timeout:
                continue

    def start_receiving(self):
        """开始接收数据"""
        self.is_active = True

    def stop_receiving(self):
        """停止接收数据"""
        self.is_active = False

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
