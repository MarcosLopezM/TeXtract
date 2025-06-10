__app_name__ = "textract"
__version__ = "0.1.0"

(
    SUCCESS,
    TOC_ERROR,
    FILE_ERROR,
    NAME_ERROR,
    CONTENT_ERROR,
    PARSE_ERROR,
) = range(6)

ERRORS = {
    TOC_ERROR: "Table of contents not found",
    FILE_ERROR: "File not found or unnsupported format",
    NAME_ERROR: "Invalid project name",
    CONTENT_ERROR: "Content not found",
    PARSE_ERROR: "Error parsing the file",
}
