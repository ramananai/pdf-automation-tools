import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter

def select_files():
    files = filedialog.askopenfilenames(
        title="Select PDF files in required order",
        filetypes=[("PDF Files", "*.pdf")]
    )
    
    if files:
        file_list.delete(0, tk.END)
        for file in files:
            file_list.insert(tk.END, file)

def merge_pdfs():
    files = file_list.get(0, tk.END)

    if not files:
        messagebox.showerror("Error", "No PDF files selected!")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
        title="Save Merged PDF As"
    )

    if not save_path:
        return

    try:
        writer = PdfWriter()

        for pdf in files:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)

        with open(save_path, "wb") as output_file:
            writer.write(output_file)

        messagebox.showinfo("Success", "PDFs merged successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("PDF Merger Tool")
root.geometry("600x400")

select_button = tk.Button(root, text="Select PDF Files", command=select_files)
select_button.pack(pady=10)

merge_button = tk.Button(root, text="Merge and Save", command=merge_pdfs)
merge_button.pack(pady=10)

file_list = tk.Listbox(root, width=80)
file_list.pack(pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
