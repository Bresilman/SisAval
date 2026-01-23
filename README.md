SisAval - Sistema de Engenharia de Avaliações (NBR 14.653)

O SisAval é uma aplicação desktop profissional desenvolvida em Python para auxiliar engenheiros de avaliações e peritos na determinação do valor de mercado de imóveis urbanos.

O software foi projetado para atender rigorosamente aos critérios da NBR 14.653-2 da ABNT, oferecendo ferramentas avançadas de inferência estatística, métodos de custo e inteligência de dados.

Funcionalidades Principais

 1. Inferência Estatística (Regressão Linear)

Motor Poderoso: Baseado na biblioteca statsmodels (OLS).

Modelos Suportados: Linear e Log-Log (Cobb-Douglas).

Diagnóstico Completo: Testes automáticos de F (Significância), t-Student, Normalidade (Shapiro-Wilk), Homocedasticidade (Breusch-Pagan), Autocorrelação (Durbin-Watson) e Multicolinearidade (VIF).

Análise Econômica: Cálculo automático de Grau de Influência e Elasticidade das variáveis.

 2. Otimizador de Modelos (IA)

Automação: Encontra o melhor modelo matemático testando milhares de combinações em segundos.

Algoritmos: Suporte a Força Bruta e Stepwise Regression.

Segurança: Filtros de Coerência de Sinais (impede modelos que violem a lógica de mercado) e filtros normativos (P-valor < 10%).

 3. Método Evolutivo & Fatores

Custo de Reedição: Módulo para cálculo de construções usando CUB, BDI e Depreciação (Ross-Heidecke).

Homogeneização: Tratamento por Fatores para amostras pequenas.

 4. Inteligência de Mercado

Web Scraper Integrado: Importe dados de portais imobiliários (OLX, VivaReal) salvos localmente. Inclui extrator inteligente via JSON-LD.

Mapas & Geocodificação: Visualização espacial das amostras e conversão automática de endereços para coordenadas (Lat/Lon).

Banco de Dados: Histórico de preços para análise de tendências.

 5. Relatórios Profissionais

Geração de Laudos em PDF formatados, com tabelas, estatísticas, gráficos de diagnóstico e enquadramento na norma.

 Arquitetura e Tecnologias

O projeto segue o padrão de arquitetura MVC (Model-View-Controller) para garantir organização e escalabilidade.

Linguagem: Python 3

Interface (GUI): Tkinter (Nativo) com temas ttk.

Análise de Dados: Pandas, NumPy, SciPy.

Estatística: Statsmodels.

Gráficos: Matplotlib, Seaborn.

Mapas: TkinterMapView, Geopy.

Relatórios: FPDF2.

Scraping: BeautifulSoup4.

 Instalação e Uso

Clone o repositório:

git clone [https://github.com/seu-usuario/sisaval.git](https://github.com/seu-usuario/sisaval.git)
cd sisaval


Crie um ambiente virtual (recomendado):

python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate


Instale as dependências:

pip install pandas numpy statsmodels matplotlib scipy openpyxl fpdf2 beautifulsoup4 tkintermapview geopy seaborn


Execute o sistema:

python main.py


📚 Como Usar (Fluxo Básico)

Aba Dados: Carregue sua planilha Excel ou use o botão "Importar Web" para ler anúncios salvos. Use a ferramenta "Sanear" para remover outliers.

Aba Otimizador: Defina os sinais esperados (ex: Área = Positivo) e clique em "Rodar Robô". O sistema sugerirá o melhor modelo.

Aba Estatística: Analise os gráficos e a tabela de resíduos. Se houver pontos vermelhos (Outliers), exclua-os na aba Dados.

Aba Calculadora: Insira os dados do imóvel avaliando para obter o Valor de Mercado e o Campo de Arbítrio.

Aba Relatório: Preencha o diagnóstico de mercado e clique em "Gerar PDF".

🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir Issues ou Pull Requests para melhorar o código, adicionar novos testes estatísticos ou refinar a interface.

📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
