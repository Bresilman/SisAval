# app/config/report_config.py

"""
Repositório Estático e Gerenciador de Perfis para a Geração de Laudos.
Define textos padrão (Boilerplate), estilos visuais e metadados estruturais.
Garante que a customização do laudo (Branding) não exija alterações no motor lógico.
"""

REPORT_CONFIG = {
    # --- METADADOS E BRANDING ---
    "branding": {
        "empresa_nome": "SisAval Analista - Avaliações de Engenharia",
        "footer_text": "Laudo Técnico gerado eletronicamente em conformidade com a ABNT NBR 14.653-2.",
        "logo_path": None  # Caminho absoluto para a logomarca (Ex: 'C:/assets/logo.png')
    },

    # --- TEXTOS PADRÕES (BOILERPLATE) ---
    "textos": {
        "introducao": (
            "Este laudo técnico tem por objetivo a determinação do valor de mercado do imóvel "
            "avaliando, utilizando-se de inferência estatística e modelagem matemática."
        ),
        "metodologia": (
            "A metodologia aplicada baseia-se no Método Comparativo Direto de Dados de Mercado (MCDDM), "
            "com tratamento por Inferência Estatística, em estrita observância às diretrizes da "
            "norma ABNT NBR 14.653-2:2011 (Avaliação de Bens - Parte 2: Imóveis Urbanos)."
        ),
        "conclusao": (
            "Com base na amostra coletada e no modelo estatístico regressivo calibrado e validado, "
            "o valor final adotado representa a tendência central do mercado para o imóvel em análise."
        )
    },

    # --- ESTILIZAÇÃO (PDF) ---
    "estilos": {
        # Margens ABNT (em milímetros)
        "margens": {"top": 30, "bottom": 20, "left": 30, "right": 20},
        
        # Tipografia Fallback: Tenta usar Arial, caso falhe, usa Helvetica (Padrão PDF)
        "font_family": "Helvetica", 
        
        "tamanhos": {
            "titulo": 16,
            "subtitulo": 12,
            "corpo": 11,
            "rodape": 8
        },
        
        # Cores em RGB
        "cores": {
            "primaria": (0, 51, 102),     # Azul Escuro Institucional
            "texto": (40, 40, 40),        # Cinza Chumbo Escuro (Melhor leitura que preto 100%)
            "sucesso": (0, 128, 0),       # Verde
            "alerta": (255, 140, 0),      # Laranja
            "erro": (200, 0, 0)           # Vermelho
        }
    }
}