import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, simpledialog, messagebox
from color_utils import (
    hex_to_rgb, rgb_to_hex, rgb_to_hsl, get_contrast_color,
    generate_shades, generate_complementary, generate_analogous,
    generate_triadic, generate_monochromatic, is_valid_hex
)
from storage import load_palettes, save_palettes, add_palette, delete_palette, export_palette_css

BG = "#0d0d1a"
BG2 = "#12122a"
BG3 = "#1a1a3e"
BG4 = "#222244"
FG = "#e8e8ff"
FG2 = "#8888aa"
ACCENT = "#7c4dff"
ACCENT2 = "#651fff"
GREEN = "#00e676"
ERROR = "#ff5252"
WARNING = "#ffab40"
FONT_UI = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 11)
FONT_TITLE = ("Segoe UI", 15, "bold")


class PaletteForgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PaletteForge")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG)
        self.root.minsize(800, 550)

        self.current_color = "#7c4dff"
        self.saved_palettes = load_palettes()

        self._build_header()
        self._build_tabs()
        self._build_statusbar()

        self._update_color_display()

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG3, pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text="🎨 PaletteForge", bg=BG3, fg=FG, font=FONT_TITLE).pack(side=tk.LEFT, padx=16)
        tk.Label(header, text="  —  Color Picker & Palette Generator", bg=BG3, fg=FG2, font=FONT_UI).pack(side=tk.LEFT)

    def _build_tabs(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG3, foreground=FG2, padding=[16, 8], font=FONT_UI)
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_picker = tk.Frame(self.notebook, bg=BG)
        self.tab_palettes = tk.Frame(self.notebook, bg=BG)
        self.tab_saved = tk.Frame(self.notebook, bg=BG)

        self.notebook.add(self.tab_picker, text="🎨  Color")
        self.notebook.add(self.tab_palettes, text="🌈  Paletas")
        self.notebook.add(self.tab_saved, text="💾  Guardadas")

        self._build_picker_tab()
        self._build_palettes_tab()
        self._build_saved_tab()

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_change())

    def _build_picker_tab(self):
        main = tk.Frame(self.tab_picker, bg=BG, pady=20)
        main.pack(fill=tk.BOTH, expand=True, padx=24)

        left = tk.Frame(main, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))

        self.color_display = tk.Frame(left, bg=self.current_color, width=240, height=240,
                                       highlightbackground=BG3, highlightthickness=2)
        self.color_display.pack()
        self.color_display.pack_propagate(False)

        self.color_display_label = tk.Label(
            self.color_display, text=self.current_color.upper(),
            bg=self.current_color, font=("Segoe UI", 18, "bold")
        )
        self.color_display_label.pack(expand=True)

        tk.Button(
            left, text="🎨 Abrir selector de color", bg=ACCENT, fg="white",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
            padx=16, pady=8, cursor="hand2",
            activebackground=ACCENT2, activeforeground="white",
            command=self._open_color_picker
        ).pack(fill=tk.X, pady=(16, 0))

        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Código de color", bg=BG, fg=FG2, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 8))

        hex_row = tk.Frame(right, bg=BG)
        hex_row.pack(fill=tk.X, pady=4)
        tk.Label(hex_row, text="HEX", bg=BG, fg=FG2, font=FONT_UI, width=6).pack(side=tk.LEFT)
        self.hex_var = tk.StringVar(value=self.current_color)
        hex_entry = tk.Entry(hex_row, textvariable=self.hex_var, bg=BG3, fg=FG, font=FONT_MONO,
                              relief=tk.FLAT, insertbackground=FG, bd=0)
        hex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(8, 8))
        hex_entry.bind("<Return>", lambda e: self._apply_hex())
        tk.Button(hex_row, text="Copiar", bg=BG3, fg=ACCENT, font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  activebackground=BG4, activeforeground=ACCENT,
                  command=lambda: self._copy_to_clipboard(self.hex_var.get())).pack(side=tk.LEFT)

        self.rgb_label = self._build_code_row(right, "RGB")
        self.hsl_label = self._build_code_row(right, "HSL")

        tk.Label(right, text="Tonos", bg=BG, fg=FG2, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(20, 8))
        self.shades_frame = tk.Frame(right, bg=BG)
        self.shades_frame.pack(fill=tk.X)

        save_row = tk.Frame(right, bg=BG, pady=16)
        save_row.pack(fill=tk.X)
        tk.Button(
            save_row, text="💾 Guardar este color en una paleta nueva",
            bg=BG3, fg=ACCENT, font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
            padx=12, pady=8, cursor="hand2",
            activebackground=BG4, activeforeground=ACCENT,
            command=self._save_single_as_palette
        ).pack(fill=tk.X)

    def _build_code_row(self, parent, label_text):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=4)
        tk.Label(row, text=label_text, bg=BG, fg=FG2, font=FONT_UI, width=6).pack(side=tk.LEFT)
        value_label = tk.Label(row, text="", bg=BG3, fg=FG, font=FONT_MONO, anchor="w")
        value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(8, 8))
        tk.Button(row, text="Copiar", bg=BG3, fg=ACCENT, font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  activebackground=BG4, activeforeground=ACCENT,
                  command=lambda: self._copy_to_clipboard(value_label["text"])).pack(side=tk.LEFT)
        return value_label

    def _build_palettes_tab(self):
        main = tk.Frame(self.tab_palettes, bg=BG, pady=20)
        main.pack(fill=tk.BOTH, expand=True, padx=24)

        tk.Label(
            main, text=f"Paletas generadas a partir de {self.current_color.upper()}",
            bg=BG, fg=FG2, font=("Segoe UI", 9, "bold")
        ).pack(anchor=tk.W, pady=(0, 16))

        self.palettes_container = tk.Frame(main, bg=BG)
        self.palettes_container.pack(fill=tk.BOTH, expand=True)

    def _build_saved_tab(self):
        main = tk.Frame(self.tab_saved, bg=BG, pady=20)
        main.pack(fill=tk.BOTH, expand=True, padx=24)

        header = tk.Frame(main, bg=BG)
        header.pack(fill=tk.X, pady=(0, 12))
        tk.Label(header, text="Paletas guardadas", bg=BG, fg=FG2, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        self.saved_container = tk.Frame(main, bg=BG)
        self.saved_container.pack(fill=tk.BOTH, expand=True)

        self._refresh_saved()

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG3, pady=5)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(bar, text="Listo", bg=BG3, fg=FG2, font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=12)
        tk.Label(bar, text="PaletteForge v1.0", bg=BG3, fg=FG2, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=12)

    def _set_status(self, text, color=None):
        self.status_label.config(text=text, fg=color or FG2)

    def _open_color_picker(self):
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.hex_var.set(color)
            self._update_color_display()

    def _apply_hex(self):
        value = self.hex_var.get().strip()
        if not value.startswith("#"):
            value = "#" + value
        if is_valid_hex(value):
            self.current_color = value
            self._update_color_display()
        else:
            self._set_status("⚠ Código HEX inválido", WARNING)

    def _update_color_display(self):
        rgb = hex_to_rgb(self.current_color)
        hsl = rgb_to_hsl(rgb)
        contrast = get_contrast_color(rgb)

        self.color_display.config(bg=self.current_color)
        self.color_display_label.config(
            bg=self.current_color, fg=contrast,
            text=self.current_color.upper()
        )
        self.hex_var.set(self.current_color)
        self.rgb_label.config(text=f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})")
        self.hsl_label.config(text=f"hsl({hsl[0]}, {hsl[1]}%, {hsl[2]}%)")

        self._update_shades()
        self._update_palettes()

    def _update_shades(self):
        for widget in self.shades_frame.winfo_children():
            widget.destroy()

        shades = generate_shades(self.current_color, 7)
        for shade in shades:
            self._build_color_swatch(self.shades_frame, shade, side=tk.LEFT)

    def _build_color_swatch(self, parent, color, side=tk.TOP, width=60, height=60, show_label=True):
        rgb = hex_to_rgb(color)
        contrast = get_contrast_color(rgb)

        swatch = tk.Frame(parent, bg=color, width=width, height=height, cursor="hand2")
        swatch.pack(side=side, padx=2, pady=2)
        swatch.pack_propagate(False)

        if show_label:
            label = tk.Label(swatch, text=color.upper(), bg=color, fg=contrast, font=("Segoe UI", 8))
            label.pack(expand=True)
            label.bind("<Button-1>", lambda e, c=color: self._copy_to_clipboard(c))

        swatch.bind("<Button-1>", lambda e, c=color: self._copy_to_clipboard(c))
        return swatch

    def _update_palettes(self):
        for widget in self.palettes_container.winfo_children():
            widget.destroy()

        palettes = [
            ("Complementario", [self.current_color, generate_complementary(self.current_color)]),
            ("Análogo", [self.current_color] + generate_analogous(self.current_color)),
            ("Tríada", [self.current_color] + generate_triadic(self.current_color)),
            ("Monocromático", generate_monochromatic(self.current_color)),
        ]

        for title, colors in palettes:
            self._build_palette_row(title, colors)

    def _build_palette_row(self, title, colors):
        frame = tk.Frame(self.palettes_container, bg=BG3, pady=12, padx=12)
        frame.pack(fill=tk.X, pady=6)

        header = tk.Frame(frame, bg=BG3)
        header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(header, text=title, bg=BG3, fg=FG, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        tk.Button(
            header, text="💾 Guardar paleta", bg=BG4, fg=ACCENT,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=10, pady=3,
            cursor="hand2", activebackground=ACCENT, activeforeground="white",
            command=lambda t=title, c=colors: self._save_palette(t, c)
        ).pack(side=tk.RIGHT)

        swatches = tk.Frame(frame, bg=BG3)
        swatches.pack(fill=tk.X)

        for color in colors:
            self._build_color_swatch(swatches, color, side=tk.LEFT, width=80, height=70)

    def _refresh_saved(self):
        for widget in self.saved_container.winfo_children():
            widget.destroy()

        if not self.saved_palettes:
            tk.Label(self.saved_container, text="No tienes paletas guardadas aún",
                     bg=BG, fg=FG2, font=FONT_UI).pack(pady=40)
            return

        for i, palette in enumerate(self.saved_palettes):
            self._build_saved_row(i, palette)

    def _build_saved_row(self, index, palette):
        frame = tk.Frame(self.saved_container, bg=BG3, pady=12, padx=12)
        frame.pack(fill=tk.X, pady=6)

        header = tk.Frame(frame, bg=BG3)
        header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(header, text=palette["name"], bg=BG3, fg=FG, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        tk.Button(
            header, text="📋 Copiar CSS", bg=BG4, fg=ACCENT,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=10, pady=3,
            cursor="hand2", activebackground=ACCENT, activeforeground="white",
            command=lambda p=palette: self._copy_to_clipboard(export_palette_css(p["name"], p["colors"]))
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            header, text="🗑 Eliminar", bg=BG4, fg=ERROR,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=10, pady=3,
            cursor="hand2", activebackground=ERROR, activeforeground="white",
            command=lambda i=index: self._delete_palette(i)
        ).pack(side=tk.RIGHT, padx=4)

        swatches = tk.Frame(frame, bg=BG3)
        swatches.pack(fill=tk.X)

        for color in palette["colors"]:
            self._build_color_swatch(swatches, color, side=tk.LEFT, width=80, height=70)

    def _save_palette(self, name, colors):
        self.saved_palettes = add_palette(self.saved_palettes, name, colors)
        self._refresh_saved()
        self._set_status(f"✅ Paleta '{name}' guardada", GREEN)

    def _save_single_as_palette(self):
        name = simpledialog.askstring("Nueva paleta", "Nombre de la paleta:", initialvalue=self.current_color.upper())
        if name:
            self.saved_palettes = add_palette(self.saved_palettes, name, [self.current_color])
            self._refresh_saved()
            self._set_status(f"✅ Paleta '{name}' guardada", GREEN)

    def _delete_palette(self, index):
        confirm = messagebox.askyesno("Eliminar", "¿Eliminar esta paleta?")
        if confirm:
            self.saved_palettes = delete_palette(self.saved_palettes, index)
            self._refresh_saved()
            self._set_status("Paleta eliminada", WARNING)

    def _copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._set_status(f"✓ Copiado: {text}", GREEN)

    def _on_tab_change(self):
        if self.notebook.index(self.notebook.select()) == 1:
            self._update_palettes()