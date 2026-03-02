import customtkinter as ctk

class ValResiduals(ctk.CTkFrame):
    """
    Sub-aba: Diagnóstico de Resíduos.
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.txt_resid = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Courier New", size=12))
        self.txt_resid.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_resid.insert("0.0", "Aguardando dados...")

    def update_data(self, audit):
        self.txt_resid.delete("0.0", "end")
        resid = audit['residuals']
        
        report = f"--- DIAGNÓSTICO TÉCNICO ---\n\n"
        report += f"1. Normalidade ({resid['normality']['test']}):\n"
        report += f"   Status: {resid['normality']['status']} (P={resid['normality']['p_value']:.4f})\n\n"
        
        report += f"2. Homocedasticidade (Breusch-Pagan):\n"
        report += f"   Status: {resid['homoscedasticity']['status']} (P={resid['homoscedasticity']['p_value']:.4f})\n\n"
        
        report += f"3. Autocorrelação (Durbin-Watson):\n"
        report += f"   Valor: {resid['autocorrelation']['val']:.2f} ({resid['autocorrelation']['status']})\n\n"
        
        report += f"4. Outliers:\n"
        report += f"   Identificados: {resid['outliers']['count']}\n"
        if resid['outliers']['count'] > 0:
            report += f"   Índices: {resid['outliers']['indices']}"
            
        self.txt_resid.insert("0.0", report)