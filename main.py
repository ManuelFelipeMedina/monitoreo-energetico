import threading
from app.database.db_manager import init_db
from app.servidor_listener import run_server
from app.gui.main_gui import AppMonitoreo

if __name__ == "__main__":
    # 1. Inicializar la Base de Datos SQLite
    init_db()

    # 2. Iniciar el Servidor Listener Flask en un hilo independiente
    hilo_servidor = threading.Thread(target=run_server, daemon=True)
    hilo_servidor.start()

    # 3. Lanzar la Interfaz Gráfica CustomTkinter
    app = AppMonitoreo()
    app.mainloop()
