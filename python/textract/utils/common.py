import json
from pathlib import Path


def open_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensures_output_folder_exists(path):
    dir = Path(path)
    dir.mkdir(parents=True, exist_ok=True)
