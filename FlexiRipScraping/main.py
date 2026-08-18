from database.connection import crear_tabla
from gui.app import App

if __name__ == "__main__":
    crear_tabla()
    App().mainloop()
