from itertools import groupby
import pymupdf


def open_pdf(file_path):
    return pymupdf.open(file_path)


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
    file_path, chs_names=("Part", "Appendices"), problems_name="Problems"
):
    doc = open_pdf(file_path)
    validate_filetype(doc)
    toc = is_there_toc(doc)  # Extraer el TOC con detalles

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

    return doc, groupby_chapter(resultados)
