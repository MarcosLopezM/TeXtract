# import os
import re
from utils import ensures_output_folder_exists, save_to_json, open_json
from pathlib import Path


def clean_filename(name):
    """
    Converts the tile of the chapters, sections, and problems into a safe filename.
    """
    name = re.sub(r"[^a-zA-Z0-9\s\-_]", "", name)
    name = name.replace(" ", "_")
    return name.strip("_")


def clean_data(data):
    cleaned_data = {}

    for chapter, sections in data.items():
        clean_ch_name = clean_filename(chapter)
        cleaned_sections = []
        for section in sections:
            clean_sec_name = clean_filename(section["section"])
            section["section"] = clean_sec_name
            cleaned_sections.append(section)

        cleaned_data[clean_ch_name] = cleaned_sections

    return cleaned_data


def gen_dir(data, out_dir):
    data = clean_data(data)  # Clean the data -> Create directories with new names
    base_dir = Path(out_dir)

    for chapter, sections in data.items():
        for section in sections:
            dir_path = base_dir / f"{chapter}/{section['section']}"
            print(f"Creating directory at: {dir_path}")
            # Ensure the directory exists
            ensures_output_folder_exists(dir_path)

    return base_dir
