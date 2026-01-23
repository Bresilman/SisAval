import tkinter as tk
from tkinter import ttk, filedialog

class SettingsIdentSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        fr_main = ttk.Frame(self, padding=20)
        fr_main.pack(fill='both', expand=True)

        # 1. Professional Info
        fr_prof = ttk.LabelFrame(fr_main, text="Dados do Avaliador (Cabeçalho do Laudo)", padding=15)
        fr_prof.pack(fill='x', pady=10)

        grid_opts = {'sticky': 'w', 'padx': 5, 'pady': 5}
        
        ttk.Label(fr_prof, text="Nome Completo:").grid(row=0, column=0, **grid_opts)
        self.ent_name = ttk.Entry(fr_prof, width=40)
        self.ent_name.grid(row=0, column=1, **grid_opts)

        ttk.Label(fr_prof, text="Título Profissional:").grid(row=1, column=0, **grid_opts)
        self.ent_job = ttk.Entry(fr_prof, width=40)
        self.ent_job.insert(0, "Engenheiro Civil / Arquiteto")
        self.ent_job.grid(row=1, column=1, **grid_opts)

        ttk.Label(fr_prof, text="Registro (CREA/CAU):").grid(row=2, column=0, **grid_opts)
        self.ent_crea = ttk.Entry(fr_prof, width=20)
        self.ent_crea.grid(row=2, column=1, **grid_opts)

        ttk.Label(fr_prof, text="Empresa / Escritório:").grid(row=3, column=0, **grid_opts)
        self.ent_company = ttk.Entry(fr_prof, width=40)
        self.ent_company.grid(row=3, column=1, **grid_opts)

        # 2. Report Info
        fr_rep = ttk.LabelFrame(fr_main, text="Padrões do Relatório", padding=15)
        fr_rep.pack(fill='x', pady=10)

        ttk.Label(fr_rep, text="Título Padrão:").grid(row=0, column=0, **grid_opts)
        self.ent_title = ttk.Entry(fr_rep, width=40)
        self.ent_title.insert(0, "LAUDO DE AVALIAÇÃO DE IMÓVEL URBANO")
        self.ent_title.grid(row=0, column=1, **grid_opts)

        ttk.Label(fr_rep, text="Cidade/Data:").grid(row=1, column=0, **grid_opts)
        self.ent_city = ttk.Entry(fr_rep, width=30)
        self.ent_city.insert(0, "Fortaleza - CE")
        self.ent_city.grid(row=1, column=1, **grid_opts)

    def get_data(self):
        return {
            "avaliador": self.ent_name.get(),
            "titulo_profissional": self.ent_job.get(),
            "crea": self.ent_crea.get(),
            "empresa": self.ent_company.get(),
            "titulo_laudo": self.ent_title.get(),
            "cidade": self.ent_city.get()
        }