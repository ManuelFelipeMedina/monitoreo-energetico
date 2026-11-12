const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Inicializar Base de Datos SQLite
const db = new sqlite3.Database('./monitoreo_web.db', (err) => {
    if (err) console.error("Error BD:", err.message);
    else console.log("Conectado a la Base de Datos SQLite.");
});

// Crear Tablas (Actualizado con estrato y umbral de potencia)
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS dispositivos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, potencia_watts REAL, horas_uso_dia REAL)`);
    db.run(`CREATE TABLE IF NOT EXISTS configuraciones (id INTEGER PRIMARY KEY CHECK (id = 1), tarifa_kwh REAL, presupuesto_limite REAL, estrato INTEGER DEFAULT 4, umbral_potencia REAL DEFAULT 1200.0)`);
    db.run(`INSERT OR IGNORE INTO configuraciones (id, tarifa_kwh, presupuesto_limite, estrato, umbral_potencia) VALUES (1, 800.0, 50000.0, 4, 1200.0)`);
    db.run(`CREATE TABLE IF NOT EXISTS mediciones (id INTEGER PRIMARY KEY AUTOINCREMENT, corriente REAL, potencia_watts REAL, fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP)`);
});

// --- RUTAS DE LA API REST ---

// 1. Endpoint que recibe las lecturas WiFi del ESP32 (Flexible para corriente o potencia)
app.post('/api/medicion', (req, res) => {
    const { corriente, potencia, Potencia, Irms } = req.body;
    
    // Capturar cualquier variable de potencia o corriente que envíe el ESP32
    let valorPotencia = potencia !== undefined ? potencia : (Potencia !== undefined ? Potencia : undefined);
    let valorCorriente = corriente !== undefined ? corriente : (Irms !== undefined ? Irms : undefined);

    // Si viene corriente pero no potencia, calculamos con 115V (estándar Colombia)
    if (valorPotencia === undefined && valorCorriente !== undefined) {
        valorPotencia = valorCorriente * 115.0;
    } 
    // Si viene potencia pero no corriente, calculamos la corriente estimada
    else if (valorCorriente === undefined && valorPotencia !== undefined) {
        valorCorriente = valorPotencia / 115.0;
    }

    if (valorPotencia === undefined) {
        return res.status(400).json({ error: "Faltan datos de potencia o corriente en la petición" });
    }

    db.run(`INSERT INTO mediciones (corriente, potencia_watts) VALUES (?, ?)`, [valorCorriente || 0, valorPotencia], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        
        // Transmitir en tiempo real a la interfaz Web mediante WebSockets
        io.emit('nueva_medicion', { 
            corriente: valorCorriente, 
            potencia: valorPotencia, 
            fecha: new Date() 
        });
        
        res.json({ status: "ok", potencia_watts: valorPotencia });
    });
});

// 2. Obtener Configuración (Incluyendo estrato y umbral de potencia)
app.get('/api/configuracion', (req, res) => {
    db.get(`SELECT * FROM configuraciones WHERE id = 1`, [], (err, row) => {
        res.json(row || { tarifa_kwh: 800, presupuesto_limite: 50000, estrato: 4, umbral_potencia: 1200.0 });
    });
});

// Actualizar Configuración (Incluyendo estrato y umbral de potencia)
app.post('/api/configuracion', (req, res) => {
    const { tarifa_kwh, presupuesto_limite, estrato, umbral_potencia } = req.body;
    db.run(`UPDATE configuraciones SET tarifa_kwh = ?, presupuesto_limite = ?, estrato = ?, umbral_potencia = ? WHERE id = 1`, 
    [tarifa_kwh, presupuesto_limite, estrato, umbral_potencia], (err) => {
        if (err) return res.status(500).json({ error: err.message });
        io.emit('config_actualizada', { tarifa_kwh, presupuesto_limite, estrato, umbral_potencia });
        res.json({ status: "actualizado" });
    });
});

// 3. CRUD Dispositivos
app.get('/api/dispositivos', (req, res) => {
    db.all(`SELECT * FROM dispositivos`, [], (err, rows) => res.json(rows));
});

app.post('/api/dispositivos', (req, res) => {
    const { nombre, potencia_watts, horas_uso_dia } = req.body;
    db.run(`INSERT INTO dispositivos (nombre, potencia_watts, horas_uso_dia) VALUES (?, ?, ?)`, 
    [nombre, potencia_watts, horas_uso_dia], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.json({ id: this.lastID, status: "creado" });
    });
});

app.delete('/api/dispositivos/:id', (req, res) => {
    db.run(`DELETE FROM dispositivos WHERE id = ?`, [req.params.id], (err) => {
        res.json({ status: "eliminado" });
    });
});

// Iniciar Servidor Web
const PORT = 3000;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`\n==================================================`);
    console.log(` Aplicación Web de Monitoreo corriendo en http://localhost:${PORT}`);
    console.log(` ESP32 Endpoint: http://<TU_IP_LOCAL>:${PORT}/api/medicion`);
    console.log(`==================================================\n`);
});