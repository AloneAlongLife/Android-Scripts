from subprocess import run, PIPE, DEVNULL

from cv2 import Mat, imdecode, IMREAD_COLOR
from numpy import frombuffer, uint8


class AdbSession:
    def __init__(self, serial: str) -> None:
        self.serial = serial

        connect_device = run(["adb", "devices"], stdout=PIPE).stdout.decode()
        self.connected = serial in connect_device

        if not self.connected:
            run(["adb", "connect", serial])

            connect_device = run(["adb", "devices"],
                                 stdout=PIPE).stdout.decode()
            self.connected = serial in connect_device

    def screen_shot(self) -> Mat:
        """
        取得畫面
        """
        if not self.connected:
            raise RuntimeError("Device not connect.")

        raw_screen = run(["adb", "-s", self.serial, "exec-out",
                         "screencap", "-p"], stdout=PIPE).stdout
        return imdecode(frombuffer(raw_screen, uint8), IMREAD_COLOR)

    def tap(self, x: int, y: int) -> None:
        """
        點擊螢幕
        """
        run(["adb", "-s", self.serial, "shell",
            "input", "tap", x, y], stdout=DEVNULL)

    def swipe(
        self,
        start_x: int, start_y: int,
        end_x: int, end_y: int,
        duration: int = 100
    ) -> None:
        """
        滑動螢幕
        """
        run(["adb", "-s", self.serial, "shell", "input", "swipe",
            start_x, start_y, end_x, end_y, duration], stdout=DEVNULL)
