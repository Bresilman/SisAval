import tkinter as tk
from tkinter import ttk
from app.ui.tabs.subtabs.report_config import ReportConfigSubTab

class ReportTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Notebook for organization
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Configuration (Texts)
        self.sub_config = ReportConfigSubTab(nb)
        nb.add(self.sub_config, text="1. Redação do Laudo")

        # Tab 2: Options (Checkboxes)
        self.fr_opts = ttk.Frame(nb, padding=20)
        nb.add(self.fr_opts, text="2. Elementos Opcionais")

        self.chk_data = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.fr_opts, text="Incluir Tabela de Amostra", variable=self.chk_data).pack(anchor='w', pady=5)
        
        self.chk_plots = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.fr_opts, text="Incluir Gráficos de Diagnóstico", variable=self.chk_plots).pack(anchor='w', pady=5)

        # Bottom Action Bar
        fr_bot = ttk.Frame(self, padding=10)
        fr_bot.pack(fill='x')
        
        ttk.Button(fr_bot, text="📄 GERAR LAUDO PDF", command=self.controller.acao_gerar_pdf).pack(side='right', fill='x', expand=True)