import csv
import json
import os
import sys
import re

# ===== Read column mappings from CLI =====
col_qno = sys.argv[1]
col_type = sys.argv[2]
col_key = sys.argv[3]
col_marks = sys.argv[4] if len(sys.argv) > 4 else ""

# Normalize column names (lowercase for matching)
col_qno_l = col_qno.strip().lower()
col_type_l = col_type.strip().lower()
col_key_l = col_key.strip().lower()
col_marks_l = col_marks.strip().lower() if col_marks else ""

# ===== Paths =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ANS_FILE = os.path.join(BASE_DIR, "uploads", "answers.txt")
IMG_DIR = os.path.join(BASE_DIR, "uploads", "images")
OUTPUT_FILE = os.path.join(BASE_DIR, "uploads", "quiz.json")


# ===== Helper: normalize CSV row keys =====
def normalize_row(row):
    return {k.strip().lower(): v for k, v in row.items()}


# ===== Parse each row =====
def parse_answer(row):
    row = normalize_row(row)

    # Validate required columns
    if col_qno_l not in row:
        raise ValueError(f"Column '{col_qno}' not found. Available: {list(row.keys())}")
    if col_type_l not in row:
        raise ValueError(f"Column '{col_type}' not found. Available: {list(row.keys())}")
    if col_key_l not in row:
        raise ValueError(f"Column '{col_key}' not found. Available: {list(row.keys())}")

    # Extract values
    q_no = int(row[col_qno_l])
    q_type = row[col_type_l].strip().upper()
    key = row[col_key_l].strip()

    # Marks (optional)
    if col_marks_l and col_marks_l in row:
        try:
            marks = int(row[col_marks_l])
        except Exception:
            marks = 1
    else:
        marks = 1

    # Image path
    img_path = os.path.join(IMG_DIR, f"Q.{q_no}.png")
    if not os.path.exists(img_path):
        print(f"Warning: Image not found for Q{q_no}")

    question = {
        "id": q_no,
        "type": q_type,
        "marks": marks,
        "questionImage": f"/uploads/images/Q.{q_no}.png"
    }

    # ===== MCQ =====
    if q_type == "MCQ":
        question["answer"] = key.strip()

    # ===== MSQ =====
    elif q_type == "MSQ":
        options = re.split(r"[;, ]+", key)
        options = [opt.strip() for opt in options if opt.strip()]
        question["answer"] = options

    # ===== NAT =====
    elif q_type == "NAT":
        try:
            key_clean = key.replace("–", "-").lower()

            # Match formats: "1.05-1.15", "1.05 to 1.15"
            match = re.match(r"([\d\.]+)\s*(?:-|to)\s*([\d\.]+)", key_clean)

            if match:
                low = float(match.group(1))
                high = float(match.group(2))
                question["range"] = [low, high]
            else:
                val = float(key_clean.strip())
                question["range"] = [val, val]

        except Exception:
            print(f"Invalid NAT format for Q{q_no}: {key}")

    else:
        print(f"Unknown type for Q{q_no}: {q_type}")

    return question


# ===== Main =====
def main():
    questions = []

    if not os.path.exists(ANS_FILE):
        print("Answer file not found!")
        return

    with open(ANS_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                q = parse_answer(row)
                questions.append(q)
            except Exception as e:
                print(f"Skipping row due to error: {e}")

    # Sort by question ID
    questions.sort(key=lambda x: x["id"])

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)

    print(f"Quiz JSON generated: {OUTPUT_FILE}")
    print(f"Total questions: {len(questions)}")


if __name__ == "__main__":
    main()