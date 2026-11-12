import sqlite3
from datetime import datetime

DB_NAME = "monitoreo_energia.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabla de mediciones recibidas por WiFi del ESP32
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corriente REAL,
            potencia_watts REAL,
            fecha_hora TEXT
        )
    ''')
    # Tabla de tarifa y presupuesto configurado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuraciones (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            tarifa_kwh REAL DEFAULT 800.0,
            presupuesto_limite REAL DEFAULT 50000.0
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO configuraciones (id, tarifa_kwh, presupuesto_limite) VALUES (1, 800.0, 50000.0)")
    conn.commit()
    conn.close()

def guardar_medicion(corriente, potencia):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mediciones (corriente, potencia_watts, fecha_hora) VALUES (?, ?, ?)",
        (corriente, potencia, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def obtener_configuracion():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT tarifa_kwh, presupuesto_limite FROM configuraciones WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row if row else (800.0, 50000.0)

def actualizar_configuracion(tarifa, presupuesto):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE configuraciones SET tarifa_kwh = ?, presupuesto_limite = ? WHERE id = 1", (tarifa, presupuesto))
    conn.commit()
    conn.close()

def obtener_consumo_acumulado_kwh():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Suma aproximada en Watts convertida a kWh
    cursor.execute("SELECT SUM(potencia_watts) FROM mediciones")
    suma_watts = cursor.fetchone()[0] or 0.0
    conn.close()
    # Suponiendo mediciones periódicas cada 2 segundos
    kwh = (suma_watts * 2) / 3600000.0
    return kwh
