mod gen_latex;
use std::path::Path;
use walkdir::WalkDir;

fn main() -> std::io::Result<()> {
    // let base_dir = Path::new("Schwartz_problems");
    //
    // gen_latex::create_main_tex(
    //     base_dir,
    //     "Quantum Field Theory and the Standard Model",
    //     "Yo merengues",
    // )?;
    //
    // Ok(())
    let parent_dir = Path::new(".");

    for entry in WalkDir::new(parent_dir)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_dir())
    {
        let path = entry.path();
        if let Some(folder_name) = path.file_name().and_then(|n| n.to_str()) {
            if let Some(stripped) = folder_name.strip_suffix("_problems") {
                let title = stripped.replace('_', " ");
                gen_latex::create_main_tex(path, &title, "Yo merengues")?;
            }
        }
    }

    Ok(())
}
