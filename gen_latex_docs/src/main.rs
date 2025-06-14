mod gen_latex;
use gen_latex::{BookTitle, ProjectParameters, create_project};

fn main() -> std::io::Result<()> {
    create_project(ProjectParameters {
        book_title: BookTitle::Static("Título aletatorio para probar que esto funciona."),
        ..Default::default()
    })?;
    Ok(())
}
