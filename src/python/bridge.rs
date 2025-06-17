use std::io::{self};
use std::process::{Command, Stdio};

pub fn call_python_extract(input_file: &str) -> io::Result<String> {
    let output = Command::new("python3")
        .arg("python/textract/core.py")
        .arg(input_file)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()?; // This returns Result<Output, io::Error>

    if !output.status.success() {
        eprintln!(
            "❌ Python script failed:\n{}",
            String::from_utf8_lossy(&output.stderr)
        );
        return Err(io::Error::new(io::ErrorKind::Other, "Python script failed"));
    }

    // Convert stdout to string and trim
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Ok(stdout)
}
