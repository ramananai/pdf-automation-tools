import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import fitz  # PyMuPDF
import requests
import os
import re
import tempfile
import threading


# ============================================================
# PAGE RANGE PARSER
# ============================================================

def parse_page_ranges(text, total_pages):
    """
    Accepts:
        1-5
        1-5,10-15
        1,3,5
        1-5, 10, 15-20

    Returns zero-based page numbers.
    """

    text = text.strip()

    if not text:
        raise ValueError("Page range cannot be empty.")

    pages = []

    parts = re.split(r"[,\n]+", text)

    for part in parts:

        part = part.strip()

        if not part:
            continue

        if "-" in part:

            values = part.split("-")

            if len(values) != 2:
                raise ValueError(f"Invalid page range: {part}")

            start = int(values[0].strip())
            end = int(values[1].strip())

            if start < 1 or end < 1:
                raise ValueError(f"Page numbers must be 1 or greater: {part}")

            if start > end:
                raise ValueError(f"Invalid range: {part}")

            if end > total_pages:
                raise ValueError(
                    f"Page {end} does not exist. "
                    f"PDF has only {total_pages} pages."
                )

            for p in range(start, end + 1):
                pages.append(p - 1)

        else:

            p = int(part)

            if p < 1:
                raise ValueError(f"Invalid page number: {part}")

            if p > total_pages:
                raise ValueError(
                    f"Page {p} does not exist. "
                    f"PDF has only {total_pages} pages."
                )

            pages.append(p - 1)

    # Remove duplicates while preserving order
    unique_pages = []
    seen = set()

    for p in pages:
        if p not in seen:
            unique_pages.append(p)
            seen.add(p)

    return unique_pages


# ============================================================
# DOWNLOAD PDF
# ============================================================

def download_pdf(url, output_path):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=60,
        stream=True
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    # Write file
    with open(output_path, "wb") as f:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:
                f.write(chunk)

    # Basic validation
    if os.path.getsize(output_path) == 0:
        raise ValueError("Downloaded file is empty.")

    return output_path


# ============================================================
# CREATE TITLE / BLANK PAGE
# ============================================================

def create_title_page(name, width=595, height=842):

    page = fitz.open()

    title_page = page.new_page(
        width=width,
        height=height
    )

    # Large centered title
    rect = fitz.Rect(
        50,
        height / 2 - 60,
        width - 50,
        height / 2 + 60
    )

    title_page.insert_textbox(
        rect,
        name,
        fontsize=24,
        fontname="helv",
        align=1,
        color=(0, 0, 0)
    )

    return page


# ============================================================
# MAIN APPLICATION
# ============================================================

class PDFMergerApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "PDF URL Page Extractor & Merger"
        )

        self.root.geometry(
            "1100x700"
        )

        self.root.minsize(
            900,
            600
        )

        self.items = []

        self.create_ui()


    # ========================================================
    # UI
    # ========================================================

    def create_ui(self):

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            self.root,
            text="PDF URL PAGE EXTRACTOR & MERGER",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=(15, 5))


        subtitle = tk.Label(
            self.root,
            text=(
                "Enter PDF URL + Name + Page ranges. "
                "A title page will be inserted before each PDF's pages."
            ),
            font=("Arial", 10)
        )

        subtitle.pack(
            pady=(0, 15)
        )


        # ----------------------------------------------------
        # INPUT FRAME
        # ----------------------------------------------------

        input_frame = tk.LabelFrame(
            self.root,
            text="Add PDF",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )

        input_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )


        # URL

        tk.Label(
            input_frame,
            text="PDF URL:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.url_entry = tk.Entry(
            input_frame,
            font=("Arial", 10)
        )

        self.url_entry.grid(
            row=0,
            column=1,
            columnspan=4,
            sticky="ew",
            padx=5,
            pady=5
        )


        # NAME

        tk.Label(
            input_frame,
            text="Name:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=5
        )

        self.name_entry = tk.Entry(
            input_frame,
            font=("Arial", 10)
        )

        self.name_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5,
            pady=5
        )


        # PAGE RANGE

        tk.Label(
            input_frame,
            text="Pages:"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=(20, 5),
            pady=5
        )

        self.pages_entry = tk.Entry(
            input_frame,
            font=("Arial", 10)
        )

        self.pages_entry.grid(
            row=1,
            column=3,
            sticky="ew",
            padx=5,
            pady=5
        )


        # ADD BUTTON

        add_button = tk.Button(
            input_frame,
            text="ADD PDF",
            command=self.add_item,
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )

        add_button.grid(
            row=1,
            column=4,
            padx=10,
            pady=5
        )


        input_frame.columnconfigure(
            1,
            weight=1
        )

        input_frame.columnconfigure(
            3,
            weight=1
        )


        # ----------------------------------------------------
        # PAGE RANGE HELP
        # ----------------------------------------------------

        help_label = tk.Label(
            self.root,
            text=(
                "Page format examples: 1-5   |   1-5,10-15   |   "
                "1,3,7   |   2-5,10"
            ),
            font=("Arial", 9),
            anchor="w"
        )

        help_label.pack(
            fill="x",
            padx=20,
            pady=5
        )


        # ----------------------------------------------------
        # LIST FRAME
        # ----------------------------------------------------

        list_frame = tk.LabelFrame(
            self.root,
            text="PDFs to Merge",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )

        list_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )


        # ----------------------------------------------------
        # TREEVIEW
        # ----------------------------------------------------

        columns = (
            "number",
            "name",
            "pages",
            "url"
        )

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        self.tree.heading(
            "number",
            text="#"
        )

        self.tree.heading(
            "name",
            text="Name"
        )

        self.tree.heading(
            "pages",
            text="Page Ranges"
        )

        self.tree.heading(
            "url",
            text="PDF URL"
        )


        self.tree.column(
            "number",
            width=50,
            anchor="center"
        )

        self.tree.column(
            "name",
            width=180
        )

        self.tree.column(
            "pages",
            width=180
        )

        self.tree.column(
            "url",
            width=550
        )


        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )


        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        # ----------------------------------------------------
        # CONTROL BUTTONS
        # ----------------------------------------------------

        control_frame = tk.Frame(
            self.root
        )

        control_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )


        tk.Button(
            control_frame,
            text="↑ MOVE UP",
            command=self.move_up,
            width=12
        ).pack(
            side="left",
            padx=3
        )


        tk.Button(
            control_frame,
            text="↓ MOVE DOWN",
            command=self.move_down,
            width=12
        ).pack(
            side="left",
            padx=3
        )


        tk.Button(
            control_frame,
            text="REMOVE",
            command=self.remove_item,
            width=12
        ).pack(
            side="left",
            padx=3
        )


        tk.Button(
            control_frame,
            text="CLEAR ALL",
            command=self.clear_all,
            width=12
        ).pack(
            side="left",
            padx=3
        )


        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        output_frame = tk.Frame(
            self.root
        )

        output_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )


        tk.Label(
            output_frame,
            text="Output filename:"
        ).pack(
            side="left"
        )


        self.output_entry = tk.Entry(
            output_frame,
            font=("Arial", 10)
        )

        self.output_entry.insert(
            0,
            "Merged_PDF.pdf"
        )

        self.output_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10
        )


        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        self.progress = ttk.Progressbar(
            self.root,
            mode="determinate"
        )

        self.progress.pack(
            fill="x",
            padx=15,
            pady=5
        )


        self.status_label = tk.Label(
            self.root,
            text="Ready",
            anchor="w"
        )

        self.status_label.pack(
            fill="x",
            padx=15
        )


        # ----------------------------------------------------
        # MERGE BUTTON
        # ----------------------------------------------------

        merge_button = tk.Button(
            self.root,
            text="DOWNLOAD + EXTRACT + MERGE",
            command=self.start_merge,
            font=("Arial", 13, "bold"),
            padx=30,
            pady=10
        )

        merge_button.pack(
            pady=12
        )


    # ========================================================
    # ADD ITEM
    # ========================================================

    def add_item(self):

        url = self.url_entry.get().strip()
        name = self.name_entry.get().strip()
        pages = self.pages_entry.get().strip()

        if not url:
            messagebox.showwarning(
                "Missing URL",
                "Please enter the PDF URL."
            )
            return

        if not name:
            messagebox.showwarning(
                "Missing Name",
                "Please enter a name for this PDF."
            )
            return

        if not pages:
            messagebox.showwarning(
                "Missing Pages",
                "Please enter the page ranges."
            )
            return

        item = {
            "url": url,
            "name": name,
            "pages": pages
        }

        self.items.append(item)

        self.refresh_tree()

        self.url_entry.delete(
            0,
            tk.END
        )

        self.name_entry.delete(
            0,
            tk.END
        )

        self.pages_entry.delete(
            0,
            tk.END
        )

        self.url_entry.focus()


    # ========================================================
    # REFRESH TREE
    # ========================================================

    def refresh_tree(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, item in enumerate(
            self.items,
            start=1
        ):

            self.tree.insert(
                "",
                "end",
                values=(
                    i,
                    item["name"],
                    item["pages"],
                    item["url"]
                )
            )


    # ========================================================
    # MOVE UP
    # ========================================================

    def move_up(self):

        selected = self.tree.selection()

        if not selected:
            return

        indexes = [
            self.tree.index(item)
            for item in selected
        ]

        for index in indexes:

            if index > 0:

                self.items[index - 1], self.items[index] = (
                    self.items[index],
                    self.items[index - 1]
                )

        self.refresh_tree()


    # ========================================================
    # MOVE DOWN
    # ========================================================

    def move_down(self):

        selected = self.tree.selection()

        if not selected:
            return

        indexes = sorted(
            [
                self.tree.index(item)
                for item in selected
            ],
            reverse=True
        )

        for index in indexes:

            if index < len(self.items) - 1:

                self.items[index + 1], self.items[index] = (
                    self.items[index],
                    self.items[index + 1]
                )

        self.refresh_tree()


    # ========================================================
    # REMOVE
    # ========================================================

    def remove_item(self):

        selected = self.tree.selection()

        if not selected:
            return

        indexes = sorted(
            [
                self.tree.index(item)
                for item in selected
            ],
            reverse=True
        )

        for index in indexes:
            del self.items[index]

        self.refresh_tree()


    # ========================================================
    # CLEAR
    # ========================================================

    def clear_all(self):

        if not self.items:
            return

        answer = messagebox.askyesno(
            "Clear All",
            "Remove all PDFs from the list?"
        )

        if answer:
            self.items.clear()
            self.refresh_tree()


    # ========================================================
    # START MERGE
    # ========================================================

    def start_merge(self):

        if not self.items:

            messagebox.showwarning(
                "No PDFs",
                "Please add at least one PDF."
            )

            return

        output_name = self.output_entry.get().strip()

        if not output_name:

            messagebox.showwarning(
                "Output Filename",
                "Please enter an output filename."
            )

            return

        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"


        # Ask where to save
        output_path = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            initialfile=output_name,
            filetypes=[
                ("PDF Files", "*.pdf")
            ]
        )

        if not output_path:
            return


        # Disable button / start thread
        self.set_status(
            "Starting..."
        )

        threading.Thread(
            target=self.merge_process,
            args=(output_path,),
            daemon=True
        ).start()


    # ========================================================
    # MERGE PROCESS
    # ========================================================

    def merge_process(self, output_path):

        temp_files = []

        try:

            total = len(self.items)

            self.progress["maximum"] = total
            self.progress["value"] = 0


            # Final PDF
            final_doc = fitz.open()


            for index, item in enumerate(
                self.items,
                start=1
            ):

                name = item["name"]
                url = item["url"]
                page_range = item["pages"]


                self.set_status(
                    f"Downloading {index}/{total}: {name}"
                )


                # Temporary PDF
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".pdf",
                    delete=False
                )

                temp_file.close()

                temp_files.append(
                    temp_file.name
                )


                # Download
                download_pdf(
                    url,
                    temp_file.name
                )


                self.set_status(
                    f"Reading {index}/{total}: {name}"
                )


                source = fitz.open(
                    temp_file.name
                )


                # Parse pages
                selected_pages = parse_page_ranges(
                    page_range,
                    len(source)
                )


                # ------------------------------------------------
                # CREATE TITLE PAGE
                # ------------------------------------------------

                if len(source) > 0:

                    first_page = source[0]

                    rect = first_page.rect

                    title_doc = create_title_page(
                        name,
                        rect.width,
                        rect.height
                    )

                    final_doc.insert_pdf(
                        title_doc
                    )

                    title_doc.close()


                # ------------------------------------------------
                # INSERT SELECTED PAGES
                # ------------------------------------------------

                for page_number in selected_pages:

                    final_doc.insert_pdf(
                        source,
                        from_page=page_number,
                        to_page=page_number
                    )


                source.close()


                self.progress["value"] = index


            self.set_status(
                "Saving final PDF..."
            )


            # Save final PDF
            final_doc.save(
                output_path,
                garbage=4,
                deflate=True
            )

            final_doc.close()


            # ----------------------------------------------------
            # DELETE TEMPORARY FILES
            # ----------------------------------------------------

            for file in temp_files:

                try:
                    os.remove(file)

                except Exception:
                    pass


            self.set_status(
                "Completed"
            )


            messagebox.showinfo(
                "Completed",
                f"PDF created successfully.\n\n"
                f"Saved to:\n{output_path}"
            )


        except Exception as e:

            # Cleanup
            for file in temp_files:

                try:
                    os.remove(file)

                except Exception:
                    pass


            self.set_status(
                "Error"
            )


            messagebox.showerror(
                "Error",
                f"Could not create PDF.\n\n{str(e)}"
            )


    # ========================================================
    # STATUS
    # ========================================================

    def set_status(self, text):

        self.root.after(
            0,
            lambda: self.status_label.config(
                text=text
            )
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PDFMergerApp(
        root
    )

    root.mainloop()