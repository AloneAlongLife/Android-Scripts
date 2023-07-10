from adb import AdbSession
from read_script import scripts_interpreter, read_script_file

from logging import _nameToLevel, INFO
from os import chdir, makedirs
from sys import argv

from orjson import dumps, loads, OPT_INDENT_2

HELP = f"""
{argv[0]} [new project_name | run project_name | help]

new  新增一個腳本
run  執行一個腳本
help 顯示此訊息
"""

if __name__ == "__main__":
    option = argv[1].lower()

    if option == "run":
        dir_path = argv[2].strip()

        chdir(dir_path)

        with open("config.json", mode="rb") as config_file:
            config = loads(config_file.read())
        adb_session = AdbSession(config["serial"])
        level = config["log_level"]
        level = level if type(level) == int else _nameToLevel.get(level, INFO)

        scripts = read_script_file("main")
        try:
            scripts_interpreter(scripts, adb_session, log_level=level)
        except KeyboardInterrupt:
            print("User Interrupt.")
    elif option == "new":
        dir_path = argv[2].strip()

        makedirs(dir_path)
        chdir(dir_path)

        with open("config.json", mode="wb") as config_file:
            config_file.write(dumps({
                "serial": "",
                "log_level": "info"
            }, option=OPT_INDENT_2))
        open("main", mode="w").close()
    else:
        print(HELP)
