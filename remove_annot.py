import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox

def remove_links_from_pdf(input_path, output_path):
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        links = page.get_links()

        for link in links:
            try:
                page.delete_link(link)
            except Exception as e:
                print(f"Error removing link on page {page_num + 1}: {e}")

    doc.save(output_path)
    doc.close()

def main():
    root = tk.Tk()
    root.withdraw()

    # Select input PDF
    input_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not input_path:
        messagebox.showwarning("No file", "No PDF selected.")
        return

    # Select save location
    output_path = filedialog.asksaveasfilename(
        title="Save cleaned PDF as",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
        initialfile="cleaned_output.pdf"
    )

    if not output_path:
        messagebox.showwarning("No location", "No save location selected.")
        return

    # Process PDF
    remove_links_from_pdf(input_path, output_path)

    messagebox.showinfo("Success", "All clickable links removed successfully!")

if __name__ == "__main__":
    main()