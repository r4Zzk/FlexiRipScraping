import sys
import threading
import queue
from tkinter import ttk

import customtkinter as ctk

from config import FUENTES, resource_path, EMISOR_MAQUINAS
from services.sync_service import sincronizar
from services.search_service import buscar, contar, eliminar_registros
from theme_manager import ThemeManager

ctk.set_appearance_mode("dark")

COLUMNAS = [
    ("fecha_inicio", "Fecha", 160),
    ("tipo", "Tipo", 150),
    ("archivo", "Archivo", 360),
    ("emisor", "Emisor", 90),
    ("tipo_trabajo", "Tipo de trabajo", 150),
    ("numero_copias", "Copias", 70),
    ("dimension", "Dimensión", 130),
    ("resolucion", "Resolución", 130),
    ("info", "Estado", 220),
]

TIPO_LABEL = {
    "inicio_rip": "Inicio de RIP",
    "inicio_impresion": "Inicio de Impresión",
}

TIPO_REVERSE = {v: k for k, v in TIPO_LABEL.items()}

VERSION = "1.0.0"

MAQUINAS = sorted(set(EMISOR_MAQUINAS.values()))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FlexiRip — Buscador de registros")
        self.geometry("1300x650")
        self.minsize(900, 400)

        self.theme = ThemeManager(self)
        self._busqueda_en_curso = False
        self._callbacks = queue.Queue()
        self._poll_callbacks()

        self._cargar_icono()
        self._crear_barra_busqueda()
        self._crear_filtros()
        self._crear_tabla()
        self._crear_barra_estado()

        self.theme._aplicar()

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
        self.frame_busqueda = ctk.CTkFrame(self)
        self.frame_busqueda.pack(fill="x", padx=10, pady=(10, 0))

        self.entry = ctk.CTkEntry(
            self.frame_busqueda,
            placeholder_text="Buscar por archivo, impresora o estado...",
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda _e: self.buscar())

        self.btn_buscar = ctk.CTkButton(self.frame_busqueda, text="Buscar", width=90, command=self.buscar)
        self.btn_buscar.pack(side="left", padx=(0, 10))

        self.btn_escanear = ctk.CTkButton(self.frame_busqueda, text="Escanear", width=90, command=self.escanear)
        self.btn_escanear.pack(side="left")

        self.btn_eliminar = ctk.CTkButton(
            self.frame_busqueda, text="Eliminar", width=90,
            fg_color="#8B0000", hover_color="#A52A2A",
            command=self.eliminar_seleccion,
        )
        self.btn_eliminar.pack(side="left", padx=(10, 0))

    def _crear_filtros(self):
        self.frame_filtros = ctk.CTkFrame(self)
        self.frame_filtros.pack(fill="x", padx=10, pady=(5, 0))

        self.lbl_maquina = ctk.CTkLabel(self.frame_filtros, text="Máquina:")
        self.lbl_maquina.pack(side="left", padx=(10, 5))
        opciones_maq = ["Todas"] + MAQUINAS
        self.combo_maquina = ctk.CTkComboBox(
            self.frame_filtros, values=opciones_maq, width=130, command=lambda _e: self.buscar(),
        )
        self.combo_maquina.set("Todas")
        self.combo_maquina.pack(side="left", padx=(0, 15))

        self.lbl_desde = ctk.CTkLabel(self.frame_filtros, text="Desde:")
        self.lbl_desde.pack(side="left", padx=(0, 5))
        self.entry_fecha_desde = ctk.CTkEntry(self.frame_filtros, width=110, placeholder_text="AAAA-MM-DD")
        self.entry_fecha_desde.pack(side="left", padx=(0, 10))

        self.lbl_hasta = ctk.CTkLabel(self.frame_filtros, text="Hasta:")
        self.lbl_hasta.pack(side="left", padx=(0, 5))
        self.entry_fecha_hasta = ctk.CTkEntry(self.frame_filtros, width=110, placeholder_text="AAAA-MM-DD")
        self.entry_fecha_hasta.pack(side="left", padx=(0, 10))

        self.lbl_tipo = ctk.CTkLabel(self.frame_filtros, text="Tipo:")
        self.lbl_tipo.pack(side="left", padx=(0, 5))
        opciones_tipo = ["Todos", "Inicio de RIP", "Inicio de Impresión"]
        self.combo_tipo = ctk.CTkComboBox(
            self.frame_filtros, values=opciones_tipo, width=160, command=lambda _e: self.buscar(),
        )
        self.combo_tipo.set("Todos")
        self.combo_tipo.pack(side="left", padx=(0, 15))

        self.lbl_tema = ctk.CTkLabel(self.frame_filtros, text="Tema:")
        self.lbl_tema.pack(side="left", padx=(20, 5))

        self.switch_tema = ctk.CTkSwitch(
            self.frame_filtros, text="",
            onvalue="light", offvalue="dark",
            command=self._cambiar_tema,
        )
        if self.theme.current == "light":
            self.switch_tema.select()
        self.switch_tema.pack(side="left")

    def _cambiar_tema(self):
        self.theme.toggle()

    def _poll_callbacks(self):
        try:
            while True:
                cb = self._callbacks.get_nowait()
                cb()
        except queue.Empty:
            pass
        self.after(50, self._poll_callbacks)

    def _programar(self, callback):
        """Encola un callback para ejecutar en el hilo principal."""
        self._callbacks.put(callback)

    def _crear_tabla(self):
        self.frame_tabla = ctk.CTkFrame(self)
        self.frame_tabla.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        ids = ["_id"] + [c[0] for c in COLUMNAS]
        self.tabla = ttk.Treeview(self.frame_tabla, columns=ids, show="headings")

        self.tabla.column("_id", width=0, stretch=False)
        self.tabla.heading("_id", text="")

        for cid, texto, ancho in COLUMNAS:
            self.tabla.heading(cid, text=texto, command=lambda c=cid: self._ordenar_por(c))
            self.tabla.column(cid, width=ancho, anchor="w")

        scroll_y = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(self.frame_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self._orden_ascending = True
        self._orden_col = "fecha_inicio"

    def _crear_barra_estado(self):
        self.frame_estado = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_estado.pack(fill="x", padx=10, pady=(0, 10))
        self.lbl_escaneo = ctk.CTkLabel(self.frame_estado, text="", anchor="w")
        self.lbl_escaneo.pack(side="left", padx=(0, 20))
        self.lbl_version = ctk.CTkLabel(self.frame_estado, text=f"V. {VERSION}", anchor="center")
        self.lbl_version.pack(side="left", expand=True)
        self.lbl_estado = ctk.CTkLabel(self.frame_estado, text="", anchor="e")
        self.lbl_estado.pack(side="right")

    def _ordenar_por(self, col):
        if self._orden_col == col:
            self._orden_ascending = not self._orden_ascending
        else:
            self._orden_col = col
            self._orden_ascending = False
        self.buscar()

    def escanear(self):
        self.lbl_escaneo.configure(text="Escaneando...")
        self.btn_escanear.configure(state="disabled")
        self.update_idletasks()

        def _ejecutar():
            try:
                n = sincronizar(on_progreso=lambda msg: self._programar(lambda m=msg: self.lbl_escaneo.configure(text=m)))
                self._programar(lambda: self.lbl_escaneo.configure(text=f"Último escaneo: {n} nuevos · Total en DB: {contar()}"))
            except Exception as e:
                msg = str(e)
                self._programar(lambda: self.lbl_escaneo.configure(text=f"Error al escanear: {msg}"))
            finally:
                self._programar(lambda: self.btn_escanear.configure(state="normal"))
            self._programar(self.buscar)

        threading.Thread(target=_ejecutar, daemon=True).start()

    def eliminar_seleccion(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.lbl_estado.configure(text="No hay registros seleccionados")
            return

        cantidad = len(seleccion)
        from tkinter import messagebox
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar {cantidad} registro{'s' if cantidad > 1 else ''}?\n\nEsta acción no se puede deshacer.",
        )
        if not confirmar:
            return

        ids = [int(self.tabla.item(item, "values")[0]) for item in seleccion]

        self.lbl_estado.configure(text="Eliminando...")
        self.btn_eliminar.configure(state="disabled")
        self.update_idletasks()

        def _ejecutar():
            eliminados = eliminar_registros(ids)
            self._programar(lambda: self._post_eliminar(eliminados))

        threading.Thread(target=_ejecutar, daemon=True).start()

    def _post_eliminar(self, eliminados):
        self.btn_eliminar.configure(state="normal")
        self.lbl_escaneo.configure(text=f"Eliminados: {eliminados} registros")
        self.buscar()

    def buscar(self):
        if self._busqueda_en_curso:
            return

        termino = self.entry.get().strip()
        maquina = self.combo_maquina.get()
        emisor = maquina if maquina != "Todas" else ""
        fecha_desde = self.entry_fecha_desde.get().strip()
        fecha_hasta = self.entry_fecha_hasta.get().strip()

        tipo_label = self.combo_tipo.get()
        tipo = TIPO_REVERSE.get(tipo_label, "")

        self._busqueda_en_curso = True
        self.btn_buscar.configure(state="disabled")

        def _ejecutar():
            filas = buscar(termino=termino, tipo=tipo, emisor=emisor, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
            self._programar(lambda: self._mostrar_resultados(filas))

        threading.Thread(target=_ejecutar, daemon=True).start()

    def _mostrar_resultados(self, filas):
        self._busqueda_en_curso = False
        self.btn_buscar.configure(state="normal")

        if self._orden_col and self._orden_col != "fecha_inicio":
            reverse = not self._orden_ascending
            filas.sort(key=lambda f: f.get(self._orden_col) or "", reverse=reverse)

        self.tabla.delete(*self.tabla.get_children())
        for i, f in enumerate(filas):
            valores = [f.get("id")]
            for cid, _texto, _ancho in COLUMNAS:
                v = f.get(cid)
                if cid == "tipo":
                    v = TIPO_LABEL.get(v, v) or ""
                elif cid == "numero_copias" and v is not None:
                    v = str(v)
                else:
                    v = v or ""
                valores.append(v)
            tag = "row_even" if i % 2 == 0 else "row_odd"
            self.tabla.insert("", "end", values=valores, tags=(tag,))

        self.lbl_estado.configure(text=f"{len(filas)} resultados")


if __name__ == "__main__":
    App().mainloop()
