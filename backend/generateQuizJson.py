import csv
import json
import os

# Paths (adjust if needed)
ANS_FILE = "./uploads/answers.txt"   # your parsed answer file
IMG_DIR = "./uploads/images"
OUTPUT_FILE = "./uploads/quiz.json"


def parse_answer(row):
    q_no = int(row["Q. No."])
    q_type = row["Question Type"].strip().upper()
    key = row["Key/Range"].strip()
    marks = int(row.get("Marks", 1))

    question = {
        "id": q_no,
        "type": q_type,
        "marks": marks,
        "questionImage": f"/uploads/images/Q{q_no}.png"
    }

    # MCQ
    if q_type == "MCQ":
        question["answer"] = key.strip()

    # MSQ
    elif q_type == "MSQ":
        options = [opt.strip() for opt in key.split(";") if opt.strip()]
        question["answer"] = options

    # NAT (Numerical Answer Type)
    elif q_type == "NAT":
        try:
            low, high = key.split("to")
            low = float(low.strip())
            high = float(high.strip())
            question["range"] = [low, high]
        except Exception:
            # fallback if single value
            val = float(key.strip())
            question["range"] = [val, val]

    else:
        print(f"Unknown type for Q{q_no}: {q_type}")

    return question


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

    # Sort by question ID (important)
    questions.sort(key=lambda x: x["id"])

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)

    print(f"Quiz JSON generated: {OUTPUT_FILE}")
    print(f"Total questions: {len(questions)}")


if __name__ == "__main__":
    main()