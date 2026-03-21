import argparse
import os
import tabula


def convert_pdf_to_csv(input_pdf, output_csv=None):
    try:
        print(f"Reading tables from {input_pdf}...")

        # If output path not provided → generate default
        if output_csv is None:
            # base_name = os.path.splitext(os.path.basename(input_pdf))[0]
            output_csv = "../uploads/answers.txt"
            os.makedirs(os.path.dirname(output_csv), exist_ok=True)


        tabula.convert_into(input_pdf, output_csv, output_format="csv", pages='all')

        print(f"Successfully saved to {output_csv}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF tables to a CSV file.")

    parser.add_argument("input", help="Path to the input PDF file")

    # Make output optional
    parser.add_argument(
        "-o", "--output",
        help="Optional output CSV file path"
    )

    args = parser.parse_args()

    convert_pdf_to_csv(args.input, args.output)