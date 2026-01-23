SisAval/
├── main.py                         # Ponto de entrada da aplicação
├── install_dependencies.py         # (Opcional) Script para instalar libs
├── README.md                       # Documentação do Projeto
│
├── app/
│   ├── __init__.py
│   │
│   ├── config/                     # Configurações e Constantes
│   │   ├── settings.py             # Cores, limites estatísticos, títulos
│   │   ├── tables.py               # Tabelas de Ross-Heidecke e Vida Útil
│   │   └── factors_db.py           # Tabelas de Fatores (Profundidade, Topografia)
│   │
│   ├── models/                     # Camada de Dados
│   │   ├── data_handler.py         # Manipulação de DataFrame (Pandas), Limpeza
│   │   └── project_state.py        # Salvar/Carregar projetos (.sav) com Pickle
│   │
│   ├── engines/                    # Motores de Cálculo (Lógica Pura)
│   │   ├── stats_engine.py         # Regressão Linear (OLS), Testes de Hipótese
│   │   ├── optimizer_engine.py     # IA: Brute Force e Stepwise para seleção de modelos
│   │   ├── validator_engine.py     # Validação NBR (Graus de Fundamentação)
│   │   ├── evolutionary_engine.py  # Método Evolutivo (CUB + Depreciação)
│   │   ├── factors_engine.py       # Homogeneização por Fatores
│   │   ├── spatial_engine.py       # Geocodificação e Distâncias (Geopy)
│   │   ├── scraper_engine.py       # Web Scraper (JSON-LD + Regex)
│   │   ├── scraper_trainer.py      # Treinador de Scraper (Reconhecimento de Padrões)
│   │   ├── pdf_engine.py           # Gerador de Relatórios PDF (FPDF2)
│   │   └── geocoding_engine.py     # Wrapper para Nominatim API
│   │
│   ├── controllers/                # Controladores (Pontes UI <-> Engine)
│   │   ├── app_controller.py       # Controlador Principal (Fachada)
│   │   ├── data_controller.py      # Gestão de dados e importação
│   │   ├── stats_controller.py     # Cálculos estatísticos e otimização
│   │   ├── tools_controller.py     # Ferramentas, Relatórios e Evolutivo
│   │   ├── scraper_controller.py   # Lógica do Web Scraper
│   │   └── factors_controller.py   # Lógica de Fatores
│   │
│   └── ui/                         # Interface Gráfica
│       ├── main_window.py          # Janela Principal com Notebook (Abas)
│       ├── plots.py                # Gerenciador de Gráficos (Matplotlib)
│       └── tabs/                   # Abas Principais
│           ├── tab_data.py         # Aba de Dados (Tabela + Definição)
│           ├── tab_regression.py   # Aba de Estatística (Resumo + Gráficos)
│           ├── tab_validation.py   # Aba de Validação NBR
│           ├── tab_plots.py        # Aba de Gráficos Avançados
│           ├── tab_optimizer.py    # Aba do Otimizador de Modelos
│           ├── tab_calculator.py   # Aba Calculadora de Valor
│           ├── tab_evolutionary.py # Aba Método Evolutivo
│           ├── tab_factors.py      # Aba Homogeneização por Fatores
│           ├── tab_map.py          # Aba Mapa e Geocodificação
│           ├── tab_databank.py     # Aba Banco de Dados Histórico
│           ├── tab_settings.py     # Aba Configurações
│           │
│           └── subtabs/            # Sub-componentes da Interface
│               ├── data_table.py, data_model.py, data_tools.py, data_desc.py
│               ├── regression_summary.py, regression_residuals.py, ...
│               ├── plots_exploratory.py, plots_diagnostic.py, plots_scenarios.py
│               ├── validation_checklist.py, validation_scoring.py, ...
│               ├── evol_constructions.py, evol_complementary.py, evol_summary.py
│               ├── scraper_run.py, scraper_calibrate.py, scraper_config.py
│               ├── map_view.py, map_geocoding.py, map_vars.py
│               ├── factors_setup.py, factors_grid.py
│               └── settings_ident.py, settings_stats.py, settings_eng.py