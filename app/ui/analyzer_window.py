import customtkinter as ctk
import sys
from app.ui.tabs.tab_data import TabData
from app.ui.tabs.tab_factors import TabFactors
from app.ui.tabs.tab_regression import TabRegression
from app.ui.tabs.tab_validation import TabValidation
from app.ui.tabs.tab_report import TabReport
from app.ui.tabs.tab_optimizer import TabOptimizer
from app.ui.tabs.tab_calculator import TabCalculator # <--- Import Adicionado

try:
    from app.config.settings import APP_NAME, APP_VERSION
except ImportError:
    APP_NAME = "SisAval"
    APP_VERSION = "2.0.0"

class AnalyzerWindow(ctk.CTk):
    """
    Janela Principal do Módulo Analista.
    Gerencia a navegação por abas e a estrutura lateral.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title(f"{APP_NAME} - {APP_VERSION}")
        self.geometry("1280x800")
        self.minsize(1024, 768)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuração de Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        
        # Container das Abas
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.setup_tabs()
        
    def setup_sidebar(self):
        """Painel lateral com botões de ação rápida."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        lbl_logo = ctk.CTkLabel(self.sidebar, text="SisAval\nAnalista", 
                               font=ctk.CTkFont(size=20, weight="bold"))
        lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        btn_load = ctk.CTkButton(self.sidebar, text="1. Carregar Dados", 
                                command=self.controller.acao_carregar_dados)
        btn_load.grid(row=1, column=0, padx=20, pady=10)

        btn_calc = ctk.CTkButton(self.sidebar, text="2. Calcular Modelo", 
                                fg_color="green", hover_color="darkgreen",
                                command=self.controller.acao_calcular_regressao)
        btn_calc.grid(row=2, column=0, padx=20, pady=10)
        
    def setup_tabs(self):
        """Inicializa e registra as abas do sistema."""
        tabs_config = [
            ("Dados", TabData),
            ("Fatores", TabFactors),
            ("Otimizador", TabOptimizer),
            ("Regressão", TabRegression),
            ("Validação", TabValidation),
            ("Calculadora", TabCalculator), # <--- Aba Registrada
            ("Laudo", TabReport)
        ]
        
        self.tabs = {}
        for tab_name, TabClass in tabs_config:
            self.tab_view.add(tab_name)
            parent_frame = self.tab_view.tab(tab_name)
            try:
                # Instancia a aba passando o container e o controller
                tab_instance = TabClass(parent_frame, self.controller)
                tab_instance.pack(fill="both", expand=True)
                self.tabs[tab_name] = tab_instance
            except Exception as e:
                print(f"Erro ao carregar aba {tab_name}: {e}")
                ctk.CTkLabel(parent_frame, text=f"Erro no carregamento: {e}", text_color="red").pack()
            
    def show_error(self, message):
        """Exibe modal de erro simples."""
        error_win = ctk.CTkToplevel(self)
        error_win.title("Erro")
        error_win.geometry("400x200")
        error_win.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(error_win, text=message, text_color="red", wraplength=350)
        lbl.pack(expand=True, padx=20, pady=20)
        
        btn = ctk.CTkButton(error_win, text="OK", command=error_win.destroy)
        btn.pack(pady=(0, 20))

    def on_closing(self):
        """Limpeza de memória ao fechar."""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except: pass
        self.quit()
        self.destroy()
        sys.exit(0)