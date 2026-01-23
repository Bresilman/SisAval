import tkinter as tk
from tkinter import ttk

class ScraperConfigSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        ttk.Label(self, text="Configurações Aprendidas (JSON)", font=("Arial", 10, "bold")).pack(pady=10)
        
        self.txt_json = tk.Text(self, font=("Courier New", 10))
        self.txt_json.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Button(self, text="🔄 Recarregar Config", command=self.load_json).pack(pady=5)

    def load_json(self):
        import json
        import os
        if os.path.exists("scrapers_config.json"):
            with open("scrapers_config.json", 'r', encoding='utf-8') as f:
                content = f.read()
                self.txt_json.delete(1.0, 'end')
                self.txt_json.insert('end', content)
        else:
            self.txt_json.insert('end', "Nenhuma configuração salva ainda.")