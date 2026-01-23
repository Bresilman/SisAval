import tkinter as tk
from tkinter import ttk

class SettingsStatsSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        fr_main = ttk.Frame(self, padding=20)
        fr_main.pack(fill='both', expand=True)

        # 1. Regression Parameters
        fr_reg = ttk.LabelFrame(fr_main, text="Parâmetros de Regressão", padding=15)
        fr_reg.pack(fill='x', pady=10)

        ttk.Label(fr_reg, text="Nível de Confiança:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.cb_conf = ttk.Combobox(fr_reg, values=["80%", "90%", "95%", "99%"], state="readonly", width=10)
        self.cb_conf.set("80%")
        self.cb_conf.grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(fr_reg, text="Nível de Significância (Teste F):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.cb_sig = ttk.Combobox(fr_reg, values=["1%", "5%", "10%"], state="readonly", width=10)
        self.cb_sig.set("5%")
        self.cb_sig.grid(row=1, column=1, sticky='w', padx=5)

        # 2. Outlier Detection
        fr_out = ttk.LabelFrame(fr_main, text="Critério de Saneamento (Outliers)", padding=15)
        fr_out.pack(fill='x', pady=10)

        ttk.Label(fr_out, text="Limite Z-Score (Desvios Padrão):").grid(row=0, column=0, sticky='e', padx=5)
        self.sp_zscore = ttk.Spinbox(fr_out, from_=1.0, to=4.0, increment=0.1, width=8)
        self.sp_zscore.set(2.0) # Default
        self.sp_zscore.grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(fr_out, text="* Valor padrão é 2.0 (aprox. 95% dos dados). \n* Use 1.64 para ser mais rigoroso (90%).", foreground="gray", font=("Arial", 8)).grid(row=1, column=0, columnspan=2, sticky='w', pady=5)

    def get_data(self):
        # Convert percentages to decimals
        conf_map = {"80%": 0.20, "90%": 0.10, "95%": 0.05, "99%": 0.01} # Alpha for intervals
        sig_map = {"1%": 0.01, "5%": 0.05, "10%": 0.10}
        
        return {
            "alpha_intervalo": conf_map.get(self.cb_conf.get(), 0.20),
            "alpha_significancia": sig_map.get(self.cb_sig.get(), 0.05),
            "z_score_limit": float(self.sp_zscore.get())
        }