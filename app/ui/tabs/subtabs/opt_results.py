import customtkinter as ctk

class OptResults(ctk.CTkFrame):
    """
    Sub-aba de Resultados do Solver.
    Exibe a tabela de modelos encontrados.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.lbl_status = ctk.CTkLabel(self, text="Status: Aguardando...", text_color="gray")
        self.lbl_status.pack(pady=5)
        
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        self._create_header()

    def _create_header(self):
        h = ctk.CTkFrame(self.scroll, fg_color="gray", height=30)
        h.pack(fill="x")
        ctk.CTkLabel(h, text="#", width=30).pack(side="left", padx=5)
        ctk.CTkLabel(h, text="R² Adj", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(h, text="AIC", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Fórmula / Variáveis", width=300).pack(side="left", padx=5)

    def update_status(self, msg):
        self.lbl_status.configure(text=msg)

    def display_results(self, results):
        # Limpa resultados anteriores (mantendo header se possível ou recriando)
        for w in self.scroll.winfo_children():
            w.destroy()
            
        self._create_header()
            
        for m in results:
            row = ctk.CTkFrame(self.scroll)
            row.pack(fill="x", pady=2)
            
            rank = m.get('rank', '?')
            r2 = m.get('r2_adj', 0)
            aic = m.get('aic', 9999)
            formula = m.get('formula', '...')
            
            ctk.CTkLabel(row, text=str(rank), width=30).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{r2:.3f}", width=60, text_color="green").pack(side="left", padx=5)
            
            aic_text = f"{aic:.1f}" if aic is not None else "N/A"
            ctk.CTkLabel(row, text=aic_text, width=60).pack(side="left", padx=5)
            
            ctk.CTkLabel(row, text=formula, width=300, anchor="w").pack(side="left", padx=5)
            
            ctk.CTkButton(row, text="Carregar", width=70, height=24,
                        command=lambda mod=m: self.controller.acao_carregar_modelo_otimizado(mod)).pack(side="right", padx=5)