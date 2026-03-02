import customtkinter as ctk
from app.ui.tabs.subtabs.opt_config import OptConfig
from app.ui.tabs.subtabs.opt_results import OptResults

class TabOptimizer(ctk.CTkFrame):
    """
    Aba Principal do Otimizador.
    Refatorada para usar Abas Reais (TabView) para separar Configuração e Resultados.
    Usa .pack() para evitar conflitos de geometria com o pai.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- LAYOUT PRINCIPAL: TABVIEW ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_view.add("⚙️ Configuração")
        self.tab_view.add("📊 Resultados")
        
        # --- ABA 1: CONFIGURAÇÃO ---
        self.frame_config = self.tab_view.tab("⚙️ Configuração")
        
        # Sub-aba de Configuração
        self.sub_config = OptConfig(self.frame_config)
        self.sub_config.pack(fill="both", expand=True, padx=5, pady=5)
        
        # CRÍTICO: Conecta o botão da sub-aba à função de execução deste container
        # A sub-aba OptConfig cria o visual do botão, mas a lógica está aqui
        if hasattr(self.sub_config, 'btn_run'):
            self.sub_config.btn_run.configure(command=self._on_run)
        
        # --- ABA 2: RESULTADOS ---
        self.frame_results = self.tab_view.tab("📊 Resultados")
        
        self.sub_results = OptResults(self.frame_results, controller)
        self.sub_results.pack(fill="both", expand=True, padx=5, pady=5)

    def update_candidates(self, columns):
        """Repassa a atualização de colunas para a sub-aba de configuração."""
        if hasattr(self.sub_config, 'combo_target'):
            self.sub_config.combo_target.configure(values=columns)
            
            # Se a seleção atual não for válida, reseta
            current_target = self.sub_config.combo_target.get()
            if columns and current_target not in columns:
                self.sub_config.combo_target.set(columns[0])
                current_target = columns[0]
            
            # Atualiza também a lista de checkboxes (X)
            if hasattr(self.sub_config, 'update_candidates_list'):
                self.sub_config.update_candidates_list(columns)

    def _on_run(self):
        """Coleta dados da UI e chama o Controller."""
        print("Botão Executar Otimizador Clicado!") # Debug
        
        settings = self.sub_config.get_settings()
        target = settings.pop('target')
        
        # Coleta candidatos
        candidates = settings.pop('candidates', [])
        
        # Fallback de segurança
        if not candidates and self.controller.dataset is not None:
            all_cols = list(self.controller.dataset.columns)
            candidates = [c for c in all_cols if c != target]
            
        if self.controller.dataset is not None:
            # Muda para aba de resultados imediatamente para dar feedback visual
            self.tab_view.set("📊 Resultados")
            self.set_status("Iniciando motor de otimização...")
            
            self.controller.acao_rodar_otimizador(target, candidates, settings)
        else:
            print("Erro: Nenhum dataset carregado no controller.")

    # Métodos Proxy para o Controller chamar
    def set_status(self, msg):
        """Atualiza barra de status na aba de resultados."""
        self.sub_results.update_status(msg)
        
    def display_results(self, results):
        """Exibe resultados e foca na aba correta."""
        self.sub_results.display_results(results)
        self.tab_view.set("📊 Resultados")