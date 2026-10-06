import io
import os
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from reportlab.lib.pagesizes import A4, LETTER, A5
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color


class PDFGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 Ramanan's Custom Blank PDF Pages Generator")
        self.root.geometry("950x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.page_style_var = ctk.StringVar(value="Ruled Lines")
        self.page_size_var = ctk.StringVar(value="A4")
        self.show_page_numbers_var = ctk.BooleanVar(value=True)
        self.add_margin_line_var = ctk.BooleanVar(value=False)
        self.auto_timestamp_var = ctk.BooleanVar(value=False)
        
        # Color variables (RGB tuples)
        self.line_color = (1, 1, 0)  # Yellow
        self.bg_color_pdf = (0, 0, 0)  # Black
        self.watermark_color = (1, 1, 1)  # White
        
        # Default values
        self.line_spacing = 25
        self.line_width = 0.6
        self.margin = 50
        self.margin_line_pos = 80
        self.watermark_size = 60
        self.watermark_opacity = 0.05
        self.generation_count = 0
        
        self.create_ui()
    
    def create_ui(self):
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title section
        title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(title_frame, text="📄 Ramanan's Custom Blank PDF Pages Generator", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack()
        
        subtitle = ctk.CTkLabel(title_frame, text="Create customized ruled PDFs with watermarks and styling options", 
                               font=ctk.CTkFont(size=13), text_color="gray70")
        subtitle.pack(pady=(5, 0))
        
        # Copyright info
        copyright_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        copyright_frame.pack(pady=(8, 0))
        
        copyright_label = ctk.CTkLabel(copyright_frame, text="© Ramanan RDS", 
                                      font=ctk.CTkFont(size=11), text_color="gray60")
        copyright_label.pack()
        
        made_with_label = ctk.CTkLabel(copyright_frame, text="Made with Claude AI ✨", 
                                      font=ctk.CTkFont(size=10), text_color="gray50")
        made_with_label.pack(pady=(2, 0))
        
        # Create tabview
        self.tabview = ctk.CTkTabview(main_container, height=400)
        self.tabview.pack(fill="both", expand=True, pady=(0, 15))
        
        # Add tabs
        self.tabview.add("📋 Basic Settings")
        self.tabview.add("🎨 Page Style")
        self.tabview.add("✨ Watermark")
        
        # Create tab content
        self.create_basic_settings(self.tabview.tab("📋 Basic Settings"))
        self.create_style_settings(self.tabview.tab("🎨 Page Style"))
        self.create_watermark_settings(self.tabview.tab("✨ Watermark"))
        
        # Generate button
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        self.generate_btn = ctk.CTkButton(btn_frame, text="🎨 Generate PDF", 
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         height=50, corner_radius=10,
                                         command=self.generate_pdf)
        self.generate_btn.pack(expand=True)
        
        # Status label
        self.status_label = ctk.CTkLabel(main_container, text="Ready to generate PDF", 
                                        font=ctk.CTkFont(size=12), text_color="gray60")
        self.status_label.pack(pady=5)
        
        # Stats label
        self.stats_label = ctk.CTkLabel(main_container, text="PDFs generated: 0", 
                                       font=ctk.CTkFont(size=10), text_color="gray50")
        self.stats_label.pack()
    
    def create_basic_settings(self, parent):
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File name
        file_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(file_frame, text="File name (without .pdf):", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.filename_entry = ctk.CTkEntry(file_frame, placeholder_text="custom_pdf", height=35)
        self.filename_entry.insert(0, "custom_pdf")
        self.filename_entry.pack(fill="x")
        
        # Number of pages
        pages_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        pages_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(pages_frame, text="Number of pages:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        pages_inner = ctk.CTkFrame(pages_frame, fg_color="transparent")
        pages_inner.pack(fill="x")
        
        self.num_pages_slider = ctk.CTkSlider(pages_inner, from_=1, to=300, number_of_steps=299,
                                             command=self.update_pages_label)
        self.num_pages_slider.set(5)
        self.num_pages_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.pages_value_label = ctk.CTkLabel(pages_inner, text="5", width=40,
                                             font=ctk.CTkFont(size=13, weight="bold"))
        self.pages_value_label.pack(side="left")
        
        # Save location
        save_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        save_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(save_frame, text="Save location:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        save_inner = ctk.CTkFrame(save_frame, fg_color="transparent")
        save_inner.pack(fill="x")
        
        self.save_location_entry = ctk.CTkEntry(save_inner, height=35)
        self.save_location_entry.insert(0, str(Path.home()))
        self.save_location_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(save_inner, text="📁 Browse", width=100, height=35,
                                  command=self.browse_folder)
        browse_btn.pack(side="left")
        
        # Page size
        size_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(size_frame, text="Page size:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.page_size_menu = ctk.CTkOptionMenu(size_frame, values=["A4", "Letter", "A5"],
                                               variable=self.page_size_var, height=35)
        self.page_size_menu.pack(fill="x")
        
        # Checkboxes
        options_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(options_frame, text="Options:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkCheckBox(options_frame, text="Add timestamp to filename", 
                       variable=self.auto_timestamp_var).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(options_frame, text="Show page numbers", 
                       variable=self.show_page_numbers_var).pack(anchor="w", pady=5)
    
    def create_style_settings(self, parent):
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Page style
        style_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        style_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(style_frame, text="Page Type:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        radio_frame = ctk.CTkFrame(style_frame, fg_color="transparent")
        radio_frame.pack(fill="x")
        
        ctk.CTkRadioButton(radio_frame, text="Ruled Lines", variable=self.page_style_var, 
                          value="Ruled Lines", command=self.toggle_line_settings).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(radio_frame, text="Blank Page", variable=self.page_style_var, 
                          value="Blank Page", command=self.toggle_line_settings).pack(side="left")
        
        # Line settings frame
        self.line_settings_frame = ctk.CTkFrame(scroll_frame)
        self.line_settings_frame.pack(fill="x", pady=15, padx=5)
        
        settings_inner = ctk.CTkFrame(self.line_settings_frame, fg_color="transparent")
        settings_inner.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(settings_inner, text="Line Settings", 
                    font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0, 15))
        
        # Line spacing
        spacing_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        spacing_frame.pack(fill="x", pady=8)
        
        spacing_label_frame = ctk.CTkFrame(spacing_frame, fg_color="transparent")
        spacing_label_frame.pack(fill="x")
        ctk.CTkLabel(spacing_label_frame, text="Line spacing:").pack(side="left")
        self.spacing_value = ctk.CTkLabel(spacing_label_frame, text="25", 
                                         font=ctk.CTkFont(weight="bold"))
        self.spacing_value.pack(side="right")
        
        self.spacing_slider = ctk.CTkSlider(spacing_frame, from_=15, to=40, number_of_steps=25,
                                           command=self.update_spacing)
        self.spacing_slider.set(25)
        self.spacing_slider.pack(fill="x", pady=(5, 0))
        
        # Line width
        width_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        width_frame.pack(fill="x", pady=8)
        
        width_label_frame = ctk.CTkFrame(width_frame, fg_color="transparent")
        width_label_frame.pack(fill="x")
        ctk.CTkLabel(width_label_frame, text="Line width:").pack(side="left")
        self.width_value = ctk.CTkLabel(width_label_frame, text="0.6", 
                                       font=ctk.CTkFont(weight="bold"))
        self.width_value.pack(side="right")
        
        self.width_slider = ctk.CTkSlider(width_frame, from_=0.3, to=2.0, number_of_steps=17,
                                         command=self.update_width)
        self.width_slider.set(0.6)
        self.width_slider.pack(fill="x", pady=(5, 0))
        
        # Margin
        margin_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        margin_frame.pack(fill="x", pady=8)
        
        margin_label_frame = ctk.CTkFrame(margin_frame, fg_color="transparent")
        margin_label_frame.pack(fill="x")
        ctk.CTkLabel(margin_label_frame, text="Page margin:").pack(side="left")
        self.margin_value = ctk.CTkLabel(margin_label_frame, text="50", 
                                        font=ctk.CTkFont(weight="bold"))
        self.margin_value.pack(side="right")
        
        self.margin_slider = ctk.CTkSlider(margin_frame, from_=30, to=80, number_of_steps=50,
                                          command=self.update_margin)
        self.margin_slider.set(50)
        self.margin_slider.pack(fill="x", pady=(5, 0))
        
        # Line color
        line_color_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        line_color_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(line_color_frame, text="Line color:").pack(anchor="w", pady=(0, 5))
        
        color_inner = ctk.CTkFrame(line_color_frame, fg_color="transparent")
        color_inner.pack(fill="x")
        
        self.line_color_menu = ctk.CTkOptionMenu(color_inner, 
                                                values=["Light Yellow", "White", "Light Blue", "Light Grey", "Custom"],
                                                command=self.change_line_color, height=35)
        self.line_color_menu.set("Light Yellow")
        self.line_color_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.line_color_btn = ctk.CTkButton(color_inner, text="🎨 Pick", width=80, height=35,
                                           command=self.pick_line_color)
        self.line_color_btn.pack(side="left")
        
        # Background color
        bg_color_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        bg_color_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(bg_color_frame, text="Background color:").pack(anchor="w", pady=(0, 5))
        
        bg_inner = ctk.CTkFrame(bg_color_frame, fg_color="transparent")
        bg_inner.pack(fill="x")
        
        self.bg_color_menu = ctk.CTkOptionMenu(bg_inner, 
                                              values=["Black", "Dark Grey", "Dark Blue", "Custom"],
                                              command=self.change_bg_color, height=35)
        self.bg_color_menu.set("Black")
        self.bg_color_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.bg_color_btn = ctk.CTkButton(bg_inner, text="🎨 Pick", width=80, height=35,
                                         command=self.pick_bg_color)
        self.bg_color_btn.pack(side="left")
        
        # Margin line
        margin_line_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        margin_line_frame.pack(fill="x", pady=10)
        
        ctk.CTkCheckBox(margin_line_frame, text="Add margin line (notebook style)", 
                       variable=self.add_margin_line_var,
                       command=self.toggle_margin_line).pack(anchor="w")
        
        # Margin line position (hidden by default)
        self.margin_line_pos_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        
        ml_label_frame = ctk.CTkFrame(self.margin_line_pos_frame, fg_color="transparent")
        ml_label_frame.pack(fill="x")
        ctk.CTkLabel(ml_label_frame, text="Margin line position:").pack(side="left")
        self.ml_value = ctk.CTkLabel(ml_label_frame, text="80", 
                                    font=ctk.CTkFont(weight="bold"))
        self.ml_value.pack(side="right")
        
        self.ml_slider = ctk.CTkSlider(self.margin_line_pos_frame, from_=50, to=150, 
                                      number_of_steps=100, command=self.update_margin_line)
        self.ml_slider.set(80)
        self.ml_slider.pack(fill="x", pady=(5, 0))
    
    def create_watermark_settings(self, parent):
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Watermark text
        text_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        text_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(text_frame, text="Watermark text:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.watermark_entry = ctk.CTkEntry(text_frame, placeholder_text="Enter watermark text", height=35)
        self.watermark_entry.insert(0, "Ramanan")
        self.watermark_entry.pack(fill="x")
        
        # Watermark color
        wm_color_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        wm_color_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(wm_color_frame, text="Watermark color:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        color_inner = ctk.CTkFrame(wm_color_frame, fg_color="transparent")
        color_inner.pack(fill="x")
        
        self.wm_color_menu = ctk.CTkOptionMenu(color_inner, 
                                              values=["White", "Light Grey", "Light Yellow", "Light Blue", "Custom"],
                                              command=self.change_watermark_color, height=35)
        self.wm_color_menu.set("White")
        self.wm_color_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.wm_color_btn = ctk.CTkButton(color_inner, text="🎨 Pick", width=80, height=35,
                                         command=self.pick_watermark_color)
        self.wm_color_btn.pack(side="left")
        
        # Watermark size
        size_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        size_frame.pack(fill="x", pady=10)
        
        size_label_frame = ctk.CTkFrame(size_frame, fg_color="transparent")
        size_label_frame.pack(fill="x")
        ctk.CTkLabel(size_label_frame, text="Watermark size:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        self.wm_size_value = ctk.CTkLabel(size_label_frame, text="60", 
                                         font=ctk.CTkFont(size=13, weight="bold"))
        self.wm_size_value.pack(side="right")
        
        self.wm_size_slider = ctk.CTkSlider(size_frame, from_=30, to=100, number_of_steps=70,
                                           command=self.update_wm_size)
        self.wm_size_slider.set(60)
        self.wm_size_slider.pack(fill="x", pady=(5, 0))
        
        # Watermark opacity
        opacity_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        opacity_frame.pack(fill="x", pady=10)
        
        opacity_label_frame = ctk.CTkFrame(opacity_frame, fg_color="transparent")
        opacity_label_frame.pack(fill="x")
        ctk.CTkLabel(opacity_label_frame, text="Watermark opacity:", 
                    font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        self.wm_opacity_value = ctk.CTkLabel(opacity_label_frame, text="0.05", 
                                            font=ctk.CTkFont(size=13, weight="bold"))
        self.wm_opacity_value.pack(side="right")
        
        self.wm_opacity_slider = ctk.CTkSlider(opacity_frame, from_=0.01, to=0.20, number_of_steps=19,
                                              command=self.update_wm_opacity)
        self.wm_opacity_slider.set(0.05)
        self.wm_opacity_slider.pack(fill="x", pady=(5, 0))
    
    # Update methods
    def update_pages_label(self, value):
        self.pages_value_label.configure(text=str(int(value)))
    
    def update_spacing(self, value):
        self.line_spacing = int(value)
        self.spacing_value.configure(text=str(self.line_spacing))
    
    def update_width(self, value):
        self.line_width = round(value, 1)
        self.width_value.configure(text=f"{self.line_width:.1f}")
    
    def update_margin(self, value):
        self.margin = int(value)
        self.margin_value.configure(text=str(self.margin))
    
    def update_margin_line(self, value):
        self.margin_line_pos = int(value)
        self.ml_value.configure(text=str(self.margin_line_pos))
    
    def update_wm_size(self, value):
        self.watermark_size = int(value)
        self.wm_size_value.configure(text=str(self.watermark_size))
    
    def update_wm_opacity(self, value):
        self.watermark_opacity = round(value, 2)
        self.wm_opacity_value.configure(text=f"{self.watermark_opacity:.2f}")
    
    def toggle_line_settings(self):
        if self.page_style_var.get() == "Ruled Lines":
            self.line_settings_frame.pack(fill="x", pady=15, padx=5)
        else:
            self.line_settings_frame.pack_forget()
    
    def toggle_margin_line(self):
        if self.add_margin_line_var.get():
            self.margin_line_pos_frame.pack(fill="x", pady=(10, 0))
        else:
            self.margin_line_pos_frame.pack_forget()
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_location_entry.delete(0, "end")
            self.save_location_entry.insert(0, folder)
    
    def change_line_color(self, preset):
        presets = {
            "Light Yellow": (1, 1, 0),
            "White": (1, 1, 1),
            "Light Blue": (0.5, 0.7, 1),
            "Light Grey": (0.7, 0.7, 0.7)
        }
        if preset in presets:
            self.line_color = presets[preset]
    
    def pick_line_color(self):
        color = colorchooser.askcolor(title="Choose Line Color")
        if color[0]:
            r, g, b = color[0]
            self.line_color = (r/255, g/255, b/255)
            self.line_color_menu.set("Custom")
    
    def change_bg_color(self, preset):
        presets = {
            "Black": (0, 0, 0),
            "Dark Grey": (0.2, 0.2, 0.2),
            "Dark Blue": (0.05, 0.05, 0.15)
        }
        if preset in presets:
            self.bg_color_pdf = presets[preset]
    
    def pick_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")
        if color[0]:
            r, g, b = color[0]
            self.bg_color_pdf = (r/255, g/255, b/255)
            self.bg_color_menu.set("Custom")
    
    def change_watermark_color(self, preset):
        presets = {
            "White": (1, 1, 1),
            "Light Grey": (0.7, 0.7, 0.7),
            "Light Yellow": (1, 1, 0),
            "Light Blue": (0.5, 0.7, 1)
        }
        if preset in presets:
            self.watermark_color = presets[preset]
    
    def pick_watermark_color(self):
        color = colorchooser.askcolor(title="Choose Watermark Color")
        if color[0]:
            r, g, b = color[0]
            self.watermark_color = (r/255, g/255, b/255)
            self.wm_color_menu.set("Custom")
    
    def generate_pdf(self):
        try:
            # Get values
            filename = self.filename_entry.get().strip() or "custom_pdf"
            filename = self.validate_filename(filename)
            
            if self.auto_timestamp_var.get():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename}_{timestamp}"
            
            num_pages = int(self.num_pages_slider.get())
            save_location = self.save_location_entry.get().strip()
            
            # Update status
            self.status_label.configure(text="⏳ Generating PDF...", text_color="orange")
            self.generate_btn.configure(state="disabled")
            self.root.update()
            
            # Generate PDF
            page_sizes = {"A4": A4, "Letter": LETTER, "A5": A5}
            selected_page_size = page_sizes[self.page_size_var.get()]
            
            pdf_bytes = self.create_pdf(
                num_pages=num_pages,
                watermark_text=self.watermark_entry.get(),
                watermark_color=self.watermark_color,
                line_color=self.line_color,
                bg_color=self.bg_color_pdf,
                page_size=selected_page_size
            )
            
            # Save PDF
            if save_location and os.path.isdir(save_location):
                filepath = os.path.join(save_location, f"{filename}.pdf")
                with open(filepath, "wb") as f:
                    f.write(pdf_bytes)
                
                file_size_kb = len(pdf_bytes) / 1024
                self.generation_count += 1
                
                self.status_label.configure(text=f"✅ PDF saved successfully! ({file_size_kb:.2f} KB)", 
                                          text_color="green")
                self.stats_label.configure(text=f"PDFs generated: {self.generation_count}")
                
                messagebox.showinfo("Success", 
                                  f"PDF generated successfully!\n\nSaved to:\n{filepath}\n\nFile size: {file_size_kb:.2f} KB")
            else:
                messagebox.showerror("Error", "Invalid save location!")
                self.status_label.configure(text="❌ Invalid save location", text_color="red")
            
            self.generate_btn.configure(state="normal")
        
        except Exception as e:
            self.generate_btn.configure(state="normal")
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")
            self.status_label.configure(text=f"❌ Error: {str(e)}", text_color="red")
    
    def create_pdf(self, num_pages, watermark_text, watermark_color, line_color, bg_color, page_size):
        width, height = page_size
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=page_size)
        
        for page_number in range(1, num_pages + 1):
            # Background
            c.setFillColor(Color(*bg_color))
            c.rect(0, 0, width, height, fill=1, stroke=0)
            
            # Ruled lines (only for ruled pages)
            if self.page_style_var.get() == "Ruled Lines":
                c.setStrokeColor(Color(*line_color))
                c.setLineWidth(self.line_width)
                y = height - self.margin
                while y > self.margin:
                    c.line(self.margin, y, width - self.margin, y)
                    y -= self.line_spacing
                
                # Margin line
                if self.add_margin_line_var.get():
                    c.setStrokeColor(Color(*line_color))
                    c.setLineWidth(self.line_width * 1.5)
                    c.line(self.margin_line_pos, self.margin, 
                          self.margin_line_pos, height - self.margin)
            
            # Watermark
            if watermark_text.strip():
                c.saveState()
                c.setFont("Helvetica-Bold", self.watermark_size)
                c.setFillColor(Color(*watermark_color, alpha=self.watermark_opacity))
                c.translate(width / 2, height / 2)
                c.rotate(45)
                c.drawCentredString(0, 0, watermark_text)
                c.restoreState()
            
            # Page number
            if self.show_page_numbers_var.get():
                c.setFont("Helvetica-Bold", 12)
                c.setFillColor(Color(0.7, 0.7, 0.7))
                c.drawCentredString(width / 5, 20, f"Page {page_number}")
            
            c.showPage()
        
        c.save()
        pdf_bytes = buf.getvalue()
        buf.close()
        return pdf_bytes
    
    def validate_filename(self, filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip() or "custom_pdf"


if __name__ == "__main__":
    root = ctk.CTk()
    app = PDFGeneratorApp(root)
    root.mainloop()