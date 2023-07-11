from subprocess import run, PIPE, DEVNULL


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
