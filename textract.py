from gen_dirs import gen_dir, clean_filename
from toc_extract import where_to_look_for_problems
from img_extract import get_problems


"""
  Ejemplo de uso para extraer problemas de un PDF
"""
docs = [
    "./An Introduction To Quantum Field Theory -- Michael E_ Peskin; Daniel V_ Schroeder -- Frontiers in Physics, First edition, 2018 -- Westview Press;CRC -- 9780201503975 -- 61d7bc2fb2ae35bda7800392f21f17ad -- Anna’s Archive.pdf",
    "./Matthew D. Schwartz - Quantum Field Theory And The Standard Model-Cambridge University Press (2014).pdf",
    "./Quantum field theory -- Srednicki, Mark -- 14th printing, 2018 -- Cambridge University Press -- 9780511269158 -- 7d33d4ca1b9af25257453d75aeaa47ff -- Anna’s Archive.pdf",
]

for doc in docs:
    file, resultados = where_to_look_for_problems(doc)

    output_folder = f"{clean_filename(file.metadata['title'])}-{clean_filename(file.metadata['author'])}_problems"
    base_dir = gen_dir(resultados, output_folder)
    get_problems(file, resultados, base_dir)
