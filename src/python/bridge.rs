use std::io::{self};
use std::process::{Command, Stdio};

pub fn call_python_extract(input_file: &str) -> io::Result<String> {
    let output = Command::new("python3")
        .arg("python/textract/core.py")
        .arg(input_file)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()?;

    if !output.status.success() {
        eprintln!(
            "❌ Python script failed:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );

        return Err(io::Error::other("Python script failed"));
    }

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Ok(stdout)
}
pub fn call_python_extract_w_dir(input_file: &str, out_dir: &str) -> io::Result<String> {
    let output = Command::new("python3")
        .arg("python/textract/core.py")
        .arg(input_file)
        .arg("--out_dir")
        .arg(out_dir)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()?;

    if !output.status.success() {
        eprintln!(
            "❌ Python script failed:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );

        return Err(io::Error::other("Python script failed"));
    }

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Ok(stdout)
}
