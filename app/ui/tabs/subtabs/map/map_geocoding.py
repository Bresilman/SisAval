import tkinter as tk
from tkinter import ttk, messagebox
import threading

class MapGeocoding(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- 1. Settings ---
        cfg_frame = ttk.LabelFrame(self, text="Configuração de Geocodificação")
        cfg_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Label(cfg_frame, text="Coluna de Endereço:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_addr = ttk.Combobox(cfg_frame)
        self.combo_addr.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(cfg_frame, text="Cidade Padrão:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_city = ttk.Entry(cfg_frame)
        self.ent_city.insert(0, "Fortaleza, CE")
        self.ent_city.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Button(cfg_frame, text="Carregar Colunas", command=self.load_columns).grid(row=0, column=4, padx=5)

        # --- 2. Action ---
        act_frame = ttk.Frame(self)
        act_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.btn_run = ttk.Button(act_frame, text="Iniciar Geocodificação em Lote", command=self.run_geocoding)
        self.btn_run.pack(side="left", fill="x", expand=True)

        self.progress = ttk.Progressbar(act_frame, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=10)

        # --- 3. Log ---
        log_frame = ttk.LabelFrame(self, text="Log de Processamento")
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        self.txt_log = tk.Text(log_frame, height=10)
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

    def load_columns(self):
        # Access DataHandler through main controller
        handler = None
        if hasattr(self.controller, 'data_handler'): handler = self.controller.data_handler
        elif hasattr(self.controller, 'main') and hasattr(self.controller.main, 'data_handler'):
            handler = self.controller.main.data_handler
            
        if handler:
            cols = handler.get_columns() # Assuming this method exists or similar
            self.combo_addr['values'] = cols
            if 'endereco' in cols: self.combo_addr.set('endereco')
            elif 'Address' in cols: self.combo_addr.set('Address')
        else:
            self.txt_log.insert("end", "Erro: DataHandler não disponível.\n")

    def run_geocoding(self):
        col = self.combo_addr.get()
        if not col:
            messagebox.showwarning("Aviso", "Selecione a coluna que contém o endereço.")
            return
            
        self.txt_log.insert("end", f"Iniciando geocodificação para coluna: {col}...\n")
        self.progress['value'] = 0
        
        # Mocking the process for UI demonstration
        # In production, use self.controller.geocoding_engine.process(df, col)
        self.txt_log.insert("end", "Conectando ao Google Maps API (Simulação)...\n")
        self.after(1000, lambda: self.progress.step(50))
        self.after(2000, lambda: self.finish_mock())

    def finish_mock(self):
        self.progress['value'] = 100
        self.txt_log.insert("end", "Sucesso: 15 endereços convertidos em coordenadas.\n")
        messagebox.showinfo("Sucesso", "Geocodificação concluída. Atualize o mapa na aba Visualização.")