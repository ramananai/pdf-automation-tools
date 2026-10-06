import os
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class MarkItDownGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        self.root.geometry("650x250")
        self.root.resizable(False, False)

        self.pdf_path = ""
        self.output_path = ""

        self.build_ui()

    def build_ui(self):
        ttk.Label(
            self.root,
            text="PDF to Markdown Converter (MarkItDown)",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        # PDF Selection
        frame1 = ttk.Frame(self.root)
        frame1.pack(fill="x", padx=15, pady=5)

        self.pdf_var = tk.StringVar()

        ttk.Entry(
            frame1,
            textvariable=self.pdf_var,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            frame1,
            text="Browse PDF",
            command=self.select_pdf
        ).pack(side="left", padx=5)

        # Output Selection
        frame2 = ttk.Frame(self.root)
        frame2.pack(fill="x", padx=15, pady=5)

        self.output_var = tk.StringVar()

        ttk.Entry(
            frame2,
            textvariable=self.output_var,
            state="readonly"
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            frame2,
            text="Save As",
            command=self.select_output
        ).pack(side="left", padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(
            self.root,
            mode="indeterminate",
            length=500
        )
        self.progress.pack(pady=20)

        # Status
        self.status = tk.StringVar(value="Ready")
        ttk.Label(
            self.root,
            textvariable=self.status
        ).pack()

        # Convert Button
        self.convert_btn = ttk.Button(
            self.root,
            text="Convert",
            command=self.start_conversion
        )
        self.convert_btn.pack(pady=15)

    def select_pdf(self):
        file = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if file:
            self.pdf_path = file
            self.pdf_var.set(file)

            default_name = os.path.splitext(os.path.basename(file))[0] + ".md"

            self.output_path = filedialog.asksaveasfilename(
                title="Save Markdown As",
                defaultextension=".md",
                initialfile=default_name,
                filetypes=[("Markdown Files", "*.md")]
            )

            if self.output_path:
                self.output_var.set(self.output_path)

    def select_output(self):
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Select a PDF first.")
            return

        default_name = os.path.splitext(os.path.basename(self.pdf_path))[0] + ".md"

        file = filedialog.asksaveasfilename(
            title="Save Markdown As",
            defaultextension=".md",
            initialfile=default_name,
            filetypes=[("Markdown Files", "*.md")]
        )

        if file:
            self.output_path = file
            self.output_var.set(file)

    def start_conversion(self):
        if not self.pdf_path:
            messagebox.showerror("Error", "Select a PDF.")
            return

        if not self.output_path:
            messagebox.showerror("Error", "Select output location.")
            return

        self.convert_btn.config(state="disabled")
        self.progress.start(10)
        self.status.set("Converting... Please wait.")

        threading.Thread(target=self.convert, daemon=True).start()

    def convert(self):
        try:
            result = subprocess.run(
                [
                    "markitdown",
                    self.pdf_path,
                    "-o",
                    self.output_path
                ],
                capture_output=True,
                text=True
            )

            self.root.after(0, self.finish_conversion, result)

        except FileNotFoundError:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error",
                    "MarkItDown executable not found.\n\nTry replacing 'markitdown' with:\npy -m markitdown"
                )
            )
            self.root.after(0, self.reset_ui)

        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", str(e))
            )
            self.root.after(0, self.reset_ui)

    def finish_conversion(self, result):
        self.progress.stop()

        if result.returncode == 0:
            self.status.set("Conversion Complete")
            messagebox.showinfo(
                "Success",
                f"Markdown saved successfully.\n\n{self.output_path}"
            )
        else:
            self.status.set("Conversion Failed")
            messagebox.showerror(
                "Error",
                result.stderr if result.stderr else result.stdout
            )

        self.convert_btn.config(state="normal")

    def reset_ui(self):
        self.progress.stop()
        self.convert_btn.config(state="normal")
        self.status.set("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkItDownGUI(root)
    root.mainloop()