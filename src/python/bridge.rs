use std::io;
use std::process::Command;

pub fn call_python_extract(input_file: &str) -> io::Result<()> {
    let status = Command::new("python3")
        .arg("python/textract/core.py")
        .arg(input_file)
        .status()?;

    if !status.success() {
        eprintln!("❌ Python script failed with exit code: {}", status);
    }

    Ok(())
}
