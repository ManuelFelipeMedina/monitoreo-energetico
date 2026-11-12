-- 1. Tabla de Dispositivos (Catálogo)
CREATE TABLE IF NOT EXISTS dispositivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    potencia_watts REAL NOT NULL,
    horas_uso_dia REAL NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Configuraciones (Tarifa y Presupuesto)
CREATE TABLE IF NOT EXISTS configuraciones (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    tarifa_kwh REAL DEFAULT 800.0,
    presupuesto_limite REAL DEFAULT 50000.0
);

INSERT OR IGNORE INTO configuraciones (id, tarifa_kwh, presupuesto_limite) VALUES (1, 800.0, 50000.0);

-- 3. Tabla de Mediciones (Captura en Tiempo Real del ESP32)
CREATE TABLE IF NOT EXISTS mediciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voltaje REAL DEFAULT 115.0,
    corriente REAL NOT NULL,
    potencia_watts REAL NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
);