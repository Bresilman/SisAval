import tkinter as tk
from tkinter import ttk, messagebox

class MapVarsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr = ttk.Frame(self, padding=20)
        fr.pack(fill='both', expand=True)

        ttk.Label(fr, text="Criação de Variáveis Espaciais", font=("Arial", 11, "bold")).pack(anchor='w')
        ttk.Label(fr, text="1. Vá na aba 'Visualização' e clique com botão direito no mapa para marcar um ponto de referência (Polo).", wraplength=600).pack(anchor='w', pady=5)
        ttk.Label(fr, text="2. Defina um nome (ex: 'Dist_Praia') e clique em Calcular.", wraplength=600).pack(anchor='w')

        # Form
        fr_form = ttk.LabelFrame(fr, text="Novo Polo Valorizante", padding=15)
        fr_form.pack(fill='x', pady=15)

        ttk.Label(fr_form, text="Nome da Nova Variável:").pack(side='left')
        self.ent_name = ttk.Entry(fr_form, width=20)
        self.ent_name.pack(side='left', padx=5)
        self.ent_name.insert(0, "Dist_Polo")

        ttk.Button(fr_form, text="📏 Calcular Distâncias e Adicionar ao Excel", command=self._calc).pack(side='left', padx=10)

    def _calc(self):
        target = self.controller.current_map_target
        if not target:
            return messagebox.showwarning("Aviso", "Nenhum ponto selecionado no mapa. Volte na aba visualização e clique com botão direito.")
        
        name = self.ent_name.get()
        if not name: return
        
        self.controller.acao_criar_variavel_distancia(name, target[0], target[1])