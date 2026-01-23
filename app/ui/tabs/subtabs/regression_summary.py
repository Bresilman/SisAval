import tkinter as tk
from tkinter import ttk

class RegressionSummarySubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Use PanedWindow to resize areas
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill='both', expand=True)

        # --- TOP AREA: METRICS & DIAGNOSTICS ---
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)

        # 1. Model Quality (Left)
        fr_qual = ttk.LabelFrame(top_frame, text="Qualidade do Ajuste", padding=10)
        fr_qual.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.tree_qual = ttk.Treeview(fr_qual, columns=("Metric", "Value", "Status"), show="headings", height=5)
        self.tree_qual.heading("Metric", text="Métrica")
        self.tree_qual.heading("Value", text="Valor")
        self.tree_qual.heading("Status", text="Avaliação")
        self.tree_qual.column("Metric", width=120)
        self.tree_qual.column("Value", width=80)
        self.tree_qual.column("Status", width=100)
        self.tree_qual.pack(fill='both', expand=True)

        # 2. Variable Coefficients Table (Right) - INCLUDES VIF!
        fr_coef = ttk.LabelFrame(top_frame, text="Equação e Multicolinearidade (VIF)", padding=10)
        fr_coef.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        cols = ("Var", "Coef", "P-Valor", "VIF", "Status")
        self.tree_coef = ttk.Treeview(fr_coef, columns=cols, show="headings", height=5)
        self.tree_coef.heading("Var", text="Variável")
        self.tree_coef.heading("Coef", text="Coeficiente")
        self.tree_coef.heading("P-Valor", text="P-Valor (Sig)")
        self.tree_coef.heading("VIF", text="VIF (FIV)")
        self.tree_coef.heading("Status", text="Diagnóstico")
        
        self.tree_coef.column("Var", width=100)
        self.tree_coef.column("Coef", width=80)
        self.tree_coef.column("P-Valor", width=80)
        self.tree_coef.column("VIF", width=60)
        self.tree_coef.column("Status", width=120)
        
        self.tree_coef.pack(fill='both', expand=True)

        # --- BOTTOM AREA: EDUCATIONAL GUIDE ---
        fr_guide = ttk.LabelFrame(paned, text="📚 Guia de Interpretação (O que isso significa?)", padding=10)
        paned.add(fr_guide, weight=1)

        self.txt_guide = tk.Text(fr_guide, font=("Arial", 10), wrap="word", bg="#f4f4f4")
        sb_guide = ttk.Scrollbar(fr_guide, command=self.txt_guide.yview)
        self.txt_guide.configure(yscrollcommand=sb_guide.set)
        
        self.txt_guide.pack(side='left', fill='both', expand=True)
        sb_guide.pack(side='right', fill='y')

        # Tag configuration for colors
        self.tree_qual.tag_configure("OK", foreground="green")
        self.tree_qual.tag_configure("BAD", foreground="red")
        self.tree_coef.tag_configure("OK", foreground="green")
        self.tree_coef.tag_configure("BAD", foreground="red")

    def update_text(self, text_raw):
        # We ignore text_raw here because we will parse the object directly in parent
        # But we keep method signature for compatibility
        pass

    def update_summary_from_stats(self, stats):
        """
        Receives the full Stats object and populates the dashboard.
        """
        # Clear tables
        self.tree_qual.delete(*self.tree_qual.get_children())
        self.tree_coef.delete(*self.tree_coef.get_children())
        self.txt_guide.delete(1.0, "end")

        # --- 1. FILL QUALITY METRICS ---
        r2 = stats['R2']
        f_p = stats['F_pvalue']
        n = stats['N_Amostras']
        diag = stats.get('Diagnosticos', {})
        
        # Helper to insert rows
        def add_metric(name, val_fmt, is_good, good_msg, bad_msg):
            status = good_msg if is_good else bad_msg
            tag = "OK" if is_good else "BAD"
            self.tree_qual.insert("", "end", values=(name, val_fmt, status), tags=(tag,))

        # R2
        add_metric("Determinação (R²)", f"{r2:.4f}", r2 >= 0.7, "Forte Correlação", "Baixa Explicação")
        # Significance (F)
        add_metric("Significância (F)", f"{f_p:.2e}", f_p < 0.05, "Modelo Válido", "Modelo não Signif.")
        # Normality
        shap_p = diag.get('Shapiro_P', 0)
        add_metric("Normalidade", f"{shap_p:.4f}", shap_p > 0.05, "Resíduos Normais", "Não Normal")
        # Homoscedasticity
        bp_p = diag.get('BreuschPagan_P', 0)
        add_metric("Homocedasticidade", f"{bp_p:.4f}", bp_p > 0.05, "Variância Cte", "Heterocedasticidade")
        # Autocorrelation
        dw = diag.get('Durbin_Watson', 0)
        add_metric("Autocorrelação", f"{dw:.2f}", 1.5 <= dw <= 2.5, "Sem Correlação", "Possível Autocorr.")

        # --- 2. FILL COEFFICIENTS & VIF ---
        params = stats['Params']
        pvalues = stats['P_values']
        vifs = diag.get('VIF', {})

        for var, coef in params.items():
            p_val = pvalues[var]
            vif_val = vifs.get(var, 0)
            
            # Logic for Status
            problems = []
            if p_val > 0.10 and var != 'const': problems.append("P-Valor Alto")
            if vif_val > 10 and var != 'const': problems.append("VIF Alto")
            
            status = "OK" if not problems else ", ".join(problems)
            tag = "OK" if not problems else "BAD"
            
            # Format VIF (const usually doesn't have VIF)
            vif_str = f"{vif_val:.2f}" if var != 'const' else "-"
            
            self.tree_coef.insert("", "end", values=(
                var, f"{coef:.4f}", f"{p_val:.4f}", vif_str, status
            ), tags=(tag,))

        # --- 3. WRITE EDUCATIONAL GUIDE ---
        guide_text = self._generate_guide(r2, f_p, shap_p, bp_p, dw)
        self.txt_guide.insert("end", guide_text)

    def _generate_guide(self, r2, fp, shap, bp, dw):
        txt = "GUIA RÁPIDO DE INTERPRETAÇÃO:\n\n"
        
        txt += "1. R² (Coeficiente de Determinação):\n"
        txt += "   • O que é: Quanto (%) o seu modelo explica do preço.\n"
        txt += f"   • Seu resultado: {r2*100:.1f}%\n"
        txt += "   • Meta: Acima de 0.70 (70%) para Grau II. Se baixo, procure variáveis melhores.\n\n"

        txt += "2. Significância (Teste F):\n"
        txt += "   • O que é: A chance do seu modelo ser pura sorte.\n"
        txt += f"   • Seu resultado: {fp:.4f}\n"
        txt += "   • Meta: Deve ser menor que 0.05 (5%). Se for maior, o modelo é inválido.\n\n"

        txt += "3. VIF (Fator de Inflação de Variância):\n"
        txt += "   • O que é: Mede se uma variável X é 'repetida' ou igual a outra.\n"
        txt += "   • Meta: Deve ser menor que 10. Se for maior, remova a variável.\n\n"

        txt += "4. P-Valor (na tabela de coeficientes):\n"
        txt += "   • O que é: A chance daquela variável específica não servir para nada.\n"
        txt += "   • Meta: Deve ser menor que 0.10 (10%). Se for alto, a variável não ajuda o modelo.\n\n"

        txt += "5. Testes de Resíduos (Normalidade/Homocedasticidade):\n"
        txt += "   • Normalidade (Shapiro): Queremos P > 0.05. Indica erros equilibrados.\n"
        txt += "   • Homocedasticidade (BP): Queremos P > 0.05. Indica que o modelo não erra mais nos imóveis caros.\n"
        
        return txt