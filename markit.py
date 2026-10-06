import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def convert_pdf_to_markdown():
    root = tk.Tk()
    root.withdraw()

    # Select PDF
    pdf_file = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not pdf_file:
        return

    # Default output name
    default_name = os.path.splitext(os.path.basename(pdf_file))[0] + ".md"

    # Ask where to save
    output_file = filedialog.asksaveasfilename(
        title="Save Markdown File",
        defaultextension=".md",
        initialfile=default_name,
        filetypes=[("Markdown Files", "*.md")]
    )

    if not output_file:
        return

    try:
        # Run MarkItDown CLI
        result = subprocess.run(
            ["markitdown", pdf_file, "-o", output_file],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            messagebox.showinfo(
                "Success",
                f"Markdown saved successfully.\n\n{output_file}"
            )
        else:
            messagebox.showerror(
                "Error",
                result.stderr or result.stdout
            )

    except FileNotFoundError:
        messagebox.showerror(
            "Error",
            "MarkItDown is not installed or not added to PATH."
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    convert_pdf_to_markdown()