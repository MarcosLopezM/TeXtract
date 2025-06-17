use once_cell::sync::Lazy;
use regex::Regex;
use rusttex::{ContentBuilder, DocumentClass, options};
use std::fmt;
use std::fs::{self, File, rename};
use std::io::Write;
use std::path::{Path, PathBuf};

static NAME_PREFIX: Lazy<Regex> = Lazy::new(|| Regex::new(r"^\d+_").unwrap());

pub fn write_file<P: AsRef<Path>>(path: P, content: &str) -> std::io::Result<()> {
    let mut file = File::create(path)?;
    file.write_all(content.as_bytes())
}

fn create_preamble(base_dir: &Path) -> std::io::Result<()> {
    const CONTENT: &str = include_str!("preamble.in");
    write_file(base_dir.join("preamble.tex"), CONTENT)
}

fn clean_name(name: &str) -> String {
    NAME_PREFIX.replace(name, "").replace("_", " ")
}

fn create_subfile_tex(folder: &Path, sec_title: &str) -> std::io::Result<()> {
    let mut builder = ContentBuilder::new();

    builder.set_document_class(
        DocumentClass::Custom("subfiles".to_string()),
        options!["../main"],
    );
    builder.add_literal("\\graphicspath{{figs/}}\n");
    builder.begin_document();
    builder.section(sec_title);
    builder.add_literal("\\kant[1-2]");
    builder.end_document();
    let latex = builder.build_document();

    let subfile_path = folder.join("problems.tex");
    write_file(&subfile_path, latex)
}

fn create_main_tex(base_dir: &Path, title_book: &str, author_sol: &str) -> std::io::Result<()> {
    create_preamble(base_dir)?;

    let mut builder = ContentBuilder::new();
    builder.add_literal("%! TeX program = lualatex\n");
    builder.set_document_class(DocumentClass::Book, options![]);
    builder.use_package("subfiles", options![]);
    builder.input("preamble.tex");
    builder.add_literal("\\graphicspath{{figs/}}\n");
    builder.title(title_book);
    builder.author(author_sol);
    builder.add_literal("\\date{\\today}\n");
    builder.begin_document();
    builder.maketitle();
    builder.add_literal("\\tableofcontents\n");

    let mut chapters: Vec<_> = fs::read_dir(base_dir)?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().is_dir())
        .collect();

    chapters.sort_by_key(|e| e.file_name());

    for chapter in &chapters {
        let chapter_name = chapter.file_name().to_string_lossy().to_string();

        if NAME_PREFIX.is_match(&chapter_name) {
            let cln_chapter_name = clean_name(&chapter_name);
            let cln_chapter_path = base_dir.join(&cln_chapter_name);

            if chapter.path() != cln_chapter_path {
                rename(chapter.path(), &cln_chapter_path)?;
            }

            builder.add_literal(&format!(
                "\\chapter{{{}}}\n",
                cln_chapter_name.replace("_", " ")
            ));

            let mut sections: Vec<PathBuf> = fs::read_dir(&cln_chapter_path)?
                .filter_map(|e| e.ok())
                .filter(|e| e.path().is_dir())
                .map(|e| e.path())
                .collect();

            sections.sort();

            for section in &sections {
                let sec_name = match section.file_name() {
                    Some(name) => name.to_string_lossy(),
                    None => {
                        eprintln!("There's no section name {:?}", section);
                        continue;
                    }
                };
                let cln_sec_name = NAME_PREFIX.replace(&sec_name, "").to_string();
                let sec_title = cln_sec_name.replace("_", " ");

                create_subfile_tex(section, &sec_title)?;

                // println!("Creating problems.tex in {:?}", section);
                let subfile_rel_path = match section.strip_prefix(base_dir) {
                    Ok(path) => path.join("problems.tex"),
                    Err(err) => {
                        eprintln!(
                            "Error stripping prefix '{} from {}: {}",
                            base_dir.display(),
                            section.display(),
                            err
                        );
                        continue;
                    }
                };

                let subfile_str = subfile_rel_path.to_string_lossy().replace("\\", "/");
                builder.add_literal(&format!("\\subfile{{\"{}\"}}\n", subfile_str));
            }
        }
    }

    builder.end_document();
    let latex = builder.build_document();
    write_file(base_dir.join("main.tex"), latex)
}

#[allow(dead_code)]
pub enum BookTitle<'a> {
    Static(&'a str),
    Dynamic {
        generator: fn(&str) -> String,
        source: &'a str, // The string to use as input
    },
}

impl<'a> fmt::Display for BookTitle<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            BookTitle::Static(s) => write!(f, "{}", s),
            BookTitle::Dynamic { generator, source } => {
                write!(f, "{}", generator(source))
            }
        }
    }
}

pub struct ProjectParameters<'a> {
    pub base_dir: &'a Path,
    pub book_title: BookTitle<'a>,
    pub author_solns: &'a str,
    pub chs_names: Vec<String>,
    pub problems_name: String,
}

pub fn default_title(base_dir: &str) -> String {
    base_dir.replace("_", " ").replace("-", " ")
}

impl<'a> Default for ProjectParameters<'a> {
    fn default() -> Self {
        Self {
            base_dir: Path::new("."),
            author_solns: "Chris P. Bacon",
            book_title: BookTitle::Dynamic {
                generator: default_title,
                source: "",
            },
            chs_names: vec!["Part".to_string(), "Appendices".to_string()],
            problems_name: "Problems".to_string(),
        }
    }
}

pub fn create_project(params: ProjectParameters) -> std::io::Result<()> {
    let base_dir = params.base_dir;
    let book_title = params.book_title;
    let author_solns = params.author_solns;

    for chapter in fs::read_dir(base_dir)? {
        let chapter = chapter?;
        let chapter_path = chapter.path();

        if chapter_path.is_dir() {
            let chapter_name = chapter.file_name().to_string_lossy().to_string();

            let title = match book_title {
                BookTitle::Static(t) => t.to_string(),
                BookTitle::Dynamic { generator, source } => generator(&chapter_name),
            };

            create_main_tex(&chapter_path, &title, author_solns)?;
        }
    }
    Ok(())
}
