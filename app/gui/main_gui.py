import customtkinter as ctk
import sqlite3
from app.database.db_manager import obtener_configuracion, actualizar_configuracion, obtener_consumo_acumulado_kwh

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppMonitoreo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Monitoreo de Consumo Energético Inteligente - ETITC")
        self.geometry("700x500")

        # Título
        self.lbl_titulo = ctk.CTkLabel(self, text="SISTEMA DE MONITOREO DE ENERGÍA (ETITC)", font=("Arial", 18, "bold"))
        self.lbl_titulo.pack(pady=15)

        # Frame de Datos
        self.frame_datos = ctk.CTkFrame(self)
        self.frame_datos.pack(pady=10, padx=20, fill="both", expand=True)

        self.lbl_kwh = ctk.CTkLabel(self.frame_datos, text="Consumo Acumulado: 0.0000 kWh", font=("Arial", 14))
        self.lbl_kwh.pack(pady=10)

        self.lbl_costo = ctk.CTkLabel(self.frame_datos, text="Costo Aproximado: $0 COP", font=("Arial", 14, "bold"), text_color="green")
        self.lbl_costo.pack(pady=10)

        # Configuración de Tarifa
        tarifa, presupuesto = obtener_configuracion()
        
        self.lbl_tarifa = ctk.CTkLabel(self.frame_datos, text="Tarifa ($/kWh):")
        self.lbl_tarifa.pack()
        self.entry_tarifa = ctk.CTkEntry(self.frame_datos)
        self.entry_tarifa.insert(0, str(tarifa))
        self.entry_tarifa.pack(pady=5)

        self.lbl_presupuesto = ctk.CTkLabel(self.frame_datos, text="Presupuesto Límite ($):")
        self.lbl_presupuesto.pack()
        self.entry_presupuesto = ctk.CTkEntry(self.frame_datos)
        self.entry_presupuesto.insert(0, str(presupuesto))
        self.entry_presupuesto.pack(pady=5)

        self.btn_guardar = ctk.CTkButton(self, text="Guardar Configuración", command=self.guardar_config)
        self.btn_guardar.pack(pady=10)

        # Bucle de actualización automática
        self.actualizar_pantalla()

    def guardar_config(self):
        try:
            tarifa = float(self.entry_tarifa.get())
            presupuesto = float(self.entry_presupuesto.get())
            actualizar_configuracion(tarifa, presupuesto)
            print("Configuración actualizada correctamente.")
        except ValueError:
            print("Error en valores ingresados.")

    def actualizar_pantalla(self):
        tarifa, presupuesto = obtener_configuracion()
        kwh = obtener_consumo_acumulado_kwh()
        costo = kwh * tarifa

        self.lbl_kwh.configure(text=f"Consumo Acumulado: {kwh:.4f} kWh")
        self.lbl_costo.configure(text=f"Costo Aproximado: ${costo:,.2f} COP")

        # Alerta visual si se supera el presupuesto
        if costo > presupuesto and presupuesto > 0:
            self.lbl_costo.configure(text_color="red")
        else:
            self.lbl_costo.configure(text_color="green")

        self.after(2000, self.actualizar_pantalla)
