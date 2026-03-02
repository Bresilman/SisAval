import customtkinter as ctk

class ValPrecision(ctk.CTkFrame):
    """
    Sub-aba: Estimativa de Precisão (Centróide).
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.frame_prec = ctk.CTkFrame(self)
        self.frame_prec.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.lbl_score = ctk.CTkLabel(self.frame_prec, text="---", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_score.pack(pady=10)
        
        self.lbl_val = ctk.CTkLabel(self.frame_prec, text="Amplitude: ---")
        self.lbl_val.pack(pady=5)
        
        ctk.CTkLabel(self.frame_prec, text="Nota: Calculado no centróide da amostra.", text_color="gray").pack(pady=20)

    def update_data(self, audit):
        prec = audit['precision_proxy']
        color = "green" if "III" in prec['grade'] else "orange" if "II" in prec['grade'] else "red"
        
        self.lbl_score.configure(text=prec['grade'], text_color=color)
        self.lbl_val.configure(text=f"Amplitude do Intervalo: {prec['amplitude_perc']:.2f}%")