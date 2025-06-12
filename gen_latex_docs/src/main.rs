use rusttex::{ContentBuilder, DocumentClass, options};
use std::fs;
use std::fs::File;
use std::io::Write;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

fn write_file<P: AsRef<Path>>(path: P, content: &str) -> std::io::Result<()> {
    let mut file = File::create(path)?;
    file.write_all(content.as_bytes())
}

fn create_preamble(base_dir: &Path) -> std::io::Result<()> {
    let content = r#"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                                                           %
%           Common Preamble: Math & Science Documents       %
%                                                           %
%  Purpose: Reusable set of packages for papers involving   %
%           mathematics, physics, or technical content.     %
%                                                           %
%  Usage: \input{preamble.tex}  (from main .tex file)       %
%                                                           %
%  Author: Marcos López Merino                              %
%  Date:    2025-06-11                                      %
%                                                           %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% ============= Encoding and Language ============ %
\usepackage[utf8]{inputenc} % UTF-8 encoding
\usepackage[T1]{fontenc} % Output font encoding
\usepackage[english]{babel} % Language support

% ============= Math Packages ============== %
\usepackage{amsmath, amssymb, amsfonts}
\usepackage{mathtools} % For advanced math typesetting
\usepackage{bm} % For bold math symbols
\usepackage{derivative} % For derivatives
\usepackage{lualatex-math} % For LuaLaTeX math support
\usepackage{empheq} % For enhanced equation environments
\usepackage{nicematrix} % For nice matrices
\usepackage{simples-matrices} % Fast matrix typesetting

% ============= Physics Packages ============ %
% \usepackage{phfqit} % BraKet notation for QM and Quantum Information Theory
% \usepackage{siunitx} % For SI units and scientific notation

% ============= Graphics and Figures ============ %
\usepackage{graphicx} % For including images
\usepackage{subcaption} % For subfigures

% ============= Fonts and Typography ============ %
\usepackage{microtype} % Better typography
\usepackage{csquotes} % Context-sensitive quotes
\usepackage{fontspec} % Font selection for XeLaTeX and LuaLaTeX

% ============= Miscellaneous ============ %
\usepackage{enumitem} % Customizable lists
\usepackage{xcolor} % Color support
\usepackage{kantlipsum} % Dummy text for testing
\usepackage{datetime2} % Date and time formatting
\setlength{\jot}{10pt} % Space between lines in equations
\allowdisplaybreaks % Allow page breaks in equations

% ============= Hyperlinks and References ============ %
\usepackage{hyperref} % Hyperlinks in the document
\usepackage{zref-clever} % Clever references"#;
    write_file(base_dir.join("preamble.tex"), content)
}

fn create_main_tex(base_dir: &Path, title_book: &str, author_sol: &str) -> std::io::Result<()> {
    let mut builder = ContentBuilder::new();
    builder.add_literal("%! TeX program = lualatex\n");
    builder.set_document_class(DocumentClass::Book, options![]);
    builder.use_package("subfiles", options![]);
    builder.add_literal("\\input{preamble.tex}\n");
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
        let chapter_name = chapter.file_name().to_string_lossy().replace('_', " ");
        let chapter_path = chapter.path();

        if chapter_name.contains("Appendix") {
            continue;
        }

        builder.add_literal(&format!("\\chapter{{{}}}\n", chapter_name));

        let mut sections: Vec<PathBuf> = fs::read_dir(&chapter_path)?
            .filter_map(|e| e.ok())
            .filter(|e| e.path().is_dir())
            .map(|e| e.path())
            .collect();

        sections.sort();

        for section in &sections {
            let subfile_rel_path = section.strip_prefix(base_dir).unwrap().join("problems.tex");
            let subfile_str = subfile_rel_path.to_string_lossy().replace("\\", "/");
            builder.add_literal(&format!("\\subfile{{\"{}\"}}\n", subfile_str));
        }
    }

    // Appendices al final
    for chapter in &chapters {
        let chapter_name = chapter.file_name().to_string_lossy().replace('_', " ");
        if !chapter_name.contains("Appendix") {
            continue;
        }

        builder.add_literal(&format!("\\chapter{{{}}}\n", chapter_name));

        let mut sections: Vec<PathBuf> = fs::read_dir(chapter.path())?
            .filter_map(|e| e.ok())
            .filter(|e| e.path().is_dir())
            .map(|e| e.path())
            .collect();

        sections.sort();

        for section in &sections {
            let subfile_rel_path = section.strip_prefix(base_dir).unwrap().join("problems.tex");
            let subfile_str = subfile_rel_path.to_string_lossy().replace("\\", "/");
            builder.add_literal(&format!("\\subfile{{\"{}\"}}\n", subfile_str));
        }
    }

    builder.end_document();
    let latex = builder.build_document();
    write_file(base_dir.join("main.tex"), &latex)
}

fn create_subfile_tex(folder: &Path) -> std::io::Result<()> {
    let mut builder = ContentBuilder::new();
    builder.set_document_class(
        DocumentClass::Custom("subfiles".to_string()),
        options!["../main"],
    );
    // builder.add_literal("\\input{preamble.tex}\n");
    builder.add_literal("\\graphicspath{{figs/}}\n");
    builder.begin_document();
    builder.section("Problemas");
    builder.add_literal("\\kant[1-2]");
    builder.end_document();
    let latex = builder.build_document();
    let subfile_path = folder.join("problems.tex");
    write_file(&subfile_path, &latex)
}

fn main() -> std::io::Result<()> {
    let base_dir = Path::new("Schwartz_problems");

    if !base_dir.starts_with("figs") {
        // Create common.sty and main.tex at base_dir
        create_preamble(base_dir)?;

        // Iterate directories at depth 2 relative to base_dir and create problems.tex
        for entry in WalkDir::new(base_dir)
            .min_depth(2)
            .max_depth(2)
            .into_iter()
            .filter_map(Result::ok)
            .filter(|e| e.file_type().is_dir())
        {
            let path = entry.path();
            println!("Creating problems.tex in {:?}", path);
            create_subfile_tex(path)?;
        }

        create_main_tex(
            base_dir,
            "Quantum Field Theory and the Standard Model",
            "Yo merengues",
        )?;
    }

    Ok(())
}
