import pymupdf
from pathlib import Path
from utils import save_to_json, ensures_output_folder_exists
from itertools import groupby


def validate_filetype(doc):
    if not doc.is_pdf:
        raise ValueError("El archivo no es un PDF válido.")


def is_there_toc(doc):
    toc = doc.get_toc(simple=False)
    if len(toc) == 0:
        raise ValueError("El documento no contiene un TOC válido.")
    return toc


# Filtramos el TOC para obtener las secciones con problemas
def groupby_chapter(resultados):
    group_same_ch = {
        key: list(group)
        for key, group in groupby(resultados, key=lambda x: x["chapter"])
    }

    for _, sections in group_same_ch.items():
        for section in sections:
            del section["chapter"]

    return group_same_ch


def where_to_look_for_problems(
    toc, chs_names=("Part", "Appendices"), problems_name="Problems"
):
    resultados = []
    cur_level_1 = None
    cur_level_2 = None

    for i, item in enumerate(toc):
        level = item[0]
        title = item[1].strip()

        if level == 1 and title.startswith(chs_names):
            cur_level_1 = title
            cur_level_2 = None
        elif level == 2:
            cur_level_2 = title
        elif level == 3 and title == problems_name:
            page = int(item[3]["page"])
            if cur_level_1 is not None:
                if i + 1 < len(toc):
                    next_page = int(toc[i + 1][3]["page"]) - 1
                else:
                    next_page = len(doc) - 1

                resultados.append(
                    {
                        "chapter": cur_level_1,
                        "section": cur_level_2,
                        "title": title,
                        "page_start": page,
                        "page_end": next_page,
                    }
                )
    return groupby_chapter(resultados)


# Extraer los problemas y las imágenes en un solo bucle
def get_problems(doc, resultados, output_folder):
    ensures_output_folder_exists(output_folder)

    for chapter in resultados:
        for section in resultados[chapter]:
            page_start = section["page_start"]
            page_end = section["page_end"] + 1
            section_title = section["section"]
            title = section.get("title", "")

            # --------- Extracción de imágenes donde se encuentran los problemas ---------
            if title == "Problems":
                start = page_start
                end = page_end

                for page_number in range(start, end):
                    page = doc.load_page(page_number)

                    pix = page.get_pixmap()

                    # Nombre de archivo
                    section_title = section.get("section", "Unknown_Section")
                    safe_section_name = (
                        str(section_title).replace(" ", "_").replace("/", "_")
                    )
                    image_filename = f"{safe_section_name}_page_{page_number + 1}.png"
                    image_path = Path(output_folder) / image_filename
                    section["image_path"] = str(image_path)

                    # Guardar imagen
                    pix.save(image_path)


## Ejemplo de uso para validar el PDF y verificar el TOC
doc = pymupdf.open(
    "./Matthew D. Schwartz - Quantum Field Theory And The Standard Model-Cambridge University Press (2014).pdf"
)
validate_filetype(doc)  # Validar el tipo de archivo PDF
toc = is_there_toc(doc)  # Extraer el TOC con detalles
resultados = where_to_look_for_problems(toc)
output_folder = "./figs/"
get_problems(doc, resultados, output_folder)
save_to_json(resultados, "problemas_Schwartz.json")
