mod latex;
mod python;
use crate::latex::{ProjectParameters, create_project};
use crate::python::bridge::{call_python_extract, call_python_extract_w_dir};
// use anyhow::Result;
use clap::{Parser, Subcommand};
use colored::*;
use dialoguer::{Confirm, theme::ColorfulTheme};
use indicatif::{ProgressBar, ProgressStyle};
use std::path::{Path, PathBuf};
use std::time::Duration;

#[derive(Parser)]
#[command(name = "textract")]
#[command(author = "Marcos López <marcoslm@ciencias.unam.mx>")]
#[command(version = "1.0")]
#[command(about = "PDF to LaTeX problem set generator")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Build LaTeX project from PDF
    Build {
        /// Path to the input PDF
        input_file: PathBuf,
    },
}

fn main() -> std::io::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Build { input_file } => run_build(input_file)?,
    }

    Ok(())
}

fn run_build(input_file: PathBuf) -> std::io::Result<()> {
    println!("📄 {} {}", "Input file:".bold(), input_file.display());

    let confirm = Confirm::with_theme(&ColorfulTheme::default())
        .with_prompt("❓ Create with default options?")
        .default(true)
        .interact()
        .map_err(std::io::Error::other)?;

    // let output_folder = call_python_extract(input_file.to_str().unwrap())?;
    let output_folder: String;

    let params: ProjectParameters = if confirm {
        output_folder = call_python_extract(input_file.to_str().unwrap())?;

        ProjectParameters {
            base_dir: Path::new(&output_folder),
            ..ProjectParameters::default()
        }
    } else {
        println!("{}", "🛠 Enter custom project parameters:".yellow());

        let custom_out: String = dialoguer::Input::new()
            .with_prompt("📁 Output folder name")
            .default("Output".into())
            .interact_text()
            .map_err(std::io::Error::other)?;

        output_folder = call_python_extract_w_dir(input_file.to_str().unwrap(), &custom_out)?;

        let book_title_input: String = dialoguer::Input::new()
            .with_prompt("📘 Book title")
            .interact_text()
            .map_err(std::io::Error::other)?;

        let book_title = latex::BookTitle::Static(Box::leak(book_title_input.into_boxed_str()));

        let author_solns: String = dialoguer::Input::new()
            .with_prompt("👤 Author of solutions")
            .default("Chris P. Bacon".into())
            .interact_text()
            .map_err(std::io::Error::other)?;

        let ch1: String = dialoguer::Input::new()
            .with_prompt("🔹 Name of first chapter group (e.g. Part)")
            .default("Part".into())
            .interact_text()
            .map_err(std::io::Error::other)?;

        let ch2: String = dialoguer::Input::new()
            .with_prompt("🔸 Name of second chapter group (e.g. Appendices)")
            .default("Appendices".into())
            .interact_text()
            .map_err(std::io::Error::other)?;

        let problems_name: String = dialoguer::Input::new()
            .with_prompt("📎 Section name for problems")
            .default("Problems".into())
            .interact_text()
            .map_err(std::io::Error::other)?;

        ProjectParameters {
            base_dir: Path::new(&output_folder),
            book_title,
            author_solns: Box::leak(author_solns.into_boxed_str()),
            chs_names: vec![ch1, ch2],
            problems_name,
        }
    };

    println!(
        "{} Looking for {} in chapters with names {} and {}",
        "ℹ️".blue(),
        params.problems_name.bold(),
        params.chs_names[0].bold(),
        params.chs_names[1].bold()
    );

    let extract_spinner = spinner("Extracting problems from PDF...");
    extract_spinner.finish_with_message("✅ Extraction complete!");

    println!(
        "{} {} {}",
        "📂".blue(),
        "Output folder:".bold(),
        output_folder
    );

    let build_spinner = spinner("Generating LaTeX project...");
    println!("{} Book title: {}", "📘".blue(), params.book_title);
    println!(
        "{} Author of solutions: {}",
        "👤".blue(),
        params.author_solns
    );

    create_project(params)?;

    build_spinner.finish_with_message("✅ Project created!");

    println!(
        "{} {}\n",
        "✔ Done! Project available at".green().bold(),
        output_folder
    );

    Ok(())
}

fn spinner(msg: &str) -> ProgressBar {
    let pb = ProgressBar::new_spinner();
    pb.set_style(
        ProgressStyle::with_template("{spinner:.cyan} {msg}")
            .unwrap()
            .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
    );
    pb.set_message(msg.to_string());
    pb.enable_steady_tick(Duration::from_millis(100));
    pb
}
