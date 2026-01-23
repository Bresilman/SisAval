import tkinter as tk
from tkinter import ttk, filedialog
import os

class ScraperCalibrateSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.inputs = {}
        self._setup_ui()

    def _setup_ui(self):
        # Header
        ttk.Label(self, text="Treinador de Perfis de Scraping", font=("Arial", 12, "bold")).pack(pady=10)
        
        # 1. File Selection
        fr_file = ttk.LabelFrame(self, text="1. Arquivo de Exemplo (HTML)", padding=10)
        fr_file.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(fr_file, text="📂 Carregar HTML", command=self.controller.acao_carregar_html_treino).pack(side='left')
        self.lbl_file = ttk.Label(fr_file, text="Nenhum arquivo", foreground="gray")
        self.lbl_file.pack(side='left', padx=10)

        # 2. Profile Name
        fr_name = ttk.Frame(self)
        fr_name.pack(fill='x', padx=10, pady=5)
        ttk.Label(fr_name, text="Nome do Perfil (ex: OLX_2026):").pack(side='left')
        self.ent_profile = ttk.Entry(fr_name)
        self.ent_profile.pack(side='left', padx=5, fill='x', expand=True)

        # 3. Fields to Train
        fr_fields = ttk.LabelFrame(self, text="2. Identifique os Dados (O que você vê na tela?)", padding=10)
        fr_fields.pack(fill='both', expand=True, padx=10, pady=5)

        fields = [
            ("Valor_Total", "Preço (ex: 1.350.000)"),
            ("Area", "Área (ex: 660)"),
            ("Quartos", "Quartos (ex: 3)"),
            ("Vagas", "Vagas (ex: 2)"),
            ("Bairro", "Bairro (ex: Ellery)"),
            ("Endereco", "Endereço (ex: Rua A, 100)")
        ]

        for i, (key, label) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(fr_fields, text=label).grid(row=row, column=col, sticky='e', padx=5, pady=5)
            ent = ttk.Entry(fr_fields)
            ent.grid(row=row, column=col+1, sticky='w', padx=5, pady=5)
            self.inputs[key] = ent

        # 4. Action
        ttk.Button(self, text="🧠 TREINAR E SALVAR PERFIL", command=self._train).pack(fill='x', padx=20, pady=15)

    def _train(self):
        profile_name = self.ent_profile.get().strip()
        if not profile_name:
            # Auto-generate name if empty based on file
            if self.controller.scraper_ctrl.current_html_path:
                base = os.path.basename(self.controller.scraper_ctrl.current_html_path)
                profile_name = base.split('.')[0]
            else:
                profile_name = "Perfil_Novo"

        # Collect data
        data = {}
        for key, ent in self.inputs.items():
            val = ent.get().strip()
            if val: data[key] = val

        self.controller.acao_executar_treinamento(profile_name, data)