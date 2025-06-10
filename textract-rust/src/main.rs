use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashMap};
use std::fs::{self, File};
use std::io::{self, BufReader, Write};
use std::path::Path;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Problem {
    section: String,
    title: String,
    page_start: u32,
    page_end: u32,
    content: String,
    #[serde(default)]
    image_path: Option<String>,
}

type ProblemsByPart = HashMap<String, Vec<Problem>>;

fn create_dir_if_not_exists(path: &str) -> io::Result<()> {
    if Path::new(path).exists() {
        println!("El directorio '{}' ya existe.", path);
    } else {
        fs::create_dir_all(path)?;
        println!("Directorio '{}' creado.", path);
    }
    Ok(())
}

fn write_problems_tex(path: &str, problems: &[Problem]) -> io::Result<()> {
    let mut file = File::create(path)?;
    writeln!(file, "% Archivo generado automáticamente con los problemas")?;

    for problem in problems {
        writeln!(file, "\\section*{{{}}}", problem.title)?;
        writeln!(file, "Sección: {}", problem.section)?;
        writeln!(file, "Páginas: {}-{}", problem.page_start, problem.page_end)?;
        writeln!(file, "Contenido:\n{}\n", problem.content)?;
        if let Some(img) = &problem.image_path {
            writeln!(file, "\\includegraphics{{{}}}", img)?;
        }
        writeln!(file, "\n---\n")?;
    }

    Ok(())
}

fn main() -> io::Result<()> {
    let root = "title_book";
    create_dir_if_not_exists(root)?;
    create_dir_if_not_exists(&format!("{}/figs", root))?;
    let chapters_path = format!("{}/chapters", root);
    create_dir_if_not_exists(&chapters_path)?;

    // Leer JSON
    let file = File::open("../resultados.json")?;
    let reader = BufReader::new(file);
    let problems_by_part: ProblemsByPart =
        serde_json::from_reader(reader).expect("Error al leer JSON");

    for (part_name, problems) in &problems_by_part {
        let chapter_path = format!(
            "{}/{}",
            chapters_path,
            part_name.to_lowercase().replace(" ", "_")
        );
        create_dir_if_not_exists(&chapter_path)?;

        let chapter_tex_path = format!("{}/chapter.tex", chapter_path);
        let mut chapter_file = File::create(&chapter_tex_path)?;
        writeln!(chapter_file, "% Archivo {} chapter.tex", part_name)?;

        // Agrupar problemas por sección
        let mut sections_map: BTreeMap<String, Vec<Problem>> = BTreeMap::new();
        for problem in problems {
            sections_map
                .entry(problem.section.clone())
                .or_default()
                .push(problem.clone());
        }

        for (section_name, problems_in_section) in &sections_map {
            let section_path = format!("{}/{}", chapter_path, section_name);
            create_dir_if_not_exists(&section_path)?;

            let problems_tex_path = format!("{}/problems.tex", section_path);
            write_problems_tex(&problems_tex_path, problems_in_section)?;
            println!(
                "Archivo '{}' creado con {} problemas.",
                problems_tex_path,
                problems_in_section.len()
            );
        }
    }

    println!("Estructura y archivos creados con contenido.");
    Ok(())
}

