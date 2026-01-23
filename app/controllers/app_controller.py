import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

# Models
from app.models.data_handler import DataHandler
from app.models.project_state import ProjectState

# Engines
from app.engines.stats_engine import StatsEngine
from app.engines.validator_engine import NBRValidator
from app.engines.evolutionary_engine import EvolutionaryEngine
from app.engines.report_engine import ReportEngine
from app.engines.optimizer_engine import OptimizerEngine
from app.engines.spatial_engine import SpatialEngine
from app.engines.geocoding_engine import GeocodingEngine

# UI
from app.ui.main_window import MainWindow

# Sub-Controllers
from app.controllers.data_controller import DataController
from app.controllers.stats_controller import StatsController
from app.controllers.tools_controller import ToolsController
from app.controllers.scraper_controller import ScraperController
from app.controllers.factors_controller import FactorsController # Novo

class AppController:
    def __init__(self):
        # 1. INICIALIZAÇÃO DE DADOS E MOTORES (Independentes da UI)
        self.data_handler = DataHandler()
        
        self.stats_engine = StatsEngine()
        self.validator = NBRValidator()
        self.evolutionary_engine = EvolutionaryEngine()
        self.report_engine = ReportEngine()
        self.optimizer_engine = OptimizerEngine()
        self.spatial_engine = SpatialEngine()
        self.geocoding_engine = GeocodingEngine()
        
        self.last_stats = None
        self.melhores_modelos_cache = []
        self.current_map_target = None

        # 2. INICIALIZAÇÃO DA INTERFACE (CRÍTICO: Deve vir antes dos controladores)
        # A View precisa receber 'self' para configurar os botões, mas ainda não pode chamar métodos complexos
        self.view = MainWindow(self)

        # 3. INICIALIZAÇÃO DOS SUB-CONTROLADORES (Dependentes da UI e AppController)
        # Agora 'self.view' já existe, então eles podem acessá-la sem erro.
        self.data_ctrl = DataController(self)
        self.stats_ctrl = StatsController(self)
        self.tools_ctrl = ToolsController(self)
        self.scraper_ctrl = ScraperController(self)
        self.factors_ctrl = FactorsController(self)

    def run(self):
        self.view.mainloop()

    # --- MÉTODOS DE PONTE (PROXIES) ---
    # A View chama estes métodos, que redirecionam para o sub-controlador correto

    # Data Controller
    def acao_carregar(self): self.data_ctrl.carregar()
    def acao_exemplo(self): self.data_ctrl.exemplo()
    def acao_excluir_dado(self): self.data_ctrl.excluir_dado()
    def acao_transformar(self, col, tipo): self.data_ctrl.transformar(col, tipo)
    def acao_codificar_variavel(self, col, mapping): self.data_ctrl.codificar_variavel(col, mapping)
    def acao_sanear_dados(self): self.data_ctrl.sanear_dados()
    def acao_importar_web(self): self.data_ctrl.acao_importar_web()
    def acao_calibrar_scraper(self): self.data_ctrl.acao_calibrar_scraper()

    # Stats Controller
    def acao_calcular(self): self.stats_ctrl.calcular()
    def acao_estimar(self): self.stats_ctrl.estimar()
    def acao_otimizar_modelos_avancado(self, config): self.stats_ctrl.otimizar_avancado(config)
    def acao_carregar_modelo_otimizado(self, idx): self.stats_ctrl.carregar_modelo_otimizado(idx)
    def acao_analisar_transformacoes(self): self.stats_ctrl.analisar_transformacoes()

    # Scraper Controller
    def acao_importar_pasta(self): self.scraper_ctrl.acao_importar_pasta()
    def acao_enviar_para_analise(self): self.scraper_ctrl.acao_enviar_para_analise()
    def acao_carregar_html_treino(self): self.scraper_ctrl.acao_carregar_html_treino()
    def acao_executar_treinamento(self, p, a): self.scraper_ctrl.acao_executar_treinamento(p, a)

    # Tools Controller (Evolutivo, PDF, Arquivo)
    def acao_salvar_projeto(self): self.tools_ctrl.salvar_projeto()
    def acao_abrir_projeto(self): self.tools_ctrl.abrir_projeto()
    def acao_gerar_relatorio(self): self.tools_ctrl.gerar_relatorio() # TXT Legacy
    def acao_gerar_pdf(self): self.tools_ctrl.acao_gerar_pdf() # PDF Novo
    
    # Evolutivo
    def acao_add_principal(self, d): self.tools_ctrl.acao_add_principal(d)
    def acao_add_complementar(self, d): self.tools_ctrl.acao_add_complementar(d)
    def acao_calcular_total_evolutivo(self): self.tools_ctrl.calcular_evolutivo()
    
    # Alias de compatibilidade (caso a UI ainda chame os nomes antigos)
    def acao_adicionar_benfeitoria(self, d): self.tools_ctrl.acao_add_principal(d)
    def acao_calcular_evolutivo(self): self.tools_ctrl.calcular_evolutivo()

    # Factors Controller (Aba 8)
    def acao_calcular_fatores(self): self.factors_ctrl.calcular_fatores()

    # Spatial Controller (Lógica dentro de AppController por enquanto ou mover para SpatialController)
    # Como implementamos a lógica de Threads direto no AppController anteriormente, mantemos aqui ou movemos.
    # Para consistência, o ideal seria um SpatialController, mas vamos manter o que funcionava:
    
    def acao_geocodificar(self, addr_col, city_col):
        # Lógica de thread movida para cá ou mantida se já estava funcionando
        # Se você já tinha implementado isso no passo anterior, mantenha.
        # Vou incluir a implementação básica aqui para garantir que não falte.
        import threading
        df = self.data_handler.get_data()
        if df is None: return

        def worker():
            if hasattr(self.view, 'tab_map'):
                self.view.tab_map.sub_geo.lbl_status.config(text="Processando...", foreground="blue")
            
            results = self.geocoding_engine.batch_geocode(df, addr_col, city_col)
            
            if 'Latitude' not in df.columns: df['Latitude'] = 0.0
            if 'Longitude' not in df.columns: df['Longitude'] = 0.0
            
            count = 0
            for res in results:
                if res['status'] == 'OK':
                    df.at[res['index'], 'Latitude'] = res['lat']
                    df.at[res['index'], 'Longitude'] = res['lon']
                    count += 1
            
            self.view.after(0, lambda: self._pos_geocoding(count))

        t = threading.Thread(target=worker)
        t.start()

    def _pos_geocoding(self, count):
        if hasattr(self.view, 'tab_map'):
            self.view.tab_map.sub_geo.lbl_status.config(text=f"Concluído! {count} achados.", foreground="green")
        self._atualizar_view_dados()
        messagebox.showinfo("Sucesso", f"Geocodificação: {count} endereços localizados.")

    def acao_criar_variavel_distancia(self, col_name, lat_target, lon_target):
        try:
            df = self.data_handler.get_data()
            dists = self.spatial_engine.calculate_distances(df, 'Latitude', 'Longitude', lat_target, lon_target)
            df[col_name] = dists
            self._atualizar_view_dados()
            messagebox.showinfo("Sucesso", f"Variável '{col_name}' criada!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))