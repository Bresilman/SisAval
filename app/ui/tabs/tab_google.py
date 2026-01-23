import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.google.google_config import GoogleConfigSubTab
from app.ui.tabs.subtabs.google.google_poles import GooglePolesSubTab

class GoogleTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=5, pady=5)

        self.sub_conf = GoogleConfigSubTab(nb, self.controller)
        nb.add(self.sub_conf, text="1. Configuração API")

        self.sub_poles = GooglePolesSubTab(nb, self.controller)
        nb.add(self.sub_poles, text="2. Matriz de Distâncias (Pólos)")
        
        # Futuro: Sub-aba "Places/Densidade"