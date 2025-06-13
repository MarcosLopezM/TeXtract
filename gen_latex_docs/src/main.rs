mod gen_latex;
use std::path::Path;

fn main() -> std::io::Result<()> {
    let base_dir = Path::new("Schwartz_problems");

    gen_latex::create_main_tex(
        base_dir,
        "Quantum Field Theory and the Standard Model",
        "Yo merengues",
    )?;

    Ok(())
}
