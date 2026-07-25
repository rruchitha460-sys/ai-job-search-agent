import os
from pypdf import PdfReader

RESUME_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resume.pdf")


def extract_resume_text(path_or_file=None):
    """
    Extract text from a resume PDF.
    - If path_or_file is None, falls back to the local resume.pdf (CLI/testing use).
    - If path_or_file is a file path (str), reads from disk.
    - If path_or_file is a file-like object (e.g. Streamlit's uploaded_file), reads directly from memory.
    """
    source = path_or_file if path_or_file is not None else RESUME_PATH
    reader = PdfReader(source)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


if __name__ == "__main__":
    resume_text = extract_resume_text()
    print(f"Extracted {len(resume_text)} characters from resume\n")
    print(resume_text[:500])