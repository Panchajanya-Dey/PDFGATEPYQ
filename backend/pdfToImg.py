import re
import os
import argparse

# this code converts pdf files that contains questions to series of images each containing one question
import fitz  # PyMuPDF

# # Pattern 1: Exact "Q.1" format (no spaces)
# QUESTION_RE = re.compile(r'^\s*Q\.\d+\s*$')
# # Matches: "Q.1", "Q.2", "Q.10"

# # Pattern 2: "Q.1" or "Q1" format (optional dot)
# QUESTION_RE = re.compile(r'^\s*Q\.?\d+\s*$')
# # Matches: "Q.1", "Q1", "Q.2", "Q2"

# # Pattern 3: With possible space after Q
# QUESTION_RE = re.compile(r'^\s*Q\.?\s*\d+\s*$')
# # Matches: "Q.1", "Q1", "Q. 1", "Q 1"

# # Pattern 4: Case insensitive (q.1, q1)
# QUESTION_RE = re.compile(r'^\s*[Qq]\.?\s*\d+\s*$')
# # Matches: "Q.1", "q.1", "Q1", "q1"

# Pattern 5: If there might be text after (like "Q.1 What is...")
QUESTION_RE = re.compile(r'^\s*[Qq]\.?\s*\d+')  # Remove $ at the end
# Matches start of line with Q.1 even if more text follows

def find_question_tops(page):
    """
    Return a sorted list of y-coordinates (in PDF points) where questions start on the page.
    We detect lines whose first word is a question number like '1.' or '2)'.
    """
    words = page.get_text("words")  # list of tuples: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
    # group words by (block_no, line_no)
    lines = {}
    for x0, y0, x1, y1, w, b, ln, wn in words:
        lines.setdefault((b, ln), []).append((wn, w, x0, y0, x1, y1))
    tops = []
    for key, items in lines.items():
        items.sort(key=lambda t: t[0])  # sort by word_no
        first_word = items[0][1]
        third_word = None
        if len(items) >= 3:
            third_word = items[2][1]
        if QUESTION_RE.match(first_word) and not (third_word and QUESTION_RE.match(third_word)):
            # take the minimum y0 of the words in the line as the line's top
            line_y0 = min(it[3] for it in items)
            tops.append((line_y0, first_word))
    tops.sort(key = lambda i: i[0])
    return tops

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def split_questions_from_pdf(pdf_path, out_dir=None, zoom=2.0, padding_pts=4.0):
    """
    Splits each page of pdf_path into separate images per question label (1,2,...).
    - out_dir: directory where images will be saved. Defaults to <pdf_basename>_questions in same folder.
    - zoom: rendering scale factor (1.0 = 72 DPI). Use >1 for higher resolution.
    - padding_pts: small padding in PDF points added above/below each question region.
    """
    doc = fitz.open(pdf_path)
    if out_dir is None:
        # base = os.path.splitext(os.path.basename(pdf_path))[0]
        # out_dir = os.path.join(os.path.dirname(pdf_path), f"{base}_questions")
        out_dir = "../uploads/images"
    ensure_dir(out_dir)

    mat = fitz.Matrix(zoom, zoom)
    saved = 0

    for pno in range(len(doc)):
        page = doc[pno]
        tops = find_question_tops(page)

        if not tops:
            # no explicit question markers found: save whole page as one image
            clip = page.rect
            pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
            outname = os.path.join(out_dir, f"page_{pno+1:03d}_whole.png")
            pix.save(outname)
            saved += 1
            continue

        # compute cropping rectangles between successive question tops
        page_height = page.rect.y1
        regions = []
        for i, top in enumerate(tops):
            top_clamped = max(0.0, top[0] - padding_pts)
            if i + 1 < len(tops):
                bottom = tops[i + 1][0] - padding_pts
            else:
                bottom = page_height - padding_pts
            bottom_clamped = min(page_height, bottom)
            if bottom_clamped > top_clamped + 1e-3:
                regions.append((top[1], top_clamped, bottom_clamped))

        # render each region
        for qi, top, bottom in regions:
            clip = fitz.Rect(0.0, top, page.rect.width, bottom)
            pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
            # outname = os.path.join(out_dir, f"p{pno+1:03d}_q{qi:03d}.png")
            outname = os.path.join(out_dir, f"{qi}.png")
            pix.save(outname)
            saved += 1

    doc.close()
    return saved

def main():
    parser = argparse.ArgumentParser(description="Split PDF page questions into separate images using PyMuPDF.")
    parser.add_argument("pdf", help="Input PDF file")
    parser.add_argument("-o", "--out", help="Output directory (optional). Defaults to <pdf_basename>_questions", default=None)
    parser.add_argument("-z", "--zoom", type=float, help="Render scale (default 2.0). Increase for higher resolution.", default=2.0)
    parser.add_argument("-p", "--padding", type=float, help="Vertical padding in PDF points around question regions (default 4.0).", default=4.0)
    args = parser.parse_args()

    saved = split_questions_from_pdf(args.pdf, out_dir=args.out, zoom=args.zoom, padding_pts=args.padding)
    print(f"Saved {saved} images.")

if __name__ == "__main__":
    main()