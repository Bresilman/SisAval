import customtkinter as ctk
from app.ui.tabs.subtabs.val_dashboard import ValDashboard
from app.ui.tabs.subtabs.val_analysis import ValAnalysis
from app.ui.tabs.subtabs.val_residuals import ValResiduals
from app.ui.tabs.subtabs.val_precision import ValPrecision

class TabValidation(ctk.CTkFrame):
    """
    Aba Container de Validação.
    Responsabilidade: Gerenciar as sub-abas e distribuir os dados vindos do Controller.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Layout Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Gerenciador de Abas (TabView)
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        # Criando as Abas
        self.tab_view.add("🏆 Fundamentação")
        self.tab_view.add("🔍 Análise Detalhada")
        self.tab_view.add("⚠️ Resíduos")
        self.tab_view.add("🎯 Precisão")
        
        # Instanciando as Sub-Abas (Módulos Independentes)
        # Passamos o 'frame' interno da aba como pai
        self.sub_dashboard = ValDashboard(self.tab_view.tab("🏆 Fundamentação"))
        self.sub_dashboard.pack(fill="both", expand=True)

        self.sub_analysis = ValAnalysis(self.tab_view.tab("🔍 Análise Detalhada"))
        self.sub_analysis.pack(fill="both", expand=True)

        self.sub_residuals = ValResiduals(self.tab_view.tab("⚠️ Resíduos"))
        self.sub_residuals.pack(fill="both", expand=True)

        self.sub_precision = ValPrecision(self.tab_view.tab("🎯 Precisão"))
        self.sub_precision.pack(fill="both", expand=True)

    def update_audit(self, audit_data):
        """
        Recebe o dicionário completo do NBRAuditor e distribui para os especialistas.
        """
        self.sub_dashboard.update_data(audit_data)
        self.sub_analysis.update_data(audit_data)
        self.sub_residuals.update_data(audit_data)
        self.sub_precision.update_data(audit_data)