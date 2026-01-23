import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

class ScraperCrawlerSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_main = ttk.Frame(self, padding=20)
        fr_main.pack(fill='both', expand=True)

        ttk.Label(fr_main, text="Robô de Coleta Automática (Crawler)", font=("Arial", 12, "bold")).pack(anchor='w', pady=10)
        ttk.Label(fr_main, text="Este robô abre o navegador, visita as páginas e salva os HTMLs para você.", foreground="gray").pack(anchor='w', pady=(0,10))

        # Inputs
        fr_inp = ttk.LabelFrame(fr_main, text="Configuração da Coleta", padding=10)
        fr_inp.pack(fill='x')

        ttk.Label(fr_inp, text="URL da Busca (Copie do navegador):").pack(anchor='w')
        self.ent_url = ttk.Entry(fr_inp)
        self.ent_url.pack(fill='x', pady=5)
        self.ent_url.insert(0, "https://www.olx.com.br/imoveis/venda/estado-ce/fortaleza-e-regiao?q=ellery")

        fr_grid = ttk.Frame(fr_inp)
        fr_grid.pack(fill='x', pady=5)
        
        ttk.Label(fr_grid, text="Qtd. Páginas:").pack(side='left')
        self.sp_paginas = ttk.Spinbox(fr_grid, from_=1, to=50, width=5)
        self.sp_paginas.set(1)
        self.sp_paginas.pack(side='left', padx=5)

        ttk.Label(fr_grid, text="Pasta Destino:").pack(side='left', padx=(20, 5))
        self.ent_pasta = ttk.Entry(fr_grid, width=30)
        self.ent_pasta.insert(0, "paginas_coletadas")
        self.ent_pasta.pack(side='left')
        ttk.Button(fr_grid, text="📂", width=3, command=self._escolher_pasta).pack(side='left', padx=2)

        # Log
        self.txt_log = tk.Text(fr_main, height=10, font=("Courier", 9), bg="#f0f0f0")
        self.txt_log.pack(fill='both', expand=True, pady=10)

        # Button
        ttk.Button(fr_main, text="▶ INICIAR COLETA", command=self._start_crawler).pack(fill='x', pady=5)

    def _escolher_pasta(self):
        d = filedialog.askdirectory()
        if d:
            self.ent_pasta.delete(0, tk.END)
            self.ent_pasta.insert(0, d)

    def _start_crawler(self):
        url = self.ent_url.get()
        pags = self.sp_paginas.get()
        pasta = self.ent_pasta.get()
        
        if not url: return messagebox.showwarning("Aviso", "Cole uma URL primeiro.")
        
        self.controller.acao_iniciar_crawler(url, pags, pasta, self.log_message)

    def log_message(self, msg):
        self.txt_log.insert(tk.END, f"{msg}\n")
        self.txt_log.see(tk.END)