import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

image_files = []

A4_WIDTH, A4_HEIGHT = A4

def select_images():
    global image_files

    image_files = filedialog.askopenfilenames(
        title="Select Images in Required Order",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")
        ]
    )

    listbox.delete(0, tk.END)

    for file in image_files:
        listbox.insert(tk.END, file)

def convert_to_pdf():
    if not image_files:
        messagebox.showerror("Error", "Please select images.")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not save_path:
        return

    try:
        c = canvas.Canvas(save_path, pagesize=A4)

        # 0.5 cm border
        border_margin = 14.17  # points

        for img_path in image_files:

            img = Image.open(img_path)
            img_width, img_height = img.size

            available_width = A4_WIDTH - (2 * border_margin)
            available_height = A4_HEIGHT - (2 * border_margin)

            scale = min(
                available_width / img_width,
                available_height / img_height
            )

            new_width = img_width * scale
            new_height = img_height * scale

            x = (A4_WIDTH - new_width) / 2
            y = (A4_HEIGHT - new_height) / 2

            # Draw black border
            c.rect(
                border_margin,
                border_margin,
                A4_WIDTH - (2 * border_margin),
                A4_HEIGHT - (2 * border_margin)
            )

            c.drawImage(
                img_path,
                x,
                y,
                width=new_width,
                height=new_height
            )

            c.showPage()

        c.save()

        messagebox.showinfo(
            "Success",
            f"PDF created successfully:\n{save_path}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Images to A4 PDF")
root.geometry("700x450")

tk.Button(
    root,
    text="Browse Images",
    command=select_images
).pack(pady=10)

listbox = tk.Listbox(root, width=100, height=15)
listbox.pack(padx=10, pady=10)

tk.Button(
    root,
    text="Convert to PDF",
    command=convert_to_pdf
).pack(pady=10)

root.mainloop()