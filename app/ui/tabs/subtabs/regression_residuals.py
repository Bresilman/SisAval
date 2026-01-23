import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from app.config import settings

class RegressionResidualsSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.df_temp = None 
        self._setup_ui()

    def _setup_ui(self):
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill='both', expand=True)

        fr_table = ttk.Frame(paned)
        paned.add(fr_table, weight=3)

        cols = ("ID", "Y Real", "Y Previsto", "Erro", "Erro %", "Z-Score")
        self.tree = ttk.Treeview(fr_table, columns=cols, show="headings")
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor="center")
        
        self.tree.pack(fill='both', expand=True, side='left')
        sb = ttk.Scrollbar(fr_table, command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.tag_configure("OUTLIER", background="#f8d7da", foreground="red")

        fr_bottom = ttk.LabelFrame(paned, text="Análise de Resíduos e Outliers", padding=10)
        paned.add(fr_bottom, weight=1)

        btn_export = ttk.Button(fr_bottom, text="💾 Exportar Tabela (.csv)", command=self.exportar_tabela)
        btn_export.pack(side='right', anchor='n')

        limit = settings.STATS_ZSCORE_THRESHOLD
        lbl_guide = tk.Label(fr_bottom, justify="left", anchor="w", text=(
            "GUIA DE INTERPRETAÇÃO:\n"
            "• Erro %: A diferença entre o valor real e o calculado pelo modelo.\n"
            "• Z-Score (Desvio Padronizado): Mede o quão 'anormal' é o preço.\n"
            f"   - Z entre -{limit} e +{limit}: Dado Normal (Verde).\n"
            f"   - Z > {limit} ou < -{limit}: OUTLIER (Vermelho). Pode distorcer o modelo.\n"
            "• Ação Recomendada: Verifique os Outliers na aba de Dados. Se for um erro de\n"
            "  digitação ou um imóvel atípico, exclua-o."
        ), font=("Arial", 9), bg="#f0f0f0", relief="sunken", padx=10, pady=5)
        lbl_guide.pack(side='left', fill='both', expand=True)

    def update_table(self, stats):
        self.tree.delete(*self.tree.get_children())
        
        y_real = stats['Observado']
        y_prev = stats['Valores_Previstos']
        resid = stats['Residuos']
        
        data_list = []
        std_resid = resid.std()
        z_scores = resid / std_resid if std_resid != 0 else resid * 0
        
        limit = settings.STATS_ZSCORE_THRESHOLD
        
        for idx in y_real.index:
            real = y_real[idx]
            prev = y_prev[idx]
            err = resid[idx]
            perc = (err / real) * 100 if real != 0 else 0
            z = z_scores[idx]
            
            vals = (idx, f"{real:.2f}", f"{prev:.2f}", f"{err:.2f}", f"{perc:.1f}%", f"{z:.2f}")
            
            data_list.append({
                "ID": idx, "Real": real, "Previsto": prev, 
                "Erro": err, "Erro_Perc": perc, "Z_Score": z
            })

            tags = ("OUTLIER",) if abs(z) > limit else ()
            self.tree.insert("", "end", values=vals, tags=tags)
            
        self.df_temp = pd.DataFrame(data_list)

    def exportar_tabela(self):
        if self.df_temp is None or self.df_temp.empty: return
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if f:
            try:
                self.df_temp.to_csv(f, index=False, sep=";", decimal=",")
                messagebox.showinfo("Sucesso", "Tabela exportada!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))