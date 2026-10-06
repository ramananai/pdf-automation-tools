import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from pypdf import PdfReader, PdfWriter

def unlock_pdf():
    # Hide main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Ask user to select PDF file
    file_path = filedialog.askopenfilename(
        title="Select Locked PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    # Ask for password
    password = simpledialog.askstring(
        "Password Required",
        "Enter PDF Password:",
        show='*'
    )

    if password is None:
        messagebox.showerror("Error", "No password entered.")
        return

    try:
        reader = PdfReader(file_path)

        # Try decrypting
        if reader.is_encrypted:
            reader.decrypt(password)
        else:
            messagebox.showinfo("Info", "PDF is not encrypted.")
            return

        writer = PdfWriter()

        # Add all pages to writer
        for page in reader.pages:
            writer.add_page(page)

        # Create new filename
        directory = os.path.dirname(file_path)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        new_file_path = os.path.join(directory, f"{filename}_unlocked.pdf")

        # Save unlocked file
        with open(new_file_path, "wb") as f:
            writer.write(f)

        messagebox.showinfo("Success", f"Unlocked PDF saved as:\n{new_file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to unlock PDF.\n\n{str(e)}")

if __name__ == "__main__":
    unlock_pdf()
