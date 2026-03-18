import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io

def create_overlay(page_width, page_height, text, font_size, position, align, margin_left, margin_right):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Y position
    if position == "top":
        y = page_height - (font_size + 10)
    else:
        y = font_size + 10

    # X position
    if align == "left":
        x = margin_left
    elif align == "right":
        x = page_width - margin_right
    else:
        x = page_width / 2

    # Bold font
    can.setFont("Helvetica-Bold", font_size)

    if align == "center":
        can.drawCentredString(x, y, text)
    elif align == "right":
        can.drawRightString(x, y, text)
    else:
        can.drawString(x, y, text)

    can.save()
    packet.seek(0)

    return PdfReader(packet)

def process_pdf():
    try:
        file = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not file:
            return

        reader = PdfReader(file)
        writer = PdfWriter()

        # Inputs
        font_size = simpledialog.askinteger("Font Size", "Enter font size:", initialvalue=14)
        position = simpledialog.askstring("Position", "Enter position (top/bottom):").lower()
        align = simpledialog.askstring("Alignment", "Enter alignment (left/center/right):").lower()
        margin_left = simpledialog.askinteger("Left Margin", "Left margin:", initialvalue=30)
        margin_right = simpledialog.askinteger("Right Margin", "Right margin:", initialvalue=30)

        if not all([font_size, position, align, margin_left, margin_right]):
            messagebox.showerror("Error", "All inputs required!")
            return

        for i, page in enumerate(reader.pages):
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            text = f"Page No: {i+1}"

            overlay_pdf = create_overlay(
                page_width, page_height,
                text,
                font_size,
                position,
                align,
                margin_left,
                margin_right
            )

            overlay_page = overlay_pdf.pages[0]
            page.merge_page(overlay_page)
            writer.add_page(page)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF As"
        )

        if not save_path:
            return

        with open(save_path, "wb") as f:
            writer.write(f)

        messagebox.showinfo("Success", "PDF Created Successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI
root = tk.Tk()
root.title("PDF Page Number Tool")
root.geometry("400x200")

btn = tk.Button(root, text="Select PDF & Add Page Numbers", command=process_pdf)
btn.pack(expand=True)

root.mainloop()