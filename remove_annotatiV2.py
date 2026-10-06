import tkinter as tk
from tkinter import filedialog, messagebox
import fitz
import os


def remove_pdf_links():

    # Browse and select PDF
    pdf_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not pdf_path:
        return

    try:
        # Open PDF
        doc = fitz.open(pdf_path)

        total_removed = 0

        # Remove all link annotations
        for page in doc:
            links = page.get_links()

            for link in links:
                page.delete_link(link)
                total_removed += 1

        # Save in SAME LOCATION
        folder = os.path.dirname(pdf_path)
        filename = os.path.basename(pdf_path)

        name, extension = os.path.splitext(filename)

        output_path = os.path.join(
            folder,
            f"{name}_no_links{extension}"
        )

        # Save cleaned PDF
        doc.save(output_path)
        doc.close()

        messagebox.showinfo(
            "Completed",
            f"Links removed: {total_removed}\n\n"
            f"Saved here:\n{output_path}"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )


# ---------------- GUI ----------------

root = tk.Tk()
root.title("PDF Link Remover")
root.geometry("450x220")
root.resizable(False, False)

title = tk.Label(
    root,
    text="PDF Link Remover",
    font=("Arial", 18, "bold")
)
title.pack(pady=30)

select_button = tk.Button(
    root,
    text="BROWSE PDF & REMOVE LINKS",
    command=remove_pdf_links,
    font=("Arial", 12, "bold"),
    padx=20,
    pady=12
)
select_button.pack()

root.mainloop()