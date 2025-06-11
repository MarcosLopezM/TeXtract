# import os
import re
from utils import save_to_json, open_json

# from pathlib import Path
from prettyprinter import cpprint


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


data = open_json("./problemas_Schwartz.json")
data = clean_data(data)
cpprint(data)
save_to_json(data, "problems.json")
