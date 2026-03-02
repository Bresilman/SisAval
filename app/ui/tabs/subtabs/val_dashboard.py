import customtkinter as ctk

class ValDashboard(ctk.CTkFrame):
    """
    Sub-aba: Placar Geral e Grau de Fundamentação.
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.frame_score = ctk.CTkFrame(self)
        self.frame_score.pack(fill="x", padx=10, pady=10)
        
        self.lbl_score = ctk.CTkLabel(self.frame_score, text="---", font=ctk.CTkFont(size=32, weight="bold"))
        self.lbl_score.pack(pady=10)
        
        self.lbl_msg = ctk.CTkLabel(self.frame_score, text="Aguardando cálculo...", text_color="gray")
        self.lbl_msg.pack(pady=(0, 10))
        
        self.frame_checklist = ctk.CTkScrollableFrame(self, label_text="Resumo dos Pontos")
        self.frame_checklist.pack(fill="both", expand=True, padx=10, pady=5)

    def update_data(self, audit):
        # 1. Placar
        grade = audit['fundamentacao']
        color = "green" if "III" in grade else "orange" if "II" in grade else "yellow" if "I" in grade else "red"
        
        self.lbl_score.configure(text=grade, text_color=color)
        self.lbl_msg.configure(text="Classificação Global NBR 14.653-2")
        
        # 2. Checklist
        for w in self.frame_checklist.winfo_children(): w.destroy()
        
        micro = audit['micronumerosity']
        self._add_item("Tamanho da Amostra", micro['grade'], micro['desc'])
        
        # Adicione outros resumos se desejar
        # Ex: self._add_item("Pressupostos", ..., ...)

    def _add_item(self, title, grade, desc):
        row = ctk.CTkFrame(self.frame_checklist)
        row.pack(fill="x", pady=2)
        color = "green" if "III" in grade else "orange" if "II" in grade else "red"
        icon = "✅" if color != "red" else "❌"
        ctk.CTkLabel(row, text=icon, width=30).pack(side="left")
        ctk.CTkLabel(row, text=title, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=f"[{grade}]", text_color=color).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=desc, text_color="gray").pack(side="left", padx=5)