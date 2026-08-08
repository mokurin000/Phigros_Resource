import json
import os
from pathlib import Path
import sys
import tempfile
from UnityPy import Environment
import zipfile
from io import BytesIO
from log import init_console_logger

DEBUG = False


def run(path, logger):
    Tips = None
    with open("typetree.json") as f:
        typetree = json.load(f)
    env = Environment()
    with zipfile.ZipFile(path) as apk:
        try:
            with apk.open("assets/bin/Data/globalgamemanagers.assets") as f:
                env.load_file(
                    BytesIO(f.read()), name="assets/bin/Data/globalgamemanagers.assets"
                )
        except KeyError:
            with tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)

                print("[+] extracting assets")

                for info in apk.infolist():
                    if info.filename.startswith("assets/"):
                        apk.extract(info, tmp)

                print("[+] loading assets folder")

                env.load_folder(tmp / "assets")

        for i in range(100):
            try:
                with apk.open(f"assets/bin/Data/level{i}") as f:
                    env.load_file(BytesIO(f.read()))
            except KeyError:
                break
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        if data.m_Script.get_obj().read().name == "GameInformation":
            # GameInformation = obj.read_typetree(typetree["GameInformation"])
            pass
        elif data.m_Script.get_obj().read().name == "GetCollectionControl":
            # Collections = obj.read_typetree(typetree["GetCollectionControl"], True)
            pass
        elif data.m_Script.get_obj().read().name == "TipsProvider":
            Tips = obj.read_typetree(typetree["TipsProvider"], True)

    with open("info/tips.txt", "w", encoding="utf8") as f:
        for tip in Tips.tips[0].tips:
            f.write(tip)
            f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) == 1 and os.path.isdir("/data/"):
        import subprocess

        r = subprocess.run(
            "pm path com.PigeonGames.Phigros",
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        file_path = r.stdout[8:-1].decode()
    else:
        file_path = sys.argv[1]
    if not os.path.isdir("info"):
        os.mkdir("info")
    run(file_path, init_console_logger())
