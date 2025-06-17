use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "textract")]
#[command(author = "Marcos López <marcoslm@ciencias.unam.mx>")]
#[command(version = "1.0")]
#[command(about = "PDF to LaTeX problem set generator")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Build LaTeX project from PDF
    Build {
        /// Path to the input PDF
        input_file: PathBuf,
    },
}

