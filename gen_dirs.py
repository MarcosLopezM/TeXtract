# import os
import re
from utils import ensures_output_folder_exists
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
    idx = 1

    for chapter, sections in data.items():
        clean_ch_name = (
            clean_filename(chapter)
            if re.match(r"^\d", chapter)
            else f"{idx:02d}_{clean_filename(chapter)}"
        )
        cleaned_sections = []
        for section in sections:
            clean_sec_name = clean_filename(section["section"])
            clean_sec_name = re.sub(
                r"^(\d+)_?(.*)",
                lambda m: f"{int(m.group(1)):02d}_{m.group(2)}"
                if m.group(2)
                else f"{int(m.group(1)):02d}",
                clean_sec_name,
            )

            section["section"] = clean_sec_name
            cleaned_sections.append(section)

        cleaned_data[clean_ch_name] = cleaned_sections
        idx += 1

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
