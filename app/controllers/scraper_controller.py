from tkinter import filedialog, messagebox
import pandas as pd
import os
from app.engines.scraper_engine import ScraperEngine
from app.engines.scraper_trainer import ScraperTrainer

class ScraperController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.scraper_engine = ScraperEngine()
        self.scraper_trainer = ScraperTrainer()
        self.temp_df = None
        self.current_html_path = None

    def acao_importar_pasta(self):
        folder = filedialog.askdirectory(title="Selecione pasta com HTMLs")
        if not folder: return

        try:
            self.temp_df = self.scraper_engine.extrair_de_pasta(folder)
            if self.temp_df.empty:
                messagebox.showwarning("Aviso", "Nenhum dado encontrado.")
            else:
                self.main.view.tab_scraper.sub_run.update_table(self.temp_df)
                messagebox.showinfo("Sucesso", f"{len(self.temp_df)} arquivos lidos.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def acao_enviar_para_analise(self):
        if self.temp_df is None or self.temp_df.empty: return

        tree = self.main.view.tab_scraper.sub_run.tree
        # Only get selected items (or all if none selected? standard is usually selection)
        # Let's assume if selection exists, take selection. Else take all.
        sel_ids = tree.selection()
        
        if sel_ids:
            # iid in treeview corresponds to index in temp_df
            ids = [int(item) for item in sel_ids]
            new_df = self.temp_df.loc[ids].copy()
        else:
            if not messagebox.askyesno("Confirmar", "Nenhum item selecionado. Deseja importar TUDO?"):
                return
            new_df = self.temp_df.copy()

        # DUPLICATE HANDLING
        if self.main.data_handler.df is not None and not self.main.data_handler.df.empty:
            current = self.main.data_handler.df
            
            # Create a unique key for comparison (Price + Area + rough Address)
            # Normalize address for comparison
            def make_key(df):
                return df['Valor_Total'].astype(str) + "_" + df['Area'].astype(str) + "_" + df['Endereco'].str.slice(0, 10)

            current['__key'] = make_key(current)
            new_df['__key'] = make_key(new_df)
            
            # Filter out existing keys
            existing_keys = set(current['__key'])
            unique_new = new_df[~new_df['__key'].isin(existing_keys)].copy()
            
            # Cleanup temp key
            del current['__key']
            del unique_new['__key']
            
            duplicates_count = len(new_df) - len(unique_new)
            
            if not unique_new.empty:
                self.main.data_handler.df = pd.concat([current, unique_new], ignore_index=True)
                msg = f"{len(unique_new)} novos dados importados."
                if duplicates_count > 0:
                    msg += f"\n({duplicates_count} duplicatas ignoradas)."
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showinfo("Info", "Todos os dados selecionados já existem na tabela.")
        else:
            self.main.data_handler.df = new_df
            messagebox.showinfo("Sucesso", f"{len(new_df)} dados importados!")
        
        self.main.data_controller.atualizar_view()

    def acao_carregar_html_treino(self):
        f = filedialog.askopenfilename(filetypes=[("HTML", "*.html")])
        if f:
            self.current_html_path = f
            self.main.view.tab_scraper.sub_calib.lbl_file.config(text=os.path.basename(f))

    def acao_executar_treinamento(self, profile_name, samples_dict):
        if not self.current_html_path:
            messagebox.showwarning("Aviso", "Carregue um arquivo HTML primeiro.")
            return
        
        if not samples_dict:
            messagebox.showwarning("Aviso", "Preencha pelo menos um campo para treinar.")
            return

        ok, msg = self.scraper_trainer.auto_calibrate(self.current_html_path, profile_name, samples_dict)
        
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.main.view.tab_scraper.sub_conf.load_json()
        else:
            messagebox.showerror("Falha", msg)