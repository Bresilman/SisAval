import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import numpy as np

# Engines
from app.engines.scraper_engine import ScraperEngine
from app.engines.scraper_trainer import ScraperTrainer
from app.config import settings

class DataController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.data_handler = self.main.data_handler
        self.view = self.main.view
        
        # Data Specific Engines
        self.scraper_engine = ScraperEngine()
        self.scraper_trainer = ScraperTrainer()

    def atualizar_view(self):
        """Updates the Data Tab table and variable selectors."""
        df = self.data_handler.get_data()
        cols_num = self.data_handler.get_numeric_columns()
        self.view.tab_data.update_table(df, cols_num)

    # --- LOCAL FILE MANAGEMENT ---
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
        # Access the treeview inside the subtab
        try:
            sel = self.view.tab_data.subtab_table.tree.selection()
            if sel:
                # The iid in treeview corresponds to the DataFrame index
                idx = int(sel[0])
                self.data_handler.df.drop(index=idx, inplace=True)
                # Reset index to avoid holes
                self.data_handler.df.reset_index(drop=True, inplace=True)
                self.atualizar_view()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    # --- DATA ENGINEERING TOOLS ---
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
        """Removes statistical outliers based on Z-Score."""
        try:
            df = self.data_handler.df
            y_col = self.view.tab_data.combo_y.get()
            
            if not y_col or y_col not in df.columns:
                messagebox.showwarning("Aviso", "Selecione a variável Y na aba Dados primeiro.")
                return
            
            threshold = settings.STATS_ZSCORE_THRESHOLD
            
            col_data = df[y_col]
            z_scores = (col_data - col_data.mean()) / col_data.std()
            
            n_antes = len(df)
            # Keep only rows within threshold
            self.data_handler.df = df[z_scores.abs() < threshold].reset_index(drop=True)
            n_depois = len(self.data_handler.df)
            
            self.atualizar_view()
            
            removed = n_antes - n_depois
            if removed > 0:
                messagebox.showinfo("Saneamento", f"{removed} outliers removidos (Z > {threshold}).")
            else:
                messagebox.showinfo("Saneamento", "Nenhum outlier encontrado com este critério.")
                
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def acao_enriquecer_bairros(self):
        # Placeholder for Market Intelligence integration
        messagebox.showinfo("Info", "Funcionalidade conectada à Engine de Inteligência de Mercado.")

    # --- WEB SCRAPER & DUPLICATE HANDLING ---
    def acao_importar_web(self):
        # UX: Explica que precisa selecionar pasta
        folder = filedialog.askdirectory(title="Selecione a pasta onde os HTMLs estão salvos")
        
        # UX: Se cancelar, sugere o Robô
        if not folder: 
            if messagebox.askyesno("Ajuda", "Você não tem arquivos salvos?\n\nPara baixar anúncios da internet, use a aba 'Web Scraper' > 'Coletor Automático'.\n\nDeseja ir para lá agora?"):
                try:
                    self.main.view.notebook.select(self.main.view.tab_scraper)
                except: pass
            return

        try:
            # 1. Run Extraction Engine
            df_new = self.scraper_engine.extrair_de_pasta(folder)
            
            if df_new.empty:
                if messagebox.askyesno("Aviso", "Nenhum imóvel válido encontrado nesta pasta.\n\nDeseja abrir o Robô Coletor para baixar novos dados?"):
                    try:
                        self.main.view.notebook.select(self.main.view.tab_scraper)
                    except: pass
                return

            # 2. Show Staging Window (Popup)
            top = tk.Toplevel(self.view)
            top.title(f"Revisão de Importação ({len(df_new)} itens)")
            top.geometry("900x500")

            lbl = ttk.Label(top, text="Verifique os dados antes de importar:", font=("Arial", 10, "bold"))
            lbl.pack(pady=5)

            # Table
            cols = list(df_new.columns)
            tree = ttk.Treeview(top, columns=cols, show="headings", selectmode="extended")
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=100)
            
            # Insert data into Staging Table
            for i, row in df_new.iterrows():
                tree.insert("", "end", iid=i, values=list(row))
            
            tree.pack(fill='both', expand=True, padx=10)
            
            # Scrollbar
            sb = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
            sb.place(relx=1.0, rely=0.1, relheight=0.8, anchor='ne')
            tree.configure(yscrollcommand=sb.set)

            def delete_selected_staging():
                for item in tree.selection():
                    tree.delete(item)

            def confirm_import():
                # Get remaining indices from UI
                remaining_indices = [int(child) for child in tree.get_children()]
                
                if not remaining_indices:
                    top.destroy()
                    return

                # Filter original new DF based on UI selection
                df_to_import = df_new.loc[remaining_indices].copy()
                
                # --- DUPLICATE HANDLING LOGIC ---
                if self.data_handler.df is not None and not self.data_handler.df.empty:
                    current_df = self.data_handler.df
                    
                    # Create a "Fingerprint" key: Price + Area + (First 10 chars of Address)
                    # This avoids re-importing the same ad if it was scraped again
                    def create_fingerprint(d):
                        addr = d['Endereco'].astype(str).str.lower().str.slice(0, 15)
                        return d['Valor_Total'].astype(str) + "_" + d['Area'].astype(str) + "_" + addr

                    existing_keys = set(create_fingerprint(current_df))
                    incoming_keys = create_fingerprint(df_to_import)
                    
                    # Filter out rows where key already exists
                    df_unique = df_to_import[~incoming_keys.isin(existing_keys)]
                    
                    duplicates_count = len(df_to_import) - len(df_unique)
                    
                    if not df_unique.empty:
                        # Append new unique rows
                        self.data_handler.df = pd.concat([current_df, df_unique], ignore_index=True)
                        msg = f"{len(df_unique)} novos dados importados."
                        if duplicates_count > 0:
                            msg += f"\n({duplicates_count} duplicatas ignoradas)."
                        messagebox.showinfo("Sucesso", msg)
                    else:
                        messagebox.showinfo("Info", "Todos os dados selecionados já existem na tabela.")
                        
                else:
                    # First import
                    self.data_handler.df = df_to_import.reset_index(drop=True)
                    messagebox.showinfo("Sucesso", f"{len(df_to_import)} dados importados!")
                
                self.atualizar_view()
                top.destroy()

            # Buttons
            fr_btns = ttk.Frame(top, padding=10)
            fr_btns.pack(fill='x')
            ttk.Button(fr_btns, text="🗑️ Remover Selecionados", command=delete_selected_staging).pack(side='left')
            ttk.Button(fr_btns, text="✅ Confirmar e Mesclar", command=confirm_import).pack(side='right')

        except Exception as e:
            messagebox.showerror("Erro na Importação", str(e))

    def acao_calibrar_scraper(self):
        f = filedialog.askopenfilename(title="Selecione um HTML", filetypes=[("HTML", "*.html")])
        if not f: return
        
        top = tk.Toplevel(self.view)
        top.title("Calibrar Robô")
        top.geometry("400x300")
        
        ttk.Label(top, text=f"Arquivo: {os.path.basename(f)}").pack(pady=5)
        
        fr = ttk.Frame(top, padding=10); fr.pack()
        ttk.Label(fr, text="Preço (ex: 1350000):").grid(row=0, column=0)
        ent_price = ttk.Entry(fr); ent_price.grid(row=0, column=1)
        ttk.Label(fr, text="Área (ex: 660):").grid(row=1, column=0)
        ent_area = ttk.Entry(fr); ent_area.grid(row=1, column=1)
        
        def run():
            samples = {'price': ent_price.get(), 'area': ent_area.get()}
            site = "vivareal" if "viva" in f.lower() else "olx" if "olx" in f.lower() else "custom"
            ok, msg = self.scraper_trainer.auto_calibrate(f, site, samples)
            if ok: messagebox.showinfo("Sucesso", msg); top.destroy()
            else: messagebox.showerror("Falha", msg)
            
        ttk.Button(top, text="Treinar", command=run).pack(pady=20)