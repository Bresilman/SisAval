import customtkinter as ctk

class TabFactors(ctk.CTkFrame):
    """
    Aba para Homogeneização e Tratamento de Fatores.
    (Versão Inicial Simplificada para o Módulo Analista)
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        lbl_title = ctk.CTkLabel(self, text="Tratamento de Fatores (Homogeneização)", 
                               font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Painel Informativo (Placeholder)
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        lbl_info = ctk.CTkLabel(info_frame, text="Nesta etapa, você poderá aplicar fatores de depreciação,\noferta ou transposição para homogeneizar a amostra.\n\n(Funcionalidade em migração para o novo motor)",
                              justify="center")
        lbl_info.pack(pady=20)
        
        # Exemplo de Controles Futuros
        btn_apply = ctk.CTkButton(self, text="Aplicar Fatores Padrão", state="disabled")
        btn_apply.grid(row=2, column=0, padx=20, pady=20)