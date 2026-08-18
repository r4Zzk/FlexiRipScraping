import sys
from tkinter import ttk

import customtkinter as ctk

from config import FUENTES, resource_path
from services.sync_service import sincronizar
from services.search_service import buscar, contar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLUMNAS = [
    ("fecha_inicio", "Fecha", 160),
    ("tipo", "Tipo", 150),
    ("archivo", "Archivo", 360),
    ("emisor", "Emisor", 90),
    ("tipo_trabajo", "Tipo de trabajo", 150),
    ("dimension", "Dimensión", 130),
    ("resolucion", "Resolución", 130),
    ("info", "Estado", 220),
]

TIPO_LABEL = {
    "inicio_rip": "Inicio de RIP",
    "inicio_impresion": "Inicio de Impresión",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FlexiRip — Buscador de registros")
        self.geometry("1200x600")
        self.minsize(900, 400)

        self._cargar_icono()
        self._crear_barra_busqueda()
        self._crear_tabla()
        self.lbl_estado = ctk.CTkLabel(self, text="")
        self.lbl_estado.pack(pady=(0, 10))

    def _cargar_icono(self):
        png = resource_path("assets/icon.png")
        if png.exists():
            try:
                import tkinter as tk

                self._icono_tk = tk.PhotoImage(file=str(png))
                self.iconphoto(True, self._icono_tk)
            except Exception:
                pass
        ico = resource_path("assets/icon.ico")
        if ico.exists() and sys.platform == "win32":
            try:
                self.iconbitmap(str(ico))
            except Exception:
                pass

    def _crear_barra_busqueda(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=10, pady=10)

        self.entry = ctk.CTkEntry(
            frame,
            placeholder_text="Buscar por archivo, emisor o impresora...",
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda _e: self.buscar())

        self.btn_buscar = ctk.CTkButton(frame, text="Buscar", width=90, command=self.buscar)
        self.btn_buscar.pack(side="left", padx=(0, 10))

        self.btn_escanear = ctk.CTkButton(frame, text="Escanear", width=90, command=self.escanear)
        self.btn_escanear.pack(side="left")

    def _crear_tabla(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=26, fieldbackground="#242424", background="#242424", foreground="white")
        estilo.configure("Treeview.Heading", background="#333333", foreground="white")

        ids = [c[0] for c in COLUMNAS]
        self.tabla = ttk.Treeview(frame, columns=ids, show="headings")

        for cid, texto, ancho in COLUMNAS:
            self.tabla.heading(cid, text=texto)
            self.tabla.column(cid, width=ancho, anchor="w")

        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

    def escanear(self):
        self.lbl_estado.configure(text="Escaneando...")
        try:
            n = sincronizar()
            self.lbl_estado.configure(text=f"{n} registros leídos del log · Total en DB: {contar()}")
        except Exception as e:
            self.lbl_estado.configure(text=f"Error al escanear: {e}")
        self.buscar()

    def buscar(self):
        termino = self.entry.get().strip()
        filas = buscar(termino=termino)

        self.tabla.delete(*self.tabla.get_children())
        for f in filas:
            valores = []
            for cid, _texto, _ancho in COLUMNAS:
                v = f.get(cid)
                if cid == "tipo":
                    v = TIPO_LABEL.get(v, v) or ""
                elif cid == "duracion" and v is not None:
                    v = f"{v} segundos"
                else:
                    v = v or ""
                valores.append(v)
            self.tabla.insert("", "end", values=valores)

        self.lbl_estado.configure(text=f"{len(filas)} resultados")


if __name__ == "__main__":
    App().mainloop()
