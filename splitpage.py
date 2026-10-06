import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter
import os
import re


class PDFExtractor:

    def __init__(self, root):

        self.root = root
        self.root.title("PDF Page Extractor & Merger")
        self.root.geometry("750x650")
        self.root.resizable(False, False)

        self.input_pdf = None
        self.total_pages = 0

        self.create_ui()

    def create_ui(self):

        # =====================================================
        # TITLE
        # =====================================================

        tk.Label(
            self.root,
            text="PDF PAGE EXTRACTOR & MERGER",
            font=("Arial", 20, "bold")
        ).pack(pady=(20, 5))

        tk.Label(
            self.root,
            text="Select PDF → Enter page ranges → Extract & Merge",
            font=("Arial", 11)
        ).pack(pady=(0, 20))

        # =====================================================
        # SELECT PDF BUTTON
        # =====================================================

        pdf_frame = tk.Frame(self.root)
        pdf_frame.pack(fill="x", padx=35)

        tk.Button(
            pdf_frame,
            text="SELECT PDF",
            font=("Arial", 12, "bold"),
            width=16,
            height=2,
            command=self.select_pdf
        ).pack(side="left")

        self.file_label = tk.Label(
            pdf_frame,
            text="No PDF selected",
            font=("Arial", 10),
            anchor="w"
        )

        self.file_label.pack(
            side="left",
            padx=15,
            fill="x",
            expand=True
        )

        # =====================================================
        # PAGE COUNT
        # =====================================================

        self.page_label = tk.Label(
            self.root,
            text="Total pages: -",
            font=("Arial", 11, "bold")
        )

        self.page_label.pack(pady=15)

        # =====================================================
        # RANGE SECTION
        # =====================================================

        tk.Label(
            self.root,
            text="Enter page ranges",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=35)

        tk.Label(
            self.root,
            text="Examples: 1 to 10   OR   1 to 5, 20 to 25, 35 to 50",
            font=("Arial", 9)
        ).pack(anchor="w", padx=35, pady=(3, 8))

        # =====================================================
        # TEXT BOX
        # =====================================================

        text_frame = tk.Frame(self.root)
        text_frame.pack(
            fill="both",
            expand=False,
            padx=35
        )

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.range_text = tk.Text(
            text_frame,
            height=12,
            width=75,
            font=("Consolas", 12),
            yscrollcommand=scrollbar.set
        )

        self.range_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.range_text.yview
        )

        # Example
        self.range_text.insert(
            "1.0",
            "1 to 5\n20 to 25\n35 to 50"
        )

        # =====================================================
        # OUTPUT INFORMATION
        # =====================================================

        self.output_label = tk.Label(
            self.root,
            text="Output will be saved in the same folder as the original PDF.",
            font=("Arial", 10),
            wraplength=680
        )

        self.output_label.pack(
            pady=12
        )

        # =====================================================
        # >>> EXTRACT BUTTON <<<
        # =====================================================

        button_frame = tk.Frame(self.root)
        button_frame.pack(
            pady=10
        )

        self.extract_button = tk.Button(
            button_frame,
            text="EXTRACT & MERGE PDF",
            font=("Arial", 14, "bold"),
            width=28,
            height=2,
            command=self.extract_pdf
        )

        self.extract_button.pack()

        # =====================================================
        # STATUS
        # =====================================================

        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 10)
        )

        self.status_label.pack(
            pady=10
        )

    # =========================================================
    # SELECT PDF
    # =========================================================

    def select_pdf(self):

        file_path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[
                ("PDF Files", "*.pdf")
            ]
        )

        if not file_path:
            return

        try:

            reader = PdfReader(file_path)

            self.input_pdf = file_path
            self.total_pages = len(reader.pages)

            self.file_label.config(
                text=os.path.basename(file_path)
            )

            self.page_label.config(
                text=f"Total pages: {self.total_pages}"
            )

            self.status_label.config(
                text="PDF selected successfully"
            )

            # Show expected output filename

            folder = os.path.dirname(file_path)

            filename = os.path.basename(file_path)

            name, _ = os.path.splitext(filename)

            output = os.path.join(
                folder,
                f"{name}_Extracted.pdf"
            )

            self.output_label.config(
                text=f"Output: {output}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Unable to open PDF.\n\n{e}"
            )

    # =========================================================
    # PARSE RANGES
    # =========================================================

    def parse_ranges(self, text):

        ranges = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            # Allow:
            # 1 to 5
            # 1-5
            # 1 – 5
            # Multiple ranges separated by comma

            parts = re.split(
                r"[,;]+",
                line
            )

            for part in parts:

                part = part.strip()

                match = re.match(
                    r"^(\d+)\s*(?:to|-|–)\s*(\d+)$",
                    part,
                    re.IGNORECASE
                )

                if not match:

                    raise ValueError(
                        f"Invalid range:\n\n"
                        f"{part}\n\n"
                        f"Use:\n"
                        f"1 to 10\n"
                        f"or\n"
                        f"1-10"
                    )

                start = int(match.group(1))
                end = int(match.group(2))

                if start > end:

                    raise ValueError(
                        f"Invalid range:\n"
                        f"{start} to {end}"
                    )

                ranges.append(
                    (start, end)
                )

        if not ranges:

            raise ValueError(
                "Please enter at least one page range."
            )

        return ranges

    # =========================================================
    # UNIQUE OUTPUT NAME
    # =========================================================

    def get_output_path(self):

        folder = os.path.dirname(
            self.input_pdf
        )

        filename = os.path.basename(
            self.input_pdf
        )

        name, _ = os.path.splitext(filename)

        # First output filename
        output = os.path.join(
            folder,
            f"{name}_Extracted.pdf"
        )

        counter = 1

        while os.path.exists(output):

            output = os.path.join(
                folder,
                f"{name}_Extracted_{counter}.pdf"
            )

            counter += 1

        return output

    # =========================================================
    # EXTRACT & MERGE
    # =========================================================

    def extract_pdf(self):

        if not self.input_pdf:

            messagebox.showwarning(
                "Select PDF",
                "Please click SELECT PDF first."
            )

            return

        text = self.range_text.get(
            "1.0",
            tk.END
        ).strip()

        try:

            ranges = self.parse_ranges(text)

        except ValueError as e:

            messagebox.showerror(
                "Invalid Page Range",
                str(e)
            )

            return

        # Check page limits

        for start, end in ranges:

            if start < 1 or end > self.total_pages:

                messagebox.showerror(
                    "Invalid Page Range",
                    f"Range {start} to {end} is outside "
                    f"the PDF page range.\n\n"
                    f"PDF has {self.total_pages} pages."
                )

                return

        try:

            self.status_label.config(
                text="Extracting and merging..."
            )

            self.root.update()

            reader = PdfReader(
                self.input_pdf
            )

            writer = PdfWriter()

            total_selected = 0

            # Add pages in the exact order entered

            for start, end in ranges:

                for page in range(
                    start - 1,
                    end
                ):

                    writer.add_page(
                        reader.pages[page]
                    )

                    total_selected += 1

            # Same folder + alternate filename

            output_path = self.get_output_path()

            with open(
                output_path,
                "wb"
            ) as output_file:

                writer.write(
                    output_file
                )

            self.status_label.config(
                text="Extraction completed successfully!"
            )

            self.output_label.config(
                text=f"Created: {output_path}"
            )

            messagebox.showinfo(
                "SUCCESS",
                f"PDF created successfully!\n\n"
                f"Pages extracted: {total_selected}\n\n"
                f"Saved here:\n"
                f"{output_path}"
            )

        except Exception as e:

            self.status_label.config(
                text="Error"
            )

            messagebox.showerror(
                "Error",
                f"Could not create PDF.\n\n{e}"
            )


# =============================================================
# START PROGRAM
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PDFExtractor(root)

    root.mainloop()