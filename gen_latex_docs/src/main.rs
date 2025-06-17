mod gen_latex;
use gen_latex::{ProjectParameters, create_project};

fn main() -> std::io::Result<()> {
    create_project(ProjectParameters::default())?;
    Ok(())
}
