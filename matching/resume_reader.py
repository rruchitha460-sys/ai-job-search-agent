import os
from pypdf import PdfReader

RESUME_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resume.pdf")


def extract_resume_text(path=RESUME_PATH):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


if __name__ == "__main__":
    resume_text = extract_resume_text()
    print(f"Extracted {len(resume_text)} characters from resume\n")
    print(resume_text[:500])  # print first 500 chars as a preview