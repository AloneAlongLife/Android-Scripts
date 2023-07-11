from adb import AdbSession

from datetime import datetime
from logging import getLogger, INFO, StreamHandler, Formatter
from time import sleep
from typing import Union

FUNCTION_DICT: dict[str, list[str]] = {}

LOGGER = getLogger("interpreter")
handler = StreamHandler()
handler.setFormatter(Formatter(fmt="[%(levelname)s]%(message)s"))
LOGGER.addHandler(handler)


def read_script_file(filename: str) -> list[str]:
    with open(filename, encoding="utf-8") as script_file:
        scripts = script_file.readlines()

    return scripts


def scripts_interpreter(scripts: list[str], adb_session: AdbSession, log_level: Union[int, str] = INFO):
    LOGGER.setLevel(log_level)

    # 加上檔案位置
    p_scripts: list[tuple[str, str]] = list(
        map(lambda tup: (tup[1], f"main.L-{tup[0]}"), enumerate(scripts, 1)))

    # 進行IMPORT
    import_index = 0
    while import_index < len(p_scripts):
        stat = p_scripts[import_index][0].strip().lower()
        if stat.startswith("import"):
            import_path = stat.split(" ", 1)[1].strip()
            import_scripts = read_script_file(import_path)
            p_import_scripts: list[tuple[str, str]] = list(map(lambda tup: (
                tup[1], f"{import_path}.L-{tup[0]}"), enumerate(import_scripts, 1)))

            p_scripts = p_scripts[:import_index] + p_import_scripts + p_scripts[import_index + 1:]
        import_index += 1

    # 尋找標籤位置
    label_dict: dict[str, int] = {
        key[0].strip()[1:]: index
        for index, key in filter(lambda tup: tup[1][0].strip().startswith(":"), enumerate(p_scripts))
    }
    # 變數
    var_dict: dict[str, int] = {}

    point = 0
    last_pos = (0, 0)

    while point < len(p_scripts):
        script = p_scripts[point][0].strip().split()
        # 下一行
        point += 1

        # 空行
        # input(script)
        if len(script) == 0:
            continue
        time = datetime.now().isoformat()
        LOGGER.debug(f"{time} {p_scripts[point - 1][1]} > {p_scripts[point - 1][0].strip()}")

        # 註解、標籤
        if script[0].startswith(("#", ":")):
            continue

        # IF 結束標記
        if script[0].lower() == "fi":
            continue

        # ELSE 直接跳至 FI
        if script[0].lower() == "else":
            if_num = 0
            while True:
                temp_script = p_scripts[point][0].strip().split()
                point += 1

                # 空行
                if len(temp_script) == 0:
                    continue

                # 檢查是否進入巢狀結構
                if temp_script[0].lower() == "if":
                    if_num += 1
                elif temp_script[0].lower() == "fi" and if_num > 0:
                    if_num -= 1
                    continue

                # 檢查是否已經離開巢狀結構
                if if_num > 0:
                    continue
                elif temp_script[0].lower() == "fi":
                    break
            continue

        # 輸出
        if script[0].lower() in ("log", "debug", "info", "warn", "error", "fatal"):
            level = script[0].lower()
            string = " ".join(
                map(lambda s: str(var_dict[s[1:]]) if s.startswith("%") else s, script[1:]))
            if level == "debug":
                LOGGER.debug(string)
            elif level == "log":
                print(string)
            elif level == "info":
                LOGGER.info(string)
            elif level == "warn":
                LOGGER.warning(string)
            elif level == "error":
                LOGGER.error(string)
            elif level == "fatal":
                LOGGER.critical(string)
            continue

        # GOTO
        if script[0].lower() == "goto":
            point = label_dict[script[1]]
            continue

        # 宣告變數
        if script[0].lower() == "var":
            var_name = script[1]
            if len(script) < 3:
                val = 0
            else:
                val = script[2]
                val = int(val) if val.isdigit() else var_dict[val]
            var_dict[var_name] = val
            continue

        # 輸入
        if script[0].lower() == "inp":
            var_name = script[1]
            var_dict[var_name] = int(input())
            continue

        # 加、減、乘
        if script[0].lower() in ("add", "reduce", "multi"):
            oper = script[0].lower()

            var_name = script[1]
            origin_val = var_dict[var_name]
            if len(script) < 3:
                val = 1
            else:
                val = script[2]
                val = int(val) if val.isdigit() else var_dict[val]

            if oper == "add":
                origin_val += val
            elif oper == "reduce":
                origin_val -= val
            else:
                origin_val *= val

            var_dict[var_name] = origin_val
            continue

        # IF +1 ELSE +2
        if script[0].lower() == "if":
            # 數字比較
            val_1 = script[1]
            val_2 = script[3]

            val_1 = int(val_1) if val_1.isdigit() else var_dict[val_1]
            val_2 = int(val_2) if val_2.isdigit() else var_dict[val_2]

            if script[2] == ">":
                ans = val_1 > val_2
            elif script[2] == ">=":
                ans = val_1 >= val_2
            elif script[2] == "<":
                ans = val_1 < val_2
            elif script[2] == "<=":
                ans = val_1 <= val_2
            elif script[2] == "=":
                ans = val_1 == val_2
            elif script[2] == "!=":
                ans = val_1 != val_2

            # 尋找 ELSE/FI
            if not ans:
                if_num = 0
                while True:
                    temp_script = p_scripts[point][0].strip().split()
                    point += 1

                    # 空行
                    if len(temp_script) == 0:
                        continue

                    # 檢查是否進入巢狀結構
                    if temp_script[0].lower() == "if":
                        if_num += 1
                    elif temp_script[0].lower() == "fi" and if_num > 0:
                        if_num -= 1
                        continue

                    # 檢查是否已經離開巢狀結構
                    if if_num > 0:
                        continue
                    elif temp_script[0].lower() == "else" or temp_script[0].lower() == "fi":
                        break
            continue

        # 點擊
        if script[0].lower() == "tap":
            if len(script) > 2:
                x, y = script[1], script[2]
            else:
                x, y = map(str, last_pos)
            adb_session.tap(x, y)
            continue

        # 等待秒數
        if script[0].lower() == "sleep":
            sleep(float(script[1]))
            continue
