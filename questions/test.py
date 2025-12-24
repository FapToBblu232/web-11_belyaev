from configparser import ConfigParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
config = ConfigParser()
conf_path = BASE_DIR / "question_project" / "prod.conf"
config.read(conf_path, encoding="utf-8")

for section in config.sections():
    for key, value in config.items(section):
        print(f"{section}.{key} = {repr(value)}")

