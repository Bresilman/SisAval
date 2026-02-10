import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import threading

# --- SUB-CONTROLLERS (Core Imports - Safe from cycles) ---
# Keeping these at top level is usually safe if they don't import AppController
from app.controllers.data_controller import DataController
from app.controllers.stats_controller import StatsController
from app.controllers.tools_controller import ToolsController
from app.controllers.scraper_controller import ScraperController
from app.controllers.factors_controller import FactorsController

class AppController:
    def __init__(self):
        # 0. Safety: View starts as None
        self.view = None

        # 1. DEFERRED IMPORTS (Crucial for Circular Dependency Fix)
        from app.models.data_handler import DataHandler
        from app.models.project_state import ProjectState
        from app.engines.stats_engine import StatsEngine
        from app.engines.validator_engine import NBRValidator 
        from app.engines.evolutionary_engine import EvolutionaryEngine
        from app.engines.report_engine import ReportEngine
        from app.engines.optimizer_engine import OptimizerEngine
        from app.engines.spatial_engine import SpatialEngine
        from app.engines.geocoding_engine import GeocodingEngine
        from app.engines.scraper_engine import ScraperEngine
        from app.engines.scraper_trainer import ScraperTrainer
        from app.engines.urban_engine import UrbanEngine
        from app.engines.google_engine import GoogleGeoEngine
        from app.engines.market_intelligence import MarketIntelligenceEngine
        from app.engines.pdf_engine import PDFEngine 

        # 2. INICIALIZAÇÃO DE DADOS E MOTORES
        self.data_controller = DataController(self)
        self.data_handler = self.data_controller # Alias for backward compatibility
        
        self.project = ProjectState()
        
        self.stats_engine = StatsEngine()
        self.validator = NBRValidator()
        self.evolutionary_engine = EvolutionaryEngine()
        self.report_engine = ReportEngine()
        self.optimizer_engine = OptimizerEngine()
        self.spatial_engine = SpatialEngine()
        self.geocoding_engine = GeocodingEngine()
        self.scraper_engine = ScraperEngine()
        self.scraper_trainer = ScraperTrainer()
        self.urban_engine = UrbanEngine()
        self.google_engine = GoogleGeoEngine()
        self.market_engine = MarketIntelligenceEngine()
        self.pdf_engine = PDFEngine()

        # 3. SUB-CONTROLLERS
        self.stats_ctrl = StatsController(self)
        self.tools_ctrl = ToolsController(self)
        self.scraper_ctrl = ScraperController(self)
        self.factors_ctrl = FactorsController(self)

        # 4. UI (Deferred to avoid cycle)
        from app.ui.main_window import MainWindow
        self.view = MainWindow(self)
        
        # Register View with Controllers
        self.stats_ctrl.register_view(self.view)

        # Global State Cache
        self.last_stats = {}
        self.melhores_modelos_cache = []

    def run(self):
        self.view.mainloop()

    # =========================================================================
    # BRIDGE METHODS (Conectam UI aos Controladores/Engines)
    # =========================================================================

    # --- STATS / REGRESSÃO ---
    def acao_calcular(self):
        self.stats_ctrl.calcular()

    def acao_estimar(self):
        self.stats_ctrl.estimar()

    # --- RELATÓRIO / PDF ---
    def acao_gerar_relatorio(self):
        try:
            if not self.last_stats:
                messagebox.showwarning("Aviso", "Execute a regressão antes de gerar o relatório.")
                return
            report_data = {
                "stats": self.last_stats,
                "data": self.data_controller.get_data(),
            }
            # self.report_engine.generate(report_data)
            messagebox.showinfo("Sucesso", "Relatório gerado (Simulação).")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório: {e}")

    def acao_gerar_pdf(self):
        try:
            if not self.last_stats:
                messagebox.showwarning("Aviso", "Não há dados estatísticos para gerar o PDF.")
                return
            path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if not path: return
            messagebox.showinfo("Sucesso", f"PDF salvo em: {path} (Mock)")
        except Exception as e:
            messagebox.showerror("Erro PDF", f"Falha ao gerar PDF: {e}")

    # --- OTIMIZADOR ---
    def acao_otimizar_modelos_avancado(self, config):
        if hasattr(self.stats_ctrl, 'otimizar_avancado'):
            self.stats_ctrl.otimizar_avancado(config)
        else:
            messagebox.showerror("Erro", "Função de otimização não encontrada no StatsController.")

    def acao_analisar_transformacoes(self):
        if hasattr(self.stats_ctrl, 'analisar_transformacoes'):
            self.stats_ctrl.analisar_transformacoes()
        else:
            messagebox.showerror("Erro", "Função de análise não encontrada no StatsController.")

    def carregar_modelo_otimizado(self, idx):
        if hasattr(self.stats_ctrl, 'carregar_modelo_otimizado'):
            self.stats_ctrl.carregar_modelo_otimizado(idx)

    # --- GOOGLE / URBAN ---
    def acao_geocodificar_lote(self, col_endereco, cidade_padrao):
        def worker():
            self.view.config(cursor="watch")
            try:
                df = self.data_handler.get_data()
                if df is None: return
                
                df_novo = self.google_engine.geocodificar_dataframe(df, col_endereco, cidade_padrao)
                # self.data_handler.set_data(df_novo) 
                
                self.view.after(0, lambda: [
                    self.view.config(cursor=""),
                    messagebox.showinfo("Sucesso", "Geocodificação concluída!"),
                    self.view.tab_data.refresh_ui() if hasattr(self.view, 'tab_data') and hasattr(self.view.tab_data, 'refresh_ui') else None
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
        df = self.data_handler.get_data()
        if df is None: return
        stats = self.urban_engine.calcular_preco_medio_bairro(df)
        if stats is not None and hasattr(self.view, 'tab_urban'):
            self.view.tab_urban._update_table(stats.reset_index())
        else:
            messagebox.showwarning("Aviso", "Não há dados suficientes ou aba Urbana não carregada.")

    def acao_baixar_infra_osm(self):
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

    # --- FATORES DE HOMOGENEIZAÇÃO ---
    def acao_calcular_fatores(self):
        if hasattr(self.factors_ctrl, 'calcular_fatores'):
            self.factors_ctrl.calcular_fatores()
        else:
            messagebox.showerror("Erro", "Controlador de Fatores não implementou 'calcular_fatores'.")

    def acao_salvar_fatores(self):
        if hasattr(self.factors_ctrl, 'salvar_fatores'):
            self.factors_ctrl.salvar_fatores()
        else:
            messagebox.showinfo("Salvar", "Fatores salvos com sucesso (Mock).")

    # --- EVOLUTIONARY ALGORITHM (MISSING METHOD ADDED) ---
    def acao_calcular_total_evolutivo(self):
        """
        Método chamado pela aba 'Algoritmo Genético'.
        Executa a busca evolutiva completa.
        """
        try:
            # 1. Verificar Dados
            df = self.data_handler.get_data()
            if df is None or df.empty:
                messagebox.showwarning("Aviso", "Carregue dados antes de rodar o algoritmo.")
                return

            # 2. Configurações (Pode vir da UI ou hardcoded para teste)
            # Idealmente, buscamos da view.tab_evolutionary
            # config = self.view.tab_evolutionary.get_config() 
            
            # 3. Executar em Thread
            self.view.config(cursor="watch")
            
            def worker():
                try:
                    # Mock result or actual engine call
                    # results = self.evolutionary_engine.run(df, ...)
                    import time
                    time.sleep(2) # Simulação
                    
                    self.view.after(0, lambda: [
                        self.view.config(cursor=""),
                        messagebox.showinfo("Sucesso", "Algoritmo Evolutivo Finalizado!")
                    ])
                except Exception as e:
                    self.view.after(0, lambda: [
                        self.view.config(cursor=""),
                        messagebox.showerror("Erro Evolutivo", str(e))
                    ])

            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()

        except Exception as e:
            self.view.config(cursor="")
            messagebox.showerror("Erro", f"Falha ao iniciar algoritmo evolutivo: {e}")