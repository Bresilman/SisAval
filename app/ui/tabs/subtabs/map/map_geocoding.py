import tkinter as tk
from tkinter import ttk, messagebox

class MapGeocodingSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr = ttk.Frame(self, padding=20)
        fr.pack(fill='both', expand=True)

        ttk.Label(fr, text="Geocodificação Automática (Endereço -> Lat/Lon)", font=("Arial", 11, "bold")).pack(anchor='w')
        ttk.Label(fr, text="Necessário internet. Limite: 1 endereço/segundo.", foreground="gray").pack(anchor='w', pady=(0,10))

        # Config
        fr_cfg = ttk.LabelFrame(fr, text="Configuração", padding=10)
        fr_cfg.pack(fill='x')
        
        ttk.Label(fr_cfg, text="Coluna Endereço:").grid(row=0, column=0)
        self.cb_addr = ttk.Combobox(fr_cfg, state="readonly")
        self.cb_addr.grid(row=0, column=1, padx=5)

        ttk.Label(fr_cfg, text="Coluna Cidade (Opcional):").grid(row=0, column=2)
        self.cb_city = ttk.Combobox(fr_cfg, state="readonly")
        self.cb_city.grid(row=0, column=3, padx=5)
        
        ttk.Button(fr_cfg, text="▶ Iniciar Geocodificação", command=self._start).grid(row=0, column=4, padx=10)

        # Status
        self.lbl_status = ttk.Label(fr, text="Status: Aguardando...", font=("Arial", 10))
        self.lbl_status.pack(pady=20)
        self.progress = ttk.Progressbar(fr, mode='determinate')
        self.progress.pack(fill='x', padx=20)

    def refresh_cols(self):
        df = self.controller.data_handler.get_data()
        if df is not None:
            cols = list(df.columns)
            self.cb_addr['values'] = cols
            self.cb_city['values'] = ["(Nenhuma)"] + cols

    def _start(self):
        addr = self.cb_addr.get()
        city = self.cb_city.get()
        if not addr: return messagebox.showwarning("Aviso", "Selecione a coluna de endereço.")
        if city == "(Nenhuma)": city = None
        
        self.controller.acao_geocodificar(addr, city)

    def update_progress(self, current, total):
        self.progress['maximum'] = total
        self.progress['value'] = current
        self.lbl_status.config(text=f"Processando {current}/{total}...")