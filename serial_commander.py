import threading
import time
from typing import Optional

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class SerialCommander:

    _LEVEL_CMD = {
        "INFO":      b'I',
        "WARNING":   b'W',
        "CRITICAL":  b'C',
        "EMERGENCY": b'E',
    }
    _CLEAR_CMD = b'0'

    def __init__(self, port: str = None, baud: int = 9600):
        self._port      = port
        self._baud      = baud
        self._ser: Optional[object] = None
        self._connected = False
        self._lock      = threading.Lock()


    @staticmethod
    def auto_detect_port() -> Optional[str]:

        if not SERIAL_AVAILABLE:
            return None
        keywords = ['CH340', 'CP210', 'UART', 'USB SERIAL', 'ESP32', 'SILICON']
        for port in serial.tools.list_ports.comports():
            if any(kw in port.description.upper() for kw in keywords):
                return port.device

        ports = list(serial.tools.list_ports.comports())
        return ports[0].device if ports else None

    def connect(self) -> bool:
        if not SERIAL_AVAILABLE:
            print("[SerialCommander] pyserial not installed — hardware disabled")
            return False
        try:
            port = self._port or self.auto_detect_port()
            if not port:
                print("[SerialCommander] No COM port found — running without hardware")
                return False
            self._ser = serial.Serial(port, self._baud, timeout=1)
            time.sleep(2)
            self._connected = True
            print(f"[SerialCommander] ✅ ESP32 connected on {port}")
            return True
        except Exception as exc:
            print(f"[SerialCommander] Connection failed: {exc}")
            return False

    def is_connected(self) -> bool:
        return self._connected


    def send_alert(self, level: str) -> bool:
        if not self._connected:
            return False
        cmd = self._LEVEL_CMD.get(level.upper(), b'I')
        with self._lock:
            try:
                self._ser.write(cmd)
                return True
            except Exception as exc:
                print(f"[SerialCommander] Send error: {exc}")
                self._connected = False
                return False

    def clear(self):
        if not self._connected:
            return
        with self._lock:
            try:
                self._ser.write(self._CLEAR_CMD)
            except Exception:
                pass

    def disconnect(self):
        self.clear()
        if self._ser:
            self._ser.close()
        self._connected = False
