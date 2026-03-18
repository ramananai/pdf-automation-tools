import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pypdf import PdfReader, PdfWriter

def select_file():
    file = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file:
        file_path.set(file)

def parse_pages(pages_str, total_pages):
    pages_to_remove = set()

    try:
        parts = pages_str.split(',')

        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                for i in range(start, end + 1):
                    pages_to_remove.add(i - 1)  # zero index
            else:
                pages_to_remove.add(int(part) - 1)

        # remove invalid pages
        pages_to_remove = {p for p in pages_to_remove if 0 <= p < total_pages}

        return pages_to_remove

    except:
        return None

def remove_pages():
    file = file_path.get()

    if not file:
        messagebox.showerror("Error", "Please select a PDF file!")
        return

    try:
        reader = PdfReader(file)
        total_pages = len(reader.pages)

        pages_str = simpledialog.askstring(
            "Remove Pages",
            f"Enter pages to remove (e.g., 2,5,7-10)\nTotal pages: {total_pages}"
        )

        if not pages_str:
            return

        pages_to_remove = parse_pages(pages_str, total_pages)

        if pages_to_remove is None:
            messagebox.showerror("Error", "Invalid page format!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save New PDF As"
        )

        if not save_path:
            return

        writer = PdfWriter()

        for i in range(total_pages):
            if i not in pages_to_remove:
                writer.add_page(reader.pages[i])

        with open(save_path, "wb") as output_file:
            writer.write(output_file)

        messagebox.showinfo("Success", "Pages removed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("PDF Page Remover")
root.geometry("500x200")

file_path = tk.StringVar()

select_button = tk.Button(root, text="Select PDF", command=select_file)
select_button.pack(pady=10)

file_label = tk.Label(root, textvariable=file_path, wraplength=400)
file_label.pack(pady=5)

remove_button = tk.Button(root, text="Remove Pages and Save", command=remove_pages)
remove_button.pack(pady=20)

root.mainloop()