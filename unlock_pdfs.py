import os
import pikepdf
from tqdm.notebook import tqdm

# ========= USER INPUT =========
INPUT_FOLDER = r"E:\Learning\Projects\Extract Text\New folder"      # 👈 give your input folder path
OUTPUT_FOLDER = r"D:\Downloads\Personal\Studies\CA Final\Final Study Materials\ICAI Study Material\May 26\IDT Chapter Wise"  # 👈 output folder path
# ==============================

# Create output folder if not exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Collect all PDFs
pdf_files = [
    f for f in os.listdir(INPUT_FOLDER)
    if f.lower().endswith(".pdf")
]

print(f"Total PDFs found: {len(pdf_files)}")

# Progress bar loop
for file_name in tqdm(pdf_files, desc="Unlocking PDFs", unit="file"):
    input_path = os.path.join(INPUT_FOLDER, file_name)
    output_path = os.path.join(OUTPUT_FOLDER, file_name)

    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path)
    except Exception as e:
        print(f"\nSkipped ❌ {file_name} | {e}")

print("\n🎉 Done! Unrestricted PDFs saved in:")
print(OUTPUT_FOLDER)