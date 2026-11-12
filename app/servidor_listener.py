from flask import Flask, request, jsonify
from app.database.db_manager import guardar_medicion

app = Flask(__name__)

@app.route('/api/medicion', methods=['POST'])
def recibir_medicion():
    datos = request.get_json()
    if not datos or 'corriente' not in datos:
        return jsonify({"status": "error", "message": "Datos inválidos"}), 400

    corriente = float(datos.get('corriente', 0.0))
    voltaje = 115.0  # Voltaje residencial estándar (V)
    potencia = corriente * voltaje

    guardar_medicion(corriente, potencia)
    print(f"[WiFi Recibido] Corriente: {corriente:.2f} A | Potencia: {potencia:.2f} W")
    
    return jsonify({"status": "success", "potencia_w": potencia}), 200

def run_server():
    # Se ejecuta en puerto 5000 escuchando en la red local
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
