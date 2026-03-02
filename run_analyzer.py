import customtkinter as ctk
import sys
import traceback

def main():
    """
    Ponto de entrada principal do SisAval - Módulo Analista.
    Configura o tema, instancia o Controlador (Maestro) e a Interface (View).
    """
    # 1. Configuração Visual Padrão (CustomTkinter)
    # Modos disponíveis: "System" (segue o SO), "Dark", "Light"
    ctk.set_appearance_mode("System") 
    # Temas disponíveis: "blue", "green", "dark-blue"
    ctk.set_default_color_theme("blue") 

    try:
        # 2. Importações Internas do SisAval
        # Importadas dentro do try/except para capturar erros de dependência facilmente
        from app.controllers.analyzer_controller import AnalyzerController
        from app.ui.analyzer_window import AnalyzerWindow
        
        # 3. Inicialização da Arquitetura MVC
        # Instancia o Controlador (A "mente" do aplicativo)
        controller = AnalyzerController()
        
        # Instancia a Janela Principal (A "face" do aplicativo), injetando o controlador
        app = AnalyzerWindow(controller)
        
        # Registra a View no Controlador (Comunicação bidirecional)
        controller.register_view(app)
        
        # 4. Início do Loop da Aplicação
        print("✅ Iniciando SisAval - Módulo Analista...")
        app.mainloop()
        
    except ImportError as e:
        # Tratamento amigável para bibliotecas ausentes
        print("\n❌ Erro de Importação Crítico:")
        print(f"Detalhes: {e}")
        print("\nPossível Causa: Uma biblioteca necessária não está instalada no seu ambiente Python.")
        print("Dica: Verifique se você ativou seu ambiente virtual e execute:")
        print("      pip install customtkinter pandas numpy statsmodels scipy")
        input("\nPressione Enter para sair...")
        sys.exit(1)
        
    except Exception as e:
        # Tratamento para erros de sintaxe ou falhas estruturais na inicialização
        print("\n❌ Erro Inesperado ao iniciar a aplicação:")
        traceback.print_exc()
        input("\nPressione Enter para sair...")
        sys.exit(1)

if __name__ == "__main__":
    main()