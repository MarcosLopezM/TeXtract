// pub mod cli;
// pub mod latex;
// pub mod python;
//
// use clap::Parser;
// use cli::{Cli, Commands};
// use colored::*;
// use dialoguer::{Confirm, theme::ColorfulTheme};
// use indicatif::{ProgressBar, ProgressStyle};
// use latex::{ProjectParameters, create_project};
// use python::bridge::call_python_extract;
// use std::io;
// use std::path::PathBuf;
// use std::time::Duration;
//
// pub fn run() -> io::Result<()> {
//     let cli = Cli::parse();
//
//     match cli.command {
//         Commands::Build { input_file } => run_build(input_file)?,
//     }
//
//     Ok(())
// }
//
// fn run_build(input_file: PathBuf) -> io::Result<()> {
//     println!("📄 {} {}", "Input file:".bold(), input_file.display());
//
//     let confirm = Confirm::with_theme(&ColorfulTheme::default())
//         .with_prompt("❓ Create with default options?")
//         .default(true)
//         .interact()
//         .map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;
//
//     if !confirm {
//         println!("{}", "Aborted.".red());
//         return Ok(());
//     }
//
//     let output_folder = default_output_name(&input_file);
//     let params = ProjectParameters::default();
//
//     println!(
//         "{} Looking for {} in chapters with names {} and {}",
//         "ℹ️".blue(),
//         params.problems_name.bold(),
//         params.chs_names[0].bold(),
//         params.chs_names[1].bold()
//     );
//
//     let extract_spinner = spinner("Extracting problems from PDF...");
//     call_python_extract(input_file.to_str().unwrap())?;
//     extract_spinner.finish_with_message("✅ Extraction complete!");
//
//     println!("📂 {} {}", "Output folder:".bold(), output_folder);
//
//     let build_spinner = spinner("Generating LaTeX project...");
//     println!("📘 {} {}", "Book title:".blue(), params.book_title);
//     println!(
//         "👤 {} {}",
//         "Author of solutions:".blue(),
//         params.author_solns
//     );
//
//     create_project(params)?;
//
//     build_spinner.finish_with_message("✅ Project created!");
//     println!(
//         "✔ {} {}\n",
//         "Done! Project available at".green().bold(),
//         output_folder
//     );
//
//     Ok(())
// }
//
// fn spinner(msg: &str) -> ProgressBar {
//     let pb = ProgressBar::new_spinner();
//     pb.set_style(
//         ProgressStyle::with_template("{spinner:.cyan} {msg}")
//             .unwrap()
//             .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]),
//     );
//     pb.set_message(msg.to_string());
//     pb.enable_steady_tick(Duration::from_millis(100));
//     pb
// }
//
// fn default_output_name(input_file: &PathBuf) -> String {
//     let stem = input_file
//         .file_stem()
//         .unwrap_or_default()
//         .to_string_lossy()
//         .to_string();
//     format!("{}-Bacon", stem.replace(' ', "-"))
// }
//
