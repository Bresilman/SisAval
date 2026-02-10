import tkinter as tk
from tkinter import ttk

class ValidationPrecision(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        
        # --- 1. Intervalo de Confiança (Confidence Interval) ---
        fr_ci = ttk.LabelFrame(self, text="Intervalo de Confiança (80%)")
        fr_ci.pack(fill="x", padx=10, pady=5)
        
        # Labels for display
        self.lbl_min = ttk.Label(fr_ci, text="Mínimo: -", font=("Segoe UI", 10))
        self.lbl_min.pack(side="left", padx=10, pady=5)
        
        self.lbl_central = ttk.Label(fr_ci, text="Central: -", font=("Segoe UI", 10, "bold"))
        self.lbl_central.pack(side="left", padx=10, pady=5)
        
        self.lbl_max = ttk.Label(fr_ci, text="Máximo: -", font=("Segoe UI", 10))
        self.lbl_max.pack(side="left", padx=10, pady=5)
        
        self.lbl_amplitude = ttk.Label(fr_ci, text="Amplitude: -", foreground="blue")
        self.lbl_amplitude.pack(side="right", padx=10)

        # --- 2. Grau de Precisão (Precision Degree) ---
        fr_degree = ttk.LabelFrame(self, text="Grau de Precisão (NBR 14.653-2)")
        fr_degree.pack(fill="x", padx=10, pady=5)
        
        self.lbl_degree = ttk.Label(fr_degree, text="AGUARDANDO CÁLCULO", font=("Segoe UI", 12, "bold"), foreground="gray")
        self.lbl_degree.pack(pady=10)
        
        # Explanation table
        fr_table = ttk.Frame(fr_degree)
        fr_table.pack(fill="x", padx=10, pady=5)
        
        # Simple static table for reference
        ttk.Label(fr_table, text="Grau I: Amplitude ≤ 50%").grid(row=0, column=0, sticky="w")
        ttk.Label(fr_table, text="Grau II: Amplitude ≤ 40%").grid(row=1, column=0, sticky="w")
        ttk.Label(fr_table, text="Grau III: Amplitude ≤ 30%").grid(row=2, column=0, sticky="w")

    def update_precision(self, stats):
        """
        Updates the UI with statistical results.
        Expected stats keys: 'IC_Min', 'Valor_Central', 'IC_Max' (or similar from StatsEngine)
        """
        if not stats: return

        # Extract values (handling both possible key naming conventions)
        val_central = stats.get('Valor_Central') or stats.get('valor_central', 0)
        val_min = stats.get('IC_Min') or stats.get('ic_min', 0)
        val_max = stats.get('IC_Max') or stats.get('ic_max', 0)
        
        if val_central == 0: return

        # Calculate Amplitude: (Max - Min) / Central
        amplitude = ((val_max - val_min) / val_central) * 100
        
        # Determine Degree
        if amplitude <= 30:
            degree = "GRAU III (Elevada Precisão)"
            color = "green"
        elif amplitude <= 40:
            degree = "GRAU II (Média Precisão)"
            color = "#ffd700" # Gold
        elif amplitude <= 50:
            degree = "GRAU I (Baixa Precisão)"
            color = "orange"
        else:
            degree = "FORA DOS CRITÉRIOS (> 50%)"
            color = "red"

        # Update Labels
        self.lbl_min.config(text=f"Mínimo: R$ {val_min:,.2f}")
        self.lbl_central.config(text=f"Central: R$ {val_central:,.2f}")
        self.lbl_max.config(text=f"Máximo: R$ {val_max:,.2f}")
        self.lbl_amplitude.config(text=f"Amplitude Total: {amplitude:.2f}%")
        
        self.lbl_degree.config(text=degree, foreground=color)
        
        return amplitude # Return for other modules if needed