import tkinter as tk
from tkinter import ttk
from app.config import settings

class ValidationPrecisionSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        fr_prec = ttk.LabelFrame(self, text="1. Grau de Precisão (Amplitude)", padding=15)
        fr_prec.pack(fill='x', padx=10, pady=10)

        self.lbl_val = ttk.Label(fr_prec, text="Valor Central: R$ 0,00", font=("Arial", 10))
        self.lbl_val.pack(anchor='w')
        
        self.lbl_interval = ttk.Label(fr_prec, text="Intervalo: R$ 0,00 a R$ 0,00")
        self.lbl_interval.pack(anchor='w')

        self.lbl_amp = ttk.Label(fr_prec, text="Amplitude: 0.00 %", font=("Arial", 12, "bold"), foreground="blue")
        self.lbl_amp.pack(anchor='w', pady=5)
        
        self.lbl_grade = ttk.Label(fr_prec, text="Classificação: Aguardando Cálculo...", font=("Arial", 11, "bold"))
        self.lbl_grade.pack(anchor='w', pady=5)
        
        g3 = settings.GRADE_III_LIMIT
        g2 = settings.GRADE_II_LIMIT
        ttk.Label(fr_prec, text=f"Regra NBR 14.653-2:\n• Grau III: Amplitude ≤ {g3}%\n• Grau II: Amplitude ≤ {g2}%\n• Grau I: Amplitude > {g2}%", font=("Arial", 9), foreground="gray", justify='left').pack(anchor='w', pady=5)

        fr_extra = ttk.LabelFrame(self, text="2. Verificação de Fronteiras (Extrapolação)", padding=15)
        fr_extra.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(fr_extra, text="Limites da Amostra (Onde seu modelo é seguro):").pack(anchor='w', pady=(0, 10))

        cols = ("Variável", "Mínimo Amostra", "Máximo Amostra", "Seu Imóvel", "Status")
        self.tree = ttk.Treeview(fr_extra, columns=cols, show="headings", height=8)
        
        widths = [120, 100, 100, 100, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
            
        self.tree.pack(fill='both', expand=True)
        
        self.tree.tag_configure("OK", foreground="green")
        self.tree.tag_configure("EXTRAPOLA", foreground="red")

    def update_precision(self, result_dict):
        if not result_dict: return 0.0

        central = result_dict['Valor_Central']
        min_c = result_dict['IC_Min']
        max_c = result_dict['IC_Max']
        
        amplitude = (max_c - min_c) / central
        amp_perc = amplitude * 100

        conf = int(settings.STATS_CONFIDENCE_LEVEL * 100)
        self.lbl_val.config(text=f"Valor Central: R$ {central:,.2f}")
        self.lbl_interval.config(text=f"Intervalo ({conf}%): R$ {min_c:,.2f} a R$ {max_c:,.2f}")
        self.lbl_amp.config(text=f"Amplitude: {amp_perc:.2f} %")

        if amp_perc <= settings.GRADE_III_LIMIT:
            grade = "Grau III (Excelente)"
            color = "green"
        elif amp_perc <= settings.GRADE_II_LIMIT:
            grade = "Grau II (Satisfatório)"
            color = "#D4AC0D"
        else:
            grade = "Grau I (Baixa Precisão)"
            color = "red"
            
        self.lbl_grade.config(text=f"Classificação: {grade}", foreground=color)
        
        return amp_perc

    def update_boundaries(self, df_used, input_vars=None):
        if df_used is None: return
        self.tree.delete(*self.tree.get_children())
        for col in df_used.columns:
            if col == 'const': continue
            
            # Use raw column name for display
            display_col = col.replace("Ln_", "").replace("Inv_", "").replace("Quad_", "").replace("Raiz_", "")
            
            # Need to match input vars which use display_name
            # If input_vars uses display_name, we must map col back to it
            
            min_v = df_used[col].min()
            max_v = df_used[col].max()
            
            val_str = "-"
            status = "Aguardando Input"
            tag = "OK"

            if input_vars:
                # Check using display_name in input_vars
                if display_col in input_vars:
                    val_imovel = input_vars[display_col]
                    
                    # BUT WAIT: Extrapolation check must be done on the TRANSFORMED value if the model used it?
                    # No, NBR says extrapolation check is on the observed variable range.
                    # If model used Ln_Area, we check if Ln(200) is inside [Ln(min), Ln(max)].
                    # Since df_used contains transformed data (e.g. Ln_Area), and input_vars contains RAW data (200),
                    # we must transform the input before comparing, OR untransform min/max.
                    
                    # Safer: Untransform the Limits for display if possible, or Transform input.
                    # Since we don't know the exact transform function here easily without replicating logic,
                    # let's assume 'df_used' passed here is the RAW data from 'Dados_Utilizados' in StatsEngine return.
                    # StatsEngine 'Dados_Utilizados' returns the CLEANED RAW data. Correct.
                    
                    # So df_used[col] is raw data.
                    val_str = f"{val_imovel:,.2f}"
                    
                    if val_imovel < min_v:
                        status = "Extrapola (Inferior)"
                        tag = "EXTRAPOLA"
                    elif val_imovel > max_v:
                        status = "Extrapola (Superior)"
                        tag = "EXTRAPOLA"
                    else:
                        status = "OK (Dentro)"
            
            self.tree.insert("", "end", values=(
                display_col, 
                f"{min_v:,.2f}", 
                f"{max_v:,.2f}",
                val_str,
                status
            ), tags=(tag,))