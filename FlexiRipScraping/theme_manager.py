import json
from tkinter import ttk
from pathlib import Path

from config import resource_path, CONFIG_FILE


_DARK_DEFAULTS = {
    "background": "#051F20",
    "surface": "#0B2B26",
    "card": "#163832",
    "primary": "#235347",
    "primary_hover": "#397563",
    "accent": "#8EB69B",
    "text": "#DAF1DE",
    "text_secondary": "#8EB69B",
    "cream": "#F3E9D2",
    "cream_secondary": "#E8DCC4",
    "border": "#B8A98A",
    "success": "#8EB69B",
    "warning": "#F3E9D2",
    "error": "#E8DCC4",
}

_LIGHT_DEFAULTS = {
    "background": "#F3E9D2",
    "surface": "#E8DCC4",
    "card": "#FFFFFF",
    "primary": "#235347",
    "primary_hover": "#397563",
    "accent": "#8EB69B",
    "text": "#051F20",
    "text_secondary": "#397563",
    "cream": "#F3E9D2",
    "cream_secondary": "#E8DCC4",
    "border": "#B8A98A",
    "success": "#235347",
    "warning": "#B8A98A",
    "error": "#8B0000",
}

_TTK_DARK = {
    "background": "#163832",
    "foreground": "#DAF1DE",
    "row_even_background": "#163832",
    "row_odd_background": "#0B2B26",
    "heading_background": "#235347",
    "heading_foreground": "#F3E9D2",
    "selected_background": "#397563",
    "selected_foreground": "#F3E9D2",
    "field_background": "#163832",
    "border": "#235347",
    "row_height": 28,
}

_TTK_LIGHT = {
    "background": "#DAF1DE",
    "foreground": "#051F20",
    "row_even_background": "#DAF1DE",
    "row_odd_background": "#E8DCC4",
    "heading_background": "#235347",
    "heading_foreground": "#F3E9D2",
    "selected_background": "#8EB69B",
    "selected_foreground": "#051F20",
    "field_background": "#DAF1DE",
    "border": "#8EB69B",
    "row_height": 28,
}

_SWITCH_DARK = {"on": "#235347", "off": "#B8A98A", "button": "#F3E9D2", "button_hover": "#DAF1DE"}
_SWITCH_LIGHT = {"on": "#235347", "off": "#B8A98A", "button": "#051F20", "button_hover": "#163832"}


def _cargar_json(ruta):
    if not ruta.exists():
        return {}
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _guardar_tema(nombre):
    if not CONFIG_FILE.exists():
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {}
    data["tema"] = nombre
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _cargar_tema_guardado():
    if not CONFIG_FILE.exists():
        return "dark"
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tema", "dark")
    except (json.JSONDecodeError, OSError):
        return "dark"


class ThemeManager:
    def __init__(self, app):
        self.app = app
        self._themes = {}
        self._current_name = _cargar_tema_guardado()
        self._cargar_temas()

    def _cargar_temas(self):
        for nombre in ("dark", "light"):
            ruta = resource_path(f"themes/{nombre}.json")
            self._themes[nombre] = _cargar_json(ruta)

    @property
    def colors(self):
        return self._themes.get(self._current_name, {})

    @property
    def current(self):
        return self._current_name

    def _color(self, key):
        defaults = _DARK_DEFAULTS if self._current_name == "dark" else _LIGHT_DEFAULTS
        return self.colors.get(key, defaults.get(key, "#000000"))

    def _ttk_val(self, key):
        treeview = self.colors.get("treeview", {})
        defaults = _TTK_DARK if self._current_name == "dark" else _TTK_LIGHT
        return treeview.get(key, defaults.get(key, ""))

    def _switch_val(self, key):
        switch = self.colors.get("switch", {})
        defaults = _SWITCH_DARK if self._current_name == "dark" else _SWITCH_LIGHT
        return switch.get(key, defaults.get(key, "#000000"))

    def load(self, nombre):
        if nombre not in self._themes:
            return
        self._current_name = nombre
        _guardar_tema(nombre)
        self._aplicar()

    def toggle(self):
        nuevo = "light" if self._current_name == "dark" else "dark"
        self.load(nuevo)

    def _aplicar(self):
        app = self.app
        bg = self._color("background")
        card = self._color("card")
        surface = self._color("surface")
        text = self._color("text")
        text_sec = self._color("text_secondary")
        primary = self._color("primary")
        primary_h = self._color("primary_hover")
        border = self._color("border")

        app.configure(fg_color=bg)

        for attr in ("frame_busqueda", "frame_filtros", "frame_tabla"):
            frame = getattr(app, attr, None)
            if frame:
                frame.configure(fg_color=card)

        app.entry.configure(
            fg_color=surface, border_color=border,
            text_color=text, placeholder_text_color=text_sec,
        )
        app.btn_buscar.configure(
            fg_color=primary, hover_color=primary_h, text_color=text,
        )
        app.btn_escanear.configure(
            fg_color=primary, hover_color=primary_h, text_color=text,
        )
        app.combo_maquina.configure(
            fg_color=surface, border_color=border,
            button_color=primary, button_hover_color=primary_h,
            text_color=text,
        )
        app.combo_tipo.configure(
            fg_color=surface, border_color=border,
            button_color=primary, button_hover_color=primary_h,
            text_color=text,
        )
        app.entry_fecha_desde.configure(
            fg_color=surface, border_color=border,
            text_color=text, placeholder_text_color=text_sec,
        )
        app.entry_fecha_hasta.configure(
            fg_color=surface, border_color=border,
            text_color=text, placeholder_text_color=text_sec,
        )
        app.lbl_estado.configure(text_color=text)
        app.lbl_escaneo.configure(text_color=text_sec)
        app.lbl_version.configure(text_color=text_sec)
        app.lbl_tema.configure(text_color=text)

        for attr in ("lbl_maquina", "lbl_desde", "lbl_hasta", "lbl_tipo"):
            lbl = getattr(app, attr, None)
            if lbl:
                lbl.configure(text_color=text)

        app.switch_tema.configure(
            progress_color=self._switch_val("on"),
            fg_color=self._switch_val("off"),
            button_color=self._switch_val("button"),
            button_hover_color=self._switch_val("button_hover"),
        )

        self._aplicar_ttk()

    def _aplicar_ttk(self):
        app = self.app
        estilo = ttk.Style(app)
        estilo.theme_use("clam")

        bg = self._ttk_val("background")
        fg = self._ttk_val("foreground")
        hd_bg = self._ttk_val("heading_background")
        hd_fg = self._ttk_val("heading_foreground")
        sel_bg = self._ttk_val("selected_background")
        sel_fg = self._ttk_val("selected_foreground")
        rh = self._ttk_val("row_height")

        estilo.configure("Treeview",
                         rowheight=rh,
                         fieldbackground=bg,
                         background=bg,
                         foreground=fg)
        estilo.configure("Treeview.Heading",
                         background=hd_bg,
                         foreground=hd_fg)
        estilo.map("Treeview",
                    background=[("selected", sel_bg)],
                    foreground=[("selected", sel_fg)])
        estilo.configure("Vertical.TScrollbar",
                         background=hd_bg,
                         troughcolor=bg,
                         bordercolor=bg,
                         arrowcolor=fg)
        estilo.configure("Horizontal.TScrollbar",
                         background=hd_bg,
                         troughcolor=bg,
                         bordercolor=bg,
                         arrowcolor=fg)

        row_even = self._ttk_val("row_even_background")
        row_odd = self._ttk_val("row_odd_background")
        app.tabla.tag_configure("row_even", background=row_even, foreground=fg)
        app.tabla.tag_configure("row_odd", background=row_odd, foreground=fg)
