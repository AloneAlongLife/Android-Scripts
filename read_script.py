from adb import AdbSession
from img_det import find

import cv2

from datetime import datetime
from time import sleep

FUNCTION_DICT: dict[str, list[str]] = {}

def read_script_file(filename: str) -> list[str]:
    with open(filename, encoding="utf-8") as script_file:
        scripts = script_file.readlines()

    return scripts


def scripts_interpreter(scripts: list[str], adb_session: AdbSession):
    label_dict: dict[str, int] = {
        key.strip()[1:]: index
        for index, key in filter(lambda tup: tup[1].strip().startswith(":"), enumerate(scripts))
    }

    
    point = 0
    last_pos = (0, 0)

    while point < len(scripts):
        script = scripts[point].strip().split()

        if len(script) == 0:
            point += 1
            continue
        print(f"{datetime.now().isoformat()} L-{point + 1} > {scripts[point].strip()}")

        # 註解
        if script[0].startswith("#"):
            point += 1
            continue

        if script[0].startswith(":"):
            point += 1
            continue

        if script[0].lower() == "fi":
            point += 1
            continue

        if script[0].lower() == "else":
            if_num = 0
            while True:
                point += 1
                temp_script = scripts[point].strip().split()
                
                if len(temp_script) == 0:
                    continue

                if temp_script[0].lower() == "if":
                    if_num += 1
                    continue

                if temp_script[0].lower() == "fi" and if_num > 0:
                    if_num -= 1
                    continue

                if temp_script[0].lower() == "fi":
                    break
            continue

        # 輸出
        if script[0].lower() == "log":
            print(" ".join(script[1:]))
            point += 1
            continue
        
        # GOTO
        if script[0].lower() == "goto":
            label = script[1]
            point = label_dict[label]
            continue

        # IF +1 ELSE +2
        if script[0].lower() == "if":
            template_path = script[1]

            try:
                if script[2].lower() == "debug":
                    debug = True
                else:
                    debug = False
            except:
                debug = False
            
            template = cv2.imread(template_path)
            screen_shot = adb_session.screen_shot()
            res, pos = find(template, screen_shot, debug=debug)

            if res:
                last_pos = pos
                point += 1
            else:
                if_num = 0
                while True:
                    point += 1
                    temp_script = scripts[point].strip().split()
                    
                    if len(temp_script) == 0:
                        continue

                    if temp_script[0].lower() == "if":
                        if_num += 1
                        continue

                    if temp_script[0].lower() == "fi" and if_num > 0:
                        if_num -= 1
                        continue
                    
                    if temp_script[0].lower() == "else" or temp_script[0].lower() == "fi":
                        if if_num > 0:
                            continue
                        point += 1
                        break
            continue

        # 點擊
        if script[0].lower() == "tap":
            if len(script) == 3:
                x = script[1]
                y = script[2]
                adb_session.tap(x, y)
            else:
                adb_session.tap(*map(str, last_pos))
            point += 1
            continue

        # 等待秒數
        if script[0].lower() == "sleep":
            seconds = float(script[1])
            sleep(seconds)
            point += 1
            continue
