import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from app.engines.urban_engine import UrbanEngine

class UrbanTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.engine = UrbanEngine()
        self._setup_ui()

    def _setup_ui(self):
        # Topo
        fr_top = ttk.Frame(self, padding=10)
        fr_top.pack(fill='x')
        ttk.Label(fr_top, text="Análise Urbana (Macro-Avaliação)", font=("Arial", 12, "bold")).pack(side='left')

        # Passos
        fr_steps = ttk.LabelFrame(self, text="Fluxo de Trabalho", padding=10)
        fr_steps.pack(fill='x', padx=10)

        ttk.Button(fr_steps, text="1. Carregar Dados do Scraper (Preços)", command=self._load_prices).pack(side='left', padx=5)
        ttk.Button(fr_steps, text="2. Baixar Infraestrutura (OSM)", command=self._download_infra).pack(side='left', padx=5)
        ttk.Button(fr_steps, text="3. Gerar Ranking de Bairros", command=self._calc_ranking).pack(side='left', padx=5)

        # Tabela de Resultados
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botão Exportar
        ttk.Button(self, text="Usar Ranking na Regressão", command=self._export_to_regression).pack(pady=10)

    def _load_prices(self):
        # Pega dados do DataHandler (que veio do Scraper)
        df = self.controller.data_handler.get_data()
        if df is None:
            messagebox.showwarning("Aviso", "Carregue dados na aba 1 primeiro.")
            return
        
        self.stats_precos = self.engine.calcular_preco_medio_bairro(df)
        if self.stats_precos is not None:
            self._update_table(self.stats_precos.reset_index())
            messagebox.showinfo("Sucesso", f"Preços calculados para {len(self.stats_precos)} bairros.")

    def _download_infra(self):
        messagebox.showinfo("Aviso", "Baixando dados do OpenStreetMap... Isso pode demorar.")
        # Em produção, usar Threading aqui!
        resumo, pois = self.engine.contar_infraestrutura()
        msg = "Infraestrutura encontrada (Cidade toda):\n"
        for k, v in resumo.items():
            msg += f"{k}: {v}\n"
        messagebox.showinfo("OSM", msg)

    def _calc_ranking(self):
        # Aqui cruzaria os dados. Por enquanto mostra os preços.
        pass

    def _update_table(self, df):
        self.tree.delete(*self.tree.get_children())
        cols = list(df.columns)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def _export_to_regression(self):
        # Cria a variável "Indice_Valor_Bairro" na aba de dados principal
        # baseada nesse ranking
        pass