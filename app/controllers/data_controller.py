import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from app.engines.scraper_engine import ScraperEngine
from app.engines.scraper_trainer import ScraperTrainer
from app.config import settings

class DataController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.data_handler = self.main.data_handler
        self.view = self.main.view
        
        self.scraper_engine = ScraperEngine()
        self.scraper_trainer = ScraperTrainer()

    def atualizar_view(self):
        df = self.data_handler.get_data()
        cols_num = self.data_handler.get_numeric_columns()
        self.view.tab_data.update_table(df, cols_num)

    def carregar(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv")])
            if path:
                self.data_handler.carregar_arquivo(path)
                self.atualizar_view()
        except Exception as e:
            messagebox.showerror("Erro ao carregar", str(e))

    def exemplo(self):
        self.data_handler.gerar_dados_exemplo()
        self.atualizar_view()

    def excluir_dado(self):
        sel = self.view.tab_data.tree.selection()
        if sel:
            idx = int(sel[0])
            self.data_handler.df.drop(index=idx, inplace=True)
            self.atualizar_view()

    def transformar(self, col, tipo):
        try:
            nome = self.data_handler.aplicar_transformacao(col, tipo)
            self.atualizar_view()
            messagebox.showinfo("Sucesso", f"Variável '{nome}' criada!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def codificar_variavel(self, col, mapping):
        try:
            new_col = self.data_handler.map_categorical_to_numeric(col, mapping)
            self.atualizar_view()
            messagebox.showinfo("Sucesso", f"Mapeamento criado: {new_col}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def sanear_dados(self):
        try:
            df = self.data_handler.df
            y_col = self.view.tab_data.combo_y.get()
            if not y_col or y_col not in df.columns:
                messagebox.showwarning("Aviso", "Selecione a variável Y na aba Dados primeiro.")
                return
            
            # USE CONFIG VALUE
            threshold = settings.STATS_ZSCORE_THRESHOLD
            
            col_data = df[y_col]
            z_scores = (col_data - col_data.mean()) / col_data.std()
            
            n_antes = len(df)
            self.data_handler.df = df[z_scores.abs() < threshold]
            n_depois = len(self.data_handler.df)
            
            self.atualizar_view()
            messagebox.showinfo("Info", f"{n_antes - n_depois} outliers removidos (Z > {threshold}).")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def acao_importar_web(self):
        folder = filedialog.askdirectory(title="Selecione a pasta com os arquivos HTML")
        if not folder: return

        try:
            df_new = self.scraper_engine.extrair_de_pasta(folder)
            
            if df_new.empty:
                messagebox.showwarning("Aviso", "Nenhum imóvel válido encontrado nos HTMLs.")
                return

            top = tk.Toplevel(self.view)
            top.title(f"Revisão de Importação ({len(df_new)} itens)")
            top.geometry("900x500")

            lbl = ttk.Label(top, text="Verifique os dados antes de importar (Desmarque os ruins):", font=("Arial", 10, "bold"))
            lbl.pack(pady=5)

            cols = list(df_new.columns)
            tree = ttk.Treeview(top, columns=cols, show="headings", selectmode="extended")
            
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=100)
            
            for i, row in df_new.iterrows():
                tree.insert("", "end", iid=i, values=list(row))
            
            tree.pack(fill='both', expand=True, padx=10)
            
            sb_y = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
            sb_y.place(relx=1.0, rely=0.1, relheight=0.8, anchor='ne')
            tree.configure(yscrollcommand=sb_y.set)

            def delete_selected():
                selected = tree.selection()
                for item in selected:
                    tree.delete(item)

            def confirm_import():
                remaining_indices = []
                for child in tree.get_children():
                    remaining_indices.append(int(child))
                
                if not remaining_indices:
                    top.destroy()
                    return

                df_final = df_new.loc[remaining_indices].copy()
                
                if self.data_handler.df is not None and not self.data_handler.df.empty:
                    self.data_handler.df = pd.concat([self.data_handler.df, df_final], ignore_index=True)
                else:
                    self.data_handler.df = df_final
                
                self.atualizar_view()
                top.destroy()
                messagebox.showinfo("Sucesso", f"{len(df_final)} dados importados para análise!")

            fr_btns = ttk.Frame(top, padding=10)
            fr_btns.pack(fill='x')
            
            ttk.Button(fr_btns, text="🗑️ Remover Selecionados", command=delete_selected).pack(side='left')
            ttk.Button(fr_btns, text="✅ Confirmar Importação", command=confirm_import).pack(side='right')

        except Exception as e:
            messagebox.showerror("Erro na Importação", str(e))

    def acao_calibrar_scraper(self):
        f = filedialog.askopenfilename(title="Selecione um HTML para treinar", filetypes=[("HTML", "*.html")])
        if not f: return
        
        top = tk.Toplevel(self.view)
        top.title("Calibrar Robô")
        top.geometry("400x300")
        
        ttk.Label(top, text=f"Arquivo: {os.path.basename(f)}").pack(pady=5)
        ttk.Label(top, text="Digite o valor EXATO que você vê na página:").pack()
        
        fr = ttk.Frame(top, padding=10); fr.pack()
        
        ttk.Label(fr, text="Preço (ex: 1.350.000):").grid(row=0, column=0)
        ent_price = ttk.Entry(fr); ent_price.grid(row=0, column=1)
        
        ttk.Label(fr, text="Área (ex: 660):").grid(row=1, column=0)
        ent_area = ttk.Entry(fr); ent_area.grid(row=1, column=1)
        
        def run_train():
            samples = {'price': ent_price.get(), 'area': ent_area.get()}
            site_name = "vivareal" if "viva" in f.lower() else "olx" if "olx" in f.lower() else "custom"
            
            ok, config = self.scraper_trainer.auto_calibrate(f, site_name, samples)
            if ok:
                messagebox.showinfo("Sucesso", f"Robô aprendeu a ler {site_name}!\nConfig salva.")
                top.destroy()
            else:
                messagebox.showerror("Falha", "Não consegui encontrar esses valores no HTML.")
                
        ttk.Button(top, text="Ensinar Robô", command=run_train).pack(pady=20)