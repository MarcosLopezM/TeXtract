from utils.common import ensures_output_folder_exists
from pathlib import Path
from utils.dirs import clean_filename


#
# Extraer las imágenes de los problemas
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
                ch_name = clean_filename(chapter)
                subfolder = Path(output_folder) / f"figs/{ch_name}/{section_title}"
                ensures_output_folder_exists(subfolder)

                for page_number in range(start, end):
                    page = doc.load_page(page_number)

                    pix = page.get_pixmap()

                    # Nombre de archivo
                    section_title = section.get("section", "Unknown_Section")
                    safe_section_name = (
                        str(section_title).replace(" ", "_").replace("/", "_")
                    )
                    image_filename = f"{safe_section_name}_page_{page_number + 1}.png"
                    image_path = subfolder / image_filename
                    section["image_path"] = str(image_path)

                    # Guardar imagen
                    pix.save(image_path)
