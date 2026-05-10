import fitz
import re


def extract_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype = "pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    return text

def extract_claim(text):
    patterns = [ r'.*\d+%.*', r'.\$\d+.*', r'.\d{4}.*', r'.*\d\s?(million|billion|trillion).*']

    claims = []
    lines = text.split('\n')

    for line in lines:
        clean_line = line.strip()

        if len(clean_line) < 15:
            continue

        for patterns in patterns:
            if re.search(pattern, clean_line, re.IGNORECASE):
                claims.append(clean_line)
                break
    
    return list(set(claims))