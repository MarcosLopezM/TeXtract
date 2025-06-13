import re
from utils import ensures_output_folder_exists
from pathlib import Path

FILENAME_PATTERN = re.compile(r"[^a-zA-Z0-9\s\-_]")
SEC_NAME_PATTERN = re.compile(r"^(\d+)_?(.*)")


def clean_filename(name):
    """
    Converts the tile of the chapters, sections, and problems into a safe filename.
    """
    return FILENAME_PATTERN.sub("", name).replace(" ", "_").strip("_")


def clean_ch_name(name, idx):
    if re.match(r"^\d", name):
        return clean_filename(name)
    else:
        return f"{idx:02d}_{clean_filename(name)}"


def clean_sec_name(name):
    cln_name = clean_filename(name)
    match_patttern = SEC_NAME_PATTERN.match(cln_name)

    if not match_patttern:
        return cln_name

    num, rest = match_patttern.groups()
    return f"{int(num):02d}_{rest}" if rest else f"{int(num):02d}"


def clean_data(data):
    cleaned_data = {}
    idx = 1

    for chapter, sections in data.items():
        ch_name = clean_ch_name(chapter, idx)
        cleaned_sections = []

        for section in sections:
            sec_name = clean_sec_name(section["section"])

            section["section"] = sec_name
            cleaned_sections.append(section)

        cleaned_data[ch_name] = cleaned_sections
        idx += 1

    return cleaned_data


def gen_dir(data, out_dir):
    data = clean_data(data)  # Clean the data -> Create directories with new names
    base_dir = Path(out_dir)

    for chapter, sections in data.items():
        for section in sections:
            dir_path = base_dir / f"{chapter}/{section['section']}"
            # Ensure the directory exists
            ensures_output_folder_exists(dir_path)

    return base_dir
