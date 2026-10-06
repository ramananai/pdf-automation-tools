import os
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF
from PIL import Image


def flatten_pdf_to_image_pdf(input_pdf):
    try:
        # ---------------------------------------------------------
        # Open original PDF
        # ---------------------------------------------------------
        source = fitz.open(input_pdf)

        if source.page_count == 0:
            raise Exception("The selected PDF has no pages.")

        # ---------------------------------------------------------
        # Output filename
        # ---------------------------------------------------------
        folder = os.path.dirname(input_pdf)
        filename = os.path.basename(input_pdf)

        name, ext = os.path.splitext(filename)

        output_pdf = os.path.join(
            folder,
            f"{name}_flattened{ext}"
        )

        # ---------------------------------------------------------
        # Create completely new PDF
        # ---------------------------------------------------------
        output = fitz.open()

        # ---------------------------------------------------------
        # Render quality
        #
        # 300 DPI gives very good quality.
        # 400 DPI gives higher quality but larger file.
        # ---------------------------------------------------------
        DPI = 300

        zoom = DPI / 72

        matrix = fitz.Matrix(zoom, zoom)

        for page_number in range(source.page_count):

            print(
                f"Processing page "
                f"{page_number + 1} / {source.page_count}"
            )

            page = source.load_page(page_number)

            # -----------------------------------------------------
            # Render ONLY the visual appearance of the page
            #
            # This does NOT preserve:
            # - hyperlinks
            # - annotations
            # - JavaScript
            # - forms
            # - buttons
            # - actions
            # - widgets
            # - embedded interactive elements
            # -----------------------------------------------------
            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            # Convert rendered page into PIL image
            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            # Save temporary image
            temp_image = os.path.join(
                folder,
                f"__temp_pdf_page_{page_number}.png"
            )

            image.save(
                temp_image,
                format="PNG"
            )

            # -----------------------------------------------------
            # Create a new PDF page with the exact image dimensions
            # -----------------------------------------------------
            new_page = output.new_page(
                width=pixmap.width,
                height=pixmap.height
            )

            # Insert image covering the ENTIRE page
            new_page.insert_image(
                fitz.Rect(
                    0,
                    0,
                    pixmap.width,
                    pixmap.height
                ),
                filename=temp_image
            )

            # Delete temporary image immediately
            try:
                os.remove(temp_image)
            except Exception:
                pass

        # ---------------------------------------------------------
        # Save completely new PDF
        # ---------------------------------------------------------
        output.save(
            output_pdf,
            garbage=4,
            deflate=True,
            clean=True
        )

        output.close()
        source.close()

        # ---------------------------------------------------------
        # Final verification
        # ---------------------------------------------------------
        verify_pdf = fitz.open(output_pdf)

        clickable_found = False

        for page in verify_pdf:
            # Check links
            if page.get_links():
                clickable_found = True
                break

            # Check annotations
            if page.first_annot():
                clickable_found = True
                break

            # Check widgets
            if page.first_widget():
                clickable_found = True
                break

        verify_pdf.close()

        # ---------------------------------------------------------
        # Result
        # ---------------------------------------------------------
        if clickable_found:
            messagebox.showwarning(
                "Warning",
                "The PDF was recreated, but an interactive "
                "element was detected during verification."
            )
        else:
            messagebox.showinfo(
                "Completed",
                "PDF recreated successfully.\n\n"
                "All pages were rendered as images and rebuilt "
                "into a completely new PDF.\n\n"
                "No links, annotations or widgets were detected.\n\n"
                f"Output:\n{output_pdf}"
            )

        print()
        print("==============================================")
        print("PDF RECREATION COMPLETED")
        print("==============================================")
        print(f"Pages processed : {source.page_count}")
        print(f"DPI             : {DPI}")
        print(f"Output          : {output_pdf}")
        print(f"Clickable items : {clickable_found}")
        print("==============================================")

    except Exception as e:

        # Try cleaning temporary files
        try:
            for file in os.listdir(folder):
                if file.startswith("__temp_pdf_page_"):
                    try:
                        os.remove(
                            os.path.join(folder, file)
                        )
                    except Exception:
                        pass
        except Exception:
            pass

        messagebox.showerror(
            "Error",
            f"Failed to recreate PDF.\n\n{str(e)}"
        )


def main():

    root = tk.Tk()
    root.withdraw()

    # ---------------------------------------------------------
    # Select PDF
    # ---------------------------------------------------------
    input_pdf = filedialog.askopenfilename(
        title="Select PDF to Remove All Links",
        filetypes=[
            ("PDF Files", "*.pdf"),
            ("All Files", "*.*")
        ]
    )

    if not input_pdf:
        return

    # ---------------------------------------------------------
    # Process
    # ---------------------------------------------------------
    flatten_pdf_to_image_pdf(input_pdf)


if __name__ == "__main__":
    main()