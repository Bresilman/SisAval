import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import threading

# --- MODELS ---
from app.models.data_handler import DataHandler
from app.models.project_state import ProjectState

# --- ENGINES ---
from app.engines.stats_engine import StatsEngine
from app.engines.validator_engine import NBRValidator
from app.engines.evolutionary_engine import EvolutionaryEngine
from app.engines.report_engine import ReportEngine
from app.engines.optimizer_engine import OptimizerEngine
from app.engines.spatial_engine import SpatialEngine
from app.engines.geocoding_engine import GeocodingEngine
from app.engines.scraper_engine import ScraperEngine
from app.engines.scraper_trainer import ScraperTrainer
# Engines Novas
from app.engines.urban_engine import UrbanEngine
from app.engines.google_engine import GoogleGeoEngine
from app.engines.market_intelligence import MarketIntelligenceEngine

# --- UI ---
from app.ui.main_window import MainWindow

# --- SUB-CONTROLLERS ---
from app.controllers.data_controller import DataController
from app.controllers.stats_controller import StatsController
from app.controllers.tools_controller import ToolsController
from app.controllers.scraper_controller import ScraperController
from app.controllers.factors_controller import FactorsController

class AppController:
    def __init__(self):
        # 1. INICIALIZAÇÃO DE DADOS E MOTORES (Lógica Pura)
        self.data_handler = DataHandler()
        
        self.stats_engine = StatsEngine()
        self.validator = NBRValidator()
        self.evolutionary_engine = EvolutionaryEngine()
        self.report_engine = ReportEngine()
        self.optimizer_engine = OptimizerEngine()
        self.spatial_engine = SpatialEngine()
        self.geocoding_engine = GeocodingEngine()
        
        # Novas Engines
        self.urban_engine = UrbanEngine()
        self.google_engine = GoogleGeoEngine()
        self.market_intelligence = MarketIntelligenceEngine()

        # Variáveis de Estado
        self.last_stats = None
        self.melhores_modelos_cache = []
        self.current_map_target = None

        # 2. INICIALIZAÇÃO DA INTERFACE (A View precisa do Controller, mas não chama nada no init)
        self.view = MainWindow(self)

        # 3. INICIALIZAÇÃO DOS SUB-CONTROLADORES (Eles precisam da View já criada)
        self.data_ctrl = DataController(self)
        self.stats_ctrl = StatsController(self)
        self.tools_ctrl = ToolsController(self)
        self.scraper_ctrl = ScraperController(self)
        self.factors_ctrl = FactorsController(self)

    def run(self):
        self.view.mainloop()

    # =========================================================================
    # PROXY METHODS (Redirecionam a UI para o Sub-Controlador correto)
    # =========================================================================

    # --- DATA CONTROLLER ---
    def acao_carregar(self): self.data_ctrl.carregar()
    def acao_exemplo(self): self.data_ctrl.exemplo()
    def acao_excluir_dado(self): self.data_ctrl.excluir_dado()
    def acao_transformar(self, col, tipo): self.data_ctrl.transformar(col, tipo)
    def acao_codificar_variavel(self, col, mapping): self.data_ctrl.codificar_variavel(col, mapping)
    def acao_sanear_dados(self): self.data_ctrl.sanear_dados()
    def acao_importar_web(self): self.data_ctrl.acao_importar_web()
    def acao_calibrar_scraper(self): self.data_ctrl.acao_calibrar_scraper()
    def acao_enriquecer_bairros(self): self.data_ctrl.acao_enriquecer_bairros() # Nova funcionalidade

    # --- STATS CONTROLLER ---
    def acao_calcular(self): self.stats_ctrl.calcular()
    def acao_estimar(self): self.stats_ctrl.estimar()
    def acao_otimizar_modelos_avancado(self, config): self.stats_ctrl.otimizar_avancado(config)
    def acao_carregar_modelo_otimizado(self, idx): self.stats_ctrl.carregar_modelo_otimizado(idx)
    def acao_analisar_transformacoes(self): self.stats_ctrl.analisar_transformacoes()

    # --- TOOLS CONTROLLER (Arquivos, Relatórios, Evolutivo) ---
    def acao_salvar_projeto(self): self.tools_ctrl.salvar_projeto()
    def acao_abrir_projeto(self): self.tools_ctrl.abrir_projeto()
    def acao_gerar_relatorio(self): self.tools_ctrl.gerar_relatorio() # TXT
    def acao_gerar_pdf(self): self.tools_ctrl.acao_gerar_pdf()       # PDF
    
    # Evolutivo Principal
    def acao_add_principal(self, d): self.tools_ctrl.acao_add_principal(d)
    # Alias para compatibilidade
    def acao_adicionar_benfeitoria(self, d): self.tools_ctrl.acao_add_principal(d)
    
    # Evolutivo Complementar
    def acao_add_complementar(self, d): self.tools_ctrl.acao_add_complementar(d)
    
    # Evolutivo Total
    def acao_calcular_total_evolutivo(self): self.tools_ctrl.calcular_evolutivo()
    # Alias
    def acao_calcular_evolutivo(self): self.tools_ctrl.calcular_evolutivo()

    # --- SCRAPER CONTROLLER (Crawler) ---
    def acao_importar_pasta(self): self.scraper_ctrl.acao_importar_pasta()
    def acao_enviar_para_analise(self): self.scraper_ctrl.acao_enviar_para_analise()
    def acao_carregar_html_treino(self): self.scraper_ctrl.acao_carregar_html_treino()
    def acao_executar_treinamento(self, p, a): self.scraper_ctrl.acao_executar_treinamento(p, a)
    def acao_iniciar_crawler(self, u, p, f, c): self.scraper_ctrl.acao_iniciar_crawler(u, p, f, c)

    # --- FACTORS CONTROLLER (Homogeneização) ---
    def acao_calcular_fatores(self): self.factors_ctrl.calcular_fatores()

    # =========================================================================
    # LÓGICA ESPACIAL / GOOGLE / URBAN (Mantida aqui para simplificação de Threads)
    # =========================================================================

    def acao_conectar_google(self, key):
        """Conecta na API do Google Maps."""
        return self.google_engine.connect(key)

    def acao_geocodificar(self, addr_col, city_col):
        """Roda geocodificação (Nominatim) em Thread separada."""
        df = self.data_handler.get_data()
        if df is None: return

        def worker():
            if hasattr(self.view, 'tab_map'):
                self.view.tab_map.sub_geo.lbl_status.config(text="Processando... (Pode demorar)", foreground="blue")
            
            results = self.geocoding_engine.batch_geocode(df, addr_col, city_col)
            
            # Garante colunas
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
        t.daemon = True
        t.start()

    def _pos_geocoding(self, count):
        if hasattr(self.view, 'tab_map'):
            self.view.tab_map.sub_geo.lbl_status.config(text=f"Concluído! {count} endereços localizados.", foreground="green")
            self.view.tab_map.sub_geo.progress.stop()
            
        self._atualizar_view_dados()
        messagebox.showinfo("Sucesso", f"Geocodificação: {count} coordenadas encontradas.")

    def acao_criar_variavel_distancia(self, col_name, lat_target, lon_target):
        """Calcula distância geodésica simples (offline)."""
        try:
            df = self.data_handler.get_data()
            dists = self.spatial_engine.calculate_distances(df, 'Latitude', 'Longitude', lat_target, lon_target)
            df[col_name] = dists
            self._atualizar_view_dados()
            messagebox.showinfo("Sucesso", f"Variável '{col_name}' criada!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def acao_calcular_google_matrix(self, targets):
        """Usa Google Distance Matrix (Online/Pago)."""
        df = self.data_handler.get_data()
        if df is None: return

        if 'Latitude' not in df.columns:
            return messagebox.showerror("Erro", "Geocodifique os dados primeiro (Aba Mapa).")

        def worker():
            self.view.config(cursor="watch")
            try:
                results = self.google_engine.calcular_distancias_matriz(
                    df, 'Latitude', 'Longitude', targets
                )
                
                for name, dists in results.items():
                    col_name = f"Dist_{name}_m"
                    df[col_name] = dists
                
                self.view.after(0, lambda: [
                    self._atualizar_view_dados(),
                    self.view.config(cursor=""),
                    messagebox.showinfo("Sucesso", "Variáveis de distância (Google) adicionadas!")
                ])
                
            except Exception as e:
                self.view.after(0, lambda: [
                    self.view.config(cursor=""),
                    messagebox.showerror("Erro API Google", str(e))
                ])

        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    def acao_carregar_precos_bairro(self):
        """Chama UrbanEngine para calcular média por bairro."""
        df = self.data_handler.get_data()
        if df is None: return
        stats = self.urban_engine.calcular_preco_medio_bairro(df)
        if stats is not None and hasattr(self.view, 'tab_urban'):
            self.view.tab_urban._update_table(stats.reset_index())
        else:
            messagebox.showwarning("Aviso", "Não há dados suficientes ou aba Urbana não carregada.")

    def acao_baixar_infra_osm(self):
        """Baixa POIs do OpenStreetMap."""
        def worker():
            self.view.config(cursor="watch")
            try:
                res, _ = self.urban_engine.contar_infraestrutura()
                msg = "Infraestrutura encontrada (Cidade toda):\n"
                for k, v in res.items():
                    msg += f"{k}: {v}\n"
                self.view.after(0, lambda: messagebox.showinfo("OSM", msg))
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror("Erro OSM", str(e)))
            finally:
                self.view.after(0, lambda: self.view.config(cursor=""))

        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()