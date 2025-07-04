from pdf.toc import where_to_look_for_problems
from utils.dirs import gen_dir, clean_filename
from pdf.images import get_problems
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


def path_obj_to_str(obj):
    if isinstance(obj, Path):
        return str(obj)


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

    base_dir = path_obj_to_str(base_dir)

    print(base_dir)


if __name__ == "__main__":
    # extract_n_create(archivo)
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--out_dir", type=str, default=None)
    parser.add_argument("--chs_names", nargs="+", default=("Part", "Appendices"))
    parser.add_argument("--problems_name", type=str, default="Problems")
    args = parser.parse_args()

    extract_n_create(args.input_file, args.out_dir, args.chs_names, args.problems_name)
