from tkinter import filedialog, messagebox
import os
import matplotlib.pyplot as plt
from app.models.project_state import ProjectState
from app.engines.pdf_engine import PDFEngine

class ToolsController:
    def __init__(self, main_controller):
        self.main = main_controller
        self.data_handler = self.main.data_handler
        self.evolutionary_engine = self.main.evolutionary_engine
        self.report_engine = self.main.report_engine
        self.pdf_engine = PDFEngine()
        self.view = self.main.view

    def salvar_projeto(self):
        f = filedialog.asksaveasfilename(defaultextension=".sav", filetypes=[("Projeto SisAval", "*.sav")])
        if f:
            try:
                # Pass main controller to capture FULL state
                ProjectState.save_project(f, self.main)
                messagebox.showinfo("Sucesso", "Projeto completo salvo!")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", str(e))
    
    def abrir_projeto(self):
        f = filedialog.askopenfilename(filetypes=[("Projeto SisAval", "*.sav")])
        if f:
            try:
                # Pass main controller to restore FULL state
                ProjectState.load_project(f, self.main)
                messagebox.showinfo("Sucesso", "Projeto carregado e restaurado!")
            except Exception as e:
                messagebox.showerror("Erro ao Abrir", str(e))

    def gerar_relatorio(self):
        # Legacy method for TXT generation
        if self.main.last_stats:
            f = filedialog.asksaveasfilename(defaultextension=".txt")
            if f:
                with open(f, "w") as file: file.write(self.report_engine.gerar_texto(self.main.last_stats))

    def acao_add_principal(self, data):
        try:
            res = self.evolutionary_engine.calcular_benfeitoria_principal(
                data['area'], data['cub'], data['bdi'], data['idade'], data['vida'], data['estado'], data['metodo']
            )
            vals = (data['nome'], f"{data['area']}", f"{data['cub']}", f"{data['bdi']}%", f"R$ {res['Custo_Novo']:,.2f}", f"{res['Fator_K']:.4f}", f"R$ {res['Valor_Atual']:,.2f}")
            self.view.tab_evolutionary.sub_const.tree.insert("", "end", values=vals)
        except Exception as e: messagebox.showerror("Erro", str(e))

    def acao_add_complementar(self, data):
        try:
            res = self.evolutionary_engine.calcular_complementar(
                data['qtde'], data['unit'], data['bdi'], data['idade'], data['vida'], data['estado'], "Ross-Heidecke"
            )
            vals = (data['desc'], f"{data['qtde']}", f"R$ {data['unit']}", f"{data['bdi']}%", f"R$ {res['Custo_Novo']:,.2f}", f"{res['Fator_K']:.4f}", f"R$ {res['Valor_Atual']:,.2f}")
            self.view.tab_evolutionary.sub_comp.tree.insert("", "end", values=vals)
        except Exception as e: messagebox.showerror("Erro", str(e))

    def calcular_evolutivo(self):
        try:
            sum_tab = self.view.tab_evolutionary.sub_sum
            v_terreno = float(sum_tab.ent_terr.get().replace(',', '.'))
            fc = float(sum_tab.ent_fc.get().replace(',', '.'))
            
            total_principal = 0.0
            for item in self.view.tab_evolutionary.sub_const.tree.get_children():
                val_str = self.view.tab_evolutionary.sub_const.tree.item(item)['values'][6]
                total_principal += float(val_str.replace('R$', '').replace('.', '').replace(',', '.').strip())

            total_comp = 0.0
            for item in self.view.tab_evolutionary.sub_comp.tree.get_children():
                val_str = self.view.tab_evolutionary.sub_comp.tree.item(item)['values'][6]
                total_comp += float(val_str.replace('R$', '').replace('.', '').replace(',', '.').strip())

            res = self.evolutionary_engine.calcular_total_evolutivo(v_terreno, total_principal, total_comp, fc)

            sum_tab.lbls['vt'].config(text=f"R$ {res['Valor_Terreno']:,.2f}")
            sum_tab.lbls['bp'].config(text=f"R$ {res['Soma_Principal']:,.2f}")
            sum_tab.lbls['oc'].config(text=f"R$ {res['Soma_Complementar']:,.2f}")
            sum_tab.lbls['soma'].config(text=f"R$ {res['Total_Benfeitorias'] + res['Valor_Terreno']:,.2f}")
            sum_tab.lbls['final'].config(text=f"R$ {res['Valor_Final']:,.2f}")
        except ValueError: messagebox.showerror("Erro", "Verifique valores numéricos.")

    def acao_gerar_pdf(self):
        if not self.main.last_stats:
            messagebox.showwarning("Aviso", "É necessário calcular a regressão primeiro.")
            return

        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not f: return

        try:
            context = {}
            context['settings'] = self.view.tab_settings.get_settings()
            
            if hasattr(self.view, 'tab_report'):
                context['texts'] = self.view.tab_report.sub_config.get_data()
                context['options'] = {
                    'include_data': self.view.tab_report.chk_data.get(),
                    'include_plots': self.view.tab_report.chk_plots.get()
                }
            else:
                context['texts'] = {}
                context['options'] = {'include_data': True, 'include_plots': True}
            
            context['stats'] = self.main.last_stats
            context['df'] = self.data_handler.get_data()
            
            try:
                lbl_text = self.view.tab_calculator.lbl_unit.cget("text")
                val = float(lbl_text.replace("R$", "").replace(".", "").replace(",", ".").strip())
                if val > 0:
                    context['calculator_result'] = {
                        'Valor_Central': val,
                        'IC_Min': val * 0.85, 
                        'IC_Max': val * 1.15
                    }
            except: pass

            evol_data = {'principal': [], 'complementary': [], 'summary': {}}
            tree_p = self.view.tab_evolutionary.sub_const.tree
            for item in tree_p.get_children(): evol_data['principal'].append(tree_p.item(item)['values'])
            tree_c = self.view.tab_evolutionary.sub_comp.tree
            for item in tree_c.get_children(): evol_data['complementary'].append(tree_c.item(item)['values'])
            
            sum_tab = self.view.tab_evolutionary.sub_sum
            evol_data['summary'] = {
                'land': sum_tab.lbls['vt'].cget("text"),
                'main': sum_tab.lbls['bp'].cget("text"),
                'comp': sum_tab.lbls['oc'].cget("text"),
                'total': sum_tab.lbls['final'].cget("text")
            }
            context['evolutionary'] = evol_data

            img_path = "temp_plot.png"
            if context['options']['include_plots']:
                fig = self.view.tab_regression.subtab_plots.plot_manager.figure
                fig.savefig(img_path, dpi=150)
                context['plot_image_path'] = img_path

            self.pdf_engine.gerar_pdf(f, context)
            
            if os.path.exists(img_path): os.remove(img_path)
            messagebox.showinfo("Sucesso", "Laudo PDF gerado com sucesso!")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro ao gerar PDF", f"Detalhe: {str(e)}")