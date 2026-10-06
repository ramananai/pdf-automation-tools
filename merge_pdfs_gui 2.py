"""
CA Final PDF Merger — GUI (Tkinter)
=====================================
Merge multiple PDFs (PYQ, MTP, RTP...) into ONE PDF with:
  1. Files merged in the EXACT order you add/arrange them
  2. "Page No: X" footer on every page (Helvetica-Bold, size 13)
  3. A clickable Index as the first page(s) — file name + starting page,
     click to jump straight there
  4. Bookmarks (left panel in Acrobat/Chrome/Edge) — one per file

HOW TO USE
----------
1. One-time setup (Command Prompt / PowerShell):
       pip install pypdf reportlab pikepdf

   (pikepdf is optional but recommended — it lets the tool automatically
   repair PDFs that are slightly damaged/corrupted, e.g. some PYQ/RTP/MTP
   files downloaded from ICAI's website that show a "Cannot find Root
   object" error otherwise.)

2. Run:
       python merge_pdfs.py

3. In the window that opens:
   - Click "Add File(s)" to browse and pick PDFs. Add them ONE BATCH AT A
     TIME in the order you want, or add one-by-one for full control.
   - Use "Move Up" / "Move Down" to reorder the list, "Remove" to drop one.
   - Click "Merge PDFs" and choose where to save the output file.

No need to edit any code — everything is done through the window.
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import Fit
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False

# ======================= SETTINGS (safe to tweak) =======================
PAGE_SIZE = A4                  # change to `letter` (from reportlab.lib.pagesizes) if needed
FOOTER_FONT = "Helvetica-Bold"
FOOTER_FONT_SIZE = 13
INDEX_TITLE = "INDEX"
# ==========================================================================


# ------------------------- Core merge logic -------------------------

def get_display_name(path):
    return os.path.splitext(os.path.basename(path))[0]


def safe_read_pdf(path, tmp_dir, cleanup_paths):
    """
    Opens a PDF with pypdf. If the file is damaged/corrupted (e.g. errors
    like "Cannot find Root object in pdf", broken cross-reference table,
    etc. — common with some PYQ/RTP/MTP downloads), automatically attempts
    a repair using pikepdf (which is built on qpdf, a very robust PDF
    repair engine) and retries.
    Raises a clear error naming the exact file if it truly cannot be read.
    Any temp repaired file created is appended to cleanup_paths for later removal.
    """
    try:
        reader = PdfReader(path)
        _ = len(reader.pages)  # force a real parse, not just lazy-open
        return reader
    except Exception as first_error:
        if not PIKEPDF_AVAILABLE:
            raise RuntimeError(
                f"'{os.path.basename(path)}' appears to be damaged/corrupted "
                f"({first_error}).\n\nInstall pikepdf for automatic repair:\n"
                f"    pip install pikepdf"
            )
        try:
            repaired_path = os.path.join(
                tmp_dir, f"_repaired_{os.path.basename(path)}"
            )
            with pikepdf.open(path) as pdf:
                pdf.save(repaired_path)
            cleanup_paths.append(repaired_path)
            reader = PdfReader(repaired_path)
            _ = len(reader.pages)
            return reader
        except Exception as repair_error:
            raise RuntimeError(
                f"'{os.path.basename(path)}' is damaged and could not be "
                f"repaired automatically.\n\n"
                f"Original error: {first_error}\n"
                f"Repair attempt error: {repair_error}\n\n"
                f"Try opening this file in Adobe Acrobat / a browser and "
                f"'Print to PDF' / 'Save As' to create a clean copy, then "
                f"use that copy instead."
            )


def index_layout_constants(page_size):
    width, height = page_size
    margin_x = 50
    top_y = height - 90
    line_height = 22
    usable_height = top_y - 60
    lines_per_page = max(1, int(usable_height // line_height))
    return width, height, margin_x, top_y, line_height, lines_per_page


def build_index_pdf(entries, page_size, path):
    """
    entries: list of (display_name, final_page_number) [1-based]
    Writes an index PDF to `path`. Returns link boxes:
        (page_index_within_index_pdf, x0, y0, x1, y1, target_page_number)
    """
    width, height, margin_x, top_y, line_height, lines_per_page = index_layout_constants(page_size)
    total_pages_needed = max(1, -(-len(entries) // lines_per_page))
    link_boxes = []

    c = canvas.Canvas(path, pagesize=page_size)
    entry_i = 0
    for page_i in range(total_pages_needed):
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 50, INDEX_TITLE)
        c.setFont("Helvetica", 12)
        y = top_y
        count_on_page = 0
        while entry_i < len(entries) and count_on_page < lines_per_page:
            name, target_page = entries[entry_i]
            sr_no = entry_i + 1
            c.drawString(margin_x, y, f"{sr_no}.  {name}")
            c.drawRightString(width - margin_x, y, str(target_page))
            link_boxes.append((page_i, margin_x - 5, y - 6, width - margin_x + 5, y + 14, target_page))
            y -= line_height
            entry_i += 1
            count_on_page += 1
        c.showPage()
    c.save()
    return link_boxes


def add_footers(writer, tmp_dir, start_number=1):
    for i, page in enumerate(writer.pages):
        mb = page.mediabox
        width, height = float(mb.width), float(mb.height)
        overlay_path = os.path.join(tmp_dir, f"_footer_temp_{i}.pdf")
        c = canvas.Canvas(overlay_path, pagesize=(width, height))
        c.setFont(FOOTER_FONT, FOOTER_FONT_SIZE)
        c.drawCentredString(width / 2, 25, f"Page No: {start_number + i}")
        c.save()
        overlay_reader = PdfReader(overlay_path)
        page.merge_page(overlay_reader.pages[0])
        os.remove(overlay_path)


def compute_index_pages_needed(num_entries, page_size):
    _, _, _, _, _, lines_per_page = index_layout_constants(page_size)
    return max(1, -(-num_entries // lines_per_page))


def merge_pdfs(file_list, output_path, progress_cb=None):
    """
    file_list: list of file paths, IN THE ORDER to merge them.
    output_path: full path to save the merged PDF.
    progress_cb: optional function(str) called with status updates.
    """
    def report(msg):
        if progress_cb:
            progress_cb(msg)

    tmp_dir = os.path.dirname(output_path) or "."
    display_names = [get_display_name(f) for f in file_list]

    cleanup_paths = []
    readers = []
    for f in file_list:
        report(f"Reading {os.path.basename(f)}...")
        readers.append(safe_read_pdf(f, tmp_dir, cleanup_paths))
    page_counts = [len(r.pages) for r in readers]

    num_index_pages = compute_index_pages_needed(len(file_list), PAGE_SIZE)

    def build_entries(n_index_pages):
        start_pages, running = [], n_index_pages + 1
        for count in page_counts:
            start_pages.append(running)
            running += count
        return list(zip(display_names, start_pages))

    entries = build_entries(num_index_pages)

    report("Building index...")
    index_path = os.path.join(tmp_dir, "_index_temp.pdf")
    link_boxes = build_index_pdf(entries, PAGE_SIZE, index_path)
    actual_index_pages = len(PdfReader(index_path).pages)

    if actual_index_pages != num_index_pages:
        num_index_pages = actual_index_pages
        entries = build_entries(num_index_pages)
        link_boxes = build_index_pdf(entries, PAGE_SIZE, index_path)

    index_reader = PdfReader(index_path)

    report("Merging pages...")
    writer = PdfWriter()
    for p in index_reader.pages:
        writer.add_page(p)
    for r in readers:
        for p in r.pages:
            writer.add_page(p)

    report("Adding page numbers...")
    add_footers(writer, tmp_dir, start_number=1)

    report("Adding clickable index links...")
    for (idx_page_i, x0, y0, x1, y1, target_page) in link_boxes:
        link = Link(rect=(x0, y0, x1, y1), target_page_index=target_page - 1, fit=Fit("/Fit"))
        writer.add_annotation(page_number=idx_page_i, annotation=link)

    report("Adding bookmarks...")
    writer.add_outline_item("Index", 0)
    for name, start_page in entries:
        writer.add_outline_item(name, start_page - 1)

    report("Saving file...")
    with open(output_path, "wb") as f:
        writer.write(f)

    os.remove(index_path)
    for p in cleanup_paths:
        try:
            os.remove(p)
        except OSError:
            pass  # not critical if a temp repaired file can't be deleted

    return len(writer.pages), num_index_pages


# ------------------------- GUI -------------------------

class MergerApp:
    def __init__(self, root):
        self.root = root
        root.title("CA Final PDF Merger")
        root.geometry("640x480")
        root.resizable(True, True)

        self.files = []  # full paths, in merge order

        header = tk.Label(root, text="Add your PDFs below in the order you want them merged",
                           font=("Segoe UI", 11, "bold"))
        header.pack(pady=(12, 4))

        sub = tk.Label(root, text="Tip: use Move Up / Move Down to fix the order (PYQ, MTP, RTP, etc.)",
                        font=("Segoe UI", 9), fg="gray30")
        sub.pack(pady=(0, 8))

        list_frame = tk.Frame(root)
        list_frame.pack(fill="both", expand=True, padx=12)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("Segoe UI", 10))
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=12, pady=8)

        tk.Button(btn_frame, text="Add File(s)", width=12, command=self.add_files).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Remove", width=10, command=self.remove_selected).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Move Up", width=10, command=self.move_up).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Move Down", width=10, command=self.move_down).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Clear All", width=10, command=self.clear_all).pack(side="left", padx=3)

        self.status_var = tk.StringVar(value="No files added yet.")
        status_label = tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 9), fg="gray20")
        status_label.pack(pady=(4, 0))

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", padx=12, pady=(6, 4))

        merge_btn = tk.Button(root, text="Merge PDFs...", font=("Segoe UI", 11, "bold"),
                               bg="#2e7d32", fg="white", height=2, command=self.start_merge)
        merge_btn.pack(fill="x", padx=12, pady=(4, 12))

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, f in enumerate(self.files, start=1):
            self.listbox.insert(tk.END, f"{i}. {os.path.basename(f)}")
        self.status_var.set(f"{len(self.files)} file(s) added.")

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select PDF file(s) to add",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not paths:
            return
        for p in paths:
            self.files.append(p)
        self.refresh_listbox()

    def remove_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        del self.files[idx]
        self.refresh_listbox()

    def move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        self.files[idx - 1], self.files[idx] = self.files[idx], self.files[idx - 1]
        self.refresh_listbox()
        self.listbox.selection_set(idx - 1)

    def move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.files) - 1:
            return
        idx = sel[0]
        self.files[idx + 1], self.files[idx] = self.files[idx], self.files[idx + 1]
        self.refresh_listbox()
        self.listbox.selection_set(idx + 1)

    def clear_all(self):
        self.files = []
        self.refresh_listbox()

    def start_merge(self):
        if not self.files:
            messagebox.showwarning("No files", "Please add at least one PDF file first.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="CA_Final_Merged.pdf"
        )
        if not output_path:
            return

        self.progress.start(10)
        self.status_var.set("Merging... please wait")

        # Run in a background thread so the window doesn't freeze
        thread = threading.Thread(target=self._run_merge, args=(list(self.files), output_path))
        thread.start()

    def _run_merge(self, files, output_path):
        try:
            def progress_cb(msg):
                self.root.after(0, lambda: self.status_var.set(msg))

            total_pages, index_pages = merge_pdfs(files, output_path, progress_cb)

            def on_success():
                self.progress.stop()
                self.status_var.set(f"Done! {len(files)} files merged into {total_pages} pages.")
                messagebox.showinfo(
                    "Success",
                    f"Merged PDF saved to:\n{output_path}\n\n"
                    f"Files merged: {len(files)}\n"
                    f"Index pages: {index_pages}\n"
                    f"Total pages: {total_pages}"
                )
            self.root.after(0, on_success)

        except Exception as e:
            error_message = str(e)  # capture now; Python clears 'e' after the except block

            def on_error():
                self.progress.stop()
                self.status_var.set("Failed. See error message.")
                messagebox.showerror("Error", f"Something went wrong:\n\n{error_message}")
            self.root.after(0, on_error)


if __name__ == "__main__":
    root = tk.Tk()
    app = MergerApp(root)
    root.mainloop()
