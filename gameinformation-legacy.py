import os
from pathlib import Path
import sys
import tempfile
import zipfile

from UnityPy import Environment


DEBUG = True


SHOWTIPS_TYPE_TREE = {
    "ShowTips": [
        {"m_Type": "MonoBehaviour", "m_Name": "Base", "m_MetaFlag": 0, "m_Level": 0},
        # m_GameObject
        {
            "m_Type": "PPtr<GameObject>",
            "m_Name": "m_GameObject",
            "m_MetaFlag": 0,
            "m_Level": 1,
        },
        {"m_Type": "int", "m_Name": "m_FileID", "m_MetaFlag": 0, "m_Level": 2},
        {"m_Type": "SInt64", "m_Name": "m_PathID", "m_MetaFlag": 0, "m_Level": 2},
        # m_Enabled
        {"m_Type": "UInt8", "m_Name": "m_Enabled", "m_MetaFlag": 16384, "m_Level": 1},
        # m_Script
        {
            "m_Type": "PPtr<MonoScript>",
            "m_Name": "m_Script",
            "m_MetaFlag": 0,
            "m_Level": 1,
        },
        {"m_Type": "int", "m_Name": "m_FileID", "m_MetaFlag": 0, "m_Level": 2},
        {"m_Type": "SInt64", "m_Name": "m_PathID", "m_MetaFlag": 0, "m_Level": 2},
        # m_Name
        {"m_Type": "string", "m_Name": "m_Name", "m_MetaFlag": 0, "m_Level": 1},
        {"m_Type": "Array", "m_Name": "Array", "m_MetaFlag": 16384, "m_Level": 2},
        {"m_Type": "int", "m_Name": "size", "m_MetaFlag": 0, "m_Level": 3},
        {"m_Type": "char", "m_Name": "data", "m_MetaFlag": 0, "m_Level": 3},
        # chinese
        {"m_Type": "string", "m_Name": "chinese", "m_MetaFlag": 0, "m_Level": 1},
        {"m_Type": "Array", "m_Name": "Array", "m_MetaFlag": 16384, "m_Level": 2},
        {"m_Type": "int", "m_Name": "size", "m_MetaFlag": 0, "m_Level": 3},
        {"m_Type": "char", "m_Name": "data", "m_MetaFlag": 0, "m_Level": 3},
        # chineseTraditional
        {
            "m_Type": "string",
            "m_Name": "chineseTraditional",
            "m_MetaFlag": 0,
            "m_Level": 1,
        },
        {"m_Type": "Array", "m_Name": "Array", "m_MetaFlag": 16384, "m_Level": 2},
        {"m_Type": "int", "m_Name": "size", "m_MetaFlag": 0, "m_Level": 3},
        {"m_Type": "char", "m_Name": "data", "m_MetaFlag": 0, "m_Level": 3},
        # english
        {"m_Type": "string", "m_Name": "english", "m_MetaFlag": 0, "m_Level": 1},
        {"m_Type": "Array", "m_Name": "Array", "m_MetaFlag": 16384, "m_Level": 2},
        {"m_Type": "int", "m_Name": "size", "m_MetaFlag": 0, "m_Level": 3},
        {"m_Type": "char", "m_Name": "data", "m_MetaFlag": 0, "m_Level": 3},
        # japanese
        {"m_Type": "string", "m_Name": "japanese", "m_MetaFlag": 0, "m_Level": 1},
        {"m_Type": "Array", "m_Name": "Array", "m_MetaFlag": 16384, "m_Level": 2},
        {"m_Type": "int", "m_Name": "size", "m_MetaFlag": 0, "m_Level": 3},
        {"m_Type": "char", "m_Name": "data", "m_MetaFlag": 0, "m_Level": 3},
        # tipText
        {"m_Type": "PPtr<Text>", "m_Name": "tipText", "m_MetaFlag": 0, "m_Level": 1},
        {"m_Type": "int", "m_Name": "m_FileID", "m_MetaFlag": 0, "m_Level": 2},
        {"m_Type": "SInt64", "m_Name": "m_PathID", "m_MetaFlag": 0, "m_Level": 2},
    ]
}


def load_apk_assets(path):

    env = Environment()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        print("[+] extracting assets")

        with zipfile.ZipFile(path) as apk:
            for info in apk.infolist():
                if info.filename.startswith("assets/"):
                    apk.extract(info, tmp)

        print("[+] loading assets folder")

        env.load_folder(tmp / "assets")

    return env


def extract_showtips(path):

    env = load_apk_assets(path)

    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue

        try:
            raw = obj.read()

            script = raw.m_Script.get_obj()

            if script is None:
                continue

            script_name = script.read().name

            if script_name != "ShowTips":
                continue

            print("[+] Found ShowTips:", obj.path_id)

            data = obj.read_typetree(SHOWTIPS_TYPE_TREE["ShowTips"], True)

            return data

        except Exception as e:
            if DEBUG:
                print(e)

    return None


def save_tips(data):

    if not os.path.exists("info"):
        os.mkdir("info")
    languages = ["chinese"]

    with open("info/tips.txt", "w", encoding="utf8") as f:
        for lang in languages:
            text = data[lang]

            # 原数据使用 / 分隔
            tips = text.split("/")

            for tip in tips:
                tip = tip.strip()

                if tip:
                    f.write(tip)
                    f.write("\n")

    print("[+] saved info/tips.txt")


def main():

    if len(sys.argv) < 2:
        print("Usage: python extract.py xxx.apk")

        return

    apk = sys.argv[1]

    data = extract_showtips(apk)

    if data is None:
        print("[-] ShowTips not found")

        return

    save_tips(data)


if __name__ == "__main__":
    main()
