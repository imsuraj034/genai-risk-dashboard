"""
Builds the final report: DOCX -> PDF (LibreOffice), reads the real page of each chapter from the PDF,
rebuilds the DOCX with those Table-of-Contents page numbers, exports the final PDF and verifies them.
Run:  python report/make_pdf.py [--github URL] [--render OUTDIR]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pypdf

HERE = Path(__file__).parent
DOCX = HERE / "AAT_Report_Suraj_T_1DS23AI058.docx"
PDF = DOCX.with_suffix(".pdf")
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
PAGES = HERE / "pages.json"
extra = []
if "--github" in sys.argv:
    extra = ["--github", sys.argv[sys.argv.index("--github") + 1]]


def build(with_pages):
    args = [sys.executable, str(HERE / "build_aat_report.py")] + extra + (["--pages", str(PAGES)] if with_pages else [])
    subprocess.run(args, check=True)
    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(HERE), str(DOCX)],
                   check=True, capture_output=True)


def chapter_pages():
    pages = {}
    reader = pypdf.PdfReader(PDF)
    for i, page in enumerate(reader.pages, 1):
        for n, _ in re.findall(r"^\s*(\d{1,2})\. ([A-Z][A-Z /–&-]{4,})\s*$", page.extract_text(), re.M):
            pages.setdefault(f"ch{n}", i)
    return pages, len(reader.pages)


build(False)
p1, _ = chapter_pages()
PAGES.write_text(json.dumps(p1))
build(True)
p2, total = chapter_pages()
assert p1 == p2 and len(p2) == 10, f"TOC pages unstable or missing: {p1} vs {p2}"
print(f"Final PDF: {PDF} | {total} pages | chapters at {p2}")

if "--render" in sys.argv:
    import pypdfium2 as pdfium
    from PIL import Image
    out = Path(sys.argv[sys.argv.index("--render") + 1])
    out.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(PDF))
    imgs = [doc[i].render(scale=1.1).to_pil() for i in range(len(doc))]
    for k in range(0, len(imgs), 4):
        grp = imgs[k:k + 4]
        w, h = grp[0].size
        sheet = Image.new("RGB", (w * 2, h * 2), "white")
        for j, im in enumerate(grp):
            sheet.paste(im, ((j % 2) * w, (j // 2) * h))
        sheet.save(out / f"final_{k // 4 + 1:02d}.png")
