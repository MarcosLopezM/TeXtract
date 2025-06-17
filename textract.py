from gen_dirs import gen_dir, clean_filename
from toc_extract import where_to_look_for_problems
from img_extract import get_problems
from pathlib import Path


def default_output_name(doc, fallback_stem):
    try:
        title = clean_filename(doc.metadata.get("title", ""))
        author = clean_filename(doc.metadata.get("author", "").split()[-1])

        if title and author:
            return f"{title}-{author}"

    except Exception:
        pass

    return f"{clean_filename(fallback_stem)}"


def extract_n_create(input_file, out_dir=None, chs_names=None, problems_name=None):
    input_file = Path(input_file)
    doc, resultados = where_to_look_for_problems(
        input_file,
        chs_names=chs_names if chs_names is not None else ("Part", "Appendices"),
        problems_name=problems_name if problems_name is not None else "Problems",
    )

    if out_dir is None:
        out_dir = default_output_name(
            doc,
            input_file.stem if input_file.suffix == ".pdf" else input_file.name,
        )

    base_dir = gen_dir(resultados, out_dir)
    get_problems(doc, resultados, base_dir)

    return base_dir


"""
  Ejemplo de uso para extraer problemas de un PDF
"""

archivo = "./Matthew D. Schwartz - Quantum Field Theory And The Standard Model-Cambridge University Press (2014).pdf"
if __name__ == "__main__":
    extract_n_create(archivo)
