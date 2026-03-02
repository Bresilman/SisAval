import pandas as pd
import numpy as np
import random

def gerar_dados_imobiliarios(n_amostras=200, seed=42):
    """
    Gera um dataset sintético para avaliação de imóveis.
    n_amostras: Número de imóveis a serem gerados.
    seed: Semente para reprodutibilidade.
    """
    np.random.seed(seed)
    random.seed(seed)

    print(f"Gerando {n_amostras} amostras imobiliárias...")

    # --- 1. CARACTERÍSTICAS FÍSICAS ---
    # Área Privativa: Distribuição Normal (Média 100m², Desvio 40m²)
    # Clip para evitar áreas negativas ou absurdamente pequenas/grandes
    area = np.random.normal(100, 40, n_amostras)
    area = np.clip(area, 30, 450).round(2)

    # Quartos: Dependente da área (Correlação positiva)
    # Lógica simples: 1 quarto a cada 40m², com variação
    quartos = (area / 40).astype(int) + np.random.randint(-1, 2, n_amostras)
    quartos = np.clip(quartos, 1, 6)

    # Vagas: Dependente da área e sorte
    vagas = (area / 70).astype(int) + np.random.randint(0, 2, n_amostras)
    vagas = np.clip(vagas, 0, 5)

    # Idade Aparente (Anos): Distribuição Uniforme
    idade = np.random.randint(0, 50, n_amostras)

    # --- 2. CARACTERÍSTICAS GEOGRÁFICAS (Distâncias em metros) ---
    # Simulando distâncias de caminhada (Network Distance)
    # Log-normal para simular que muitos estão perto, mas alguns estão bem longe
    dist_metro = np.random.lognormal(mean=6.5, sigma=0.8, size=n_amostras)
    dist_metro = np.clip(dist_metro, 50, 5000).round(0)

    dist_parque = np.random.lognormal(mean=7.0, sigma=0.7, size=n_amostras)
    dist_parque = np.clip(dist_parque, 100, 4000).round(0)

    dist_shopping = np.random.lognormal(mean=7.5, sigma=0.6, size=n_amostras)
    dist_shopping = np.clip(dist_shopping, 200, 8000).round(0)
    
    # Farmácias são mais comuns, distâncias menores
    dist_farmacia = np.random.lognormal(mean=5.5, sigma=0.5, size=n_amostras)
    dist_farmacia = np.clip(dist_farmacia, 10, 1500).round(0)

    # --- 3. CARACTERÍSTICAS QUALITATIVAS ---
    
    # Padrão Construtivo
    opcoes_padrao = ['Baixo', 'Médio', 'Alto']
    pesos_padrao = [0.3, 0.5, 0.2] # 50% são Médio padrão
    padrao = np.random.choice(opcoes_padrao, n_amostras, p=pesos_padrao)

    # Zona (Localização)
    opcoes_zona = ['Norte', 'Sul', 'Centro'] # Sul será a mais valorizada na nossa lógica
    zona = np.random.choice(opcoes_zona, n_amostras)

    # --- 4. PRECIFICAÇÃO (A "Fórmula Secreta" do Mercado) ---
    # Vamos definir um valor base e aplicar multiplicadores
    
    preco_base_m2 = 5000 
    
    precos = []
    
    for i in range(n_amostras):
        valor_m2 = preco_base_m2
        
        # Valorização por Padrão (Dummies implícitas na lógica)
        if padrao[i] == 'Médio': valor_m2 *= 1.2
        elif padrao[i] == 'Alto': valor_m2 *= 1.6
        
        # Valorização por Zona
        if zona[i] == 'Centro': valor_m2 *= 1.1
        elif zona[i] == 'Sul': valor_m2 *= 1.4
        
        # Depreciação por Idade (Ross-Heidecke simplificado: -0.5% ao ano)
        fator_idade = max(0.6, 1 - (idade[i] * 0.005)) 
        valor_m2 *= fator_idade
        
        # Penalização por Distância (Logarítmica - Perto vale muito mais)
        # Se dist_metro for pequena, penalidade é pequena. Se for grande, penalidade aumenta.
        # Mas para simplificar a regressão linear inversa:
        # Vamos assumir que a cada 1km longe do metrô, perde R$ 200/m²
        penalidade_metro = (dist_metro[i] / 1000) * 200
        valor_m2 -= penalidade_metro
        
        # Valorização por Vagas
        valor_m2 += (vagas[i] * 150) # R$ 150/m² a mais por vaga (diluído na área)

        # Cálculo Final com Ruído Aleatório (Erro de mercado +/- 10%)
        preco_final = (valor_m2 * area[i])
        ruido = np.random.normal(0, preco_final * 0.10) 
        precos.append(max(50000, preco_final + ruido)) # Mínimo 50k

    # --- 5. CRIAÇÃO DO DATAFRAME ---
    df = pd.DataFrame({
        'id': range(1, n_amostras + 1),
        'area_privativa': area,
        'quartos': quartos,
        'vagas': vagas,
        'idade_anos': idade,
        'dist_metro': dist_metro,
        'dist_parque': dist_parque,
        'dist_shopping': dist_shopping,
        'dist_farmacia': dist_farmacia,
        'padrao': padrao,
        'zona': zona,
        'preco_total': np.round(precos, 2)
    })

    # --- 6. TRATAMENTO DE DUMMIES (One-Hot Encoding) ---
    # drop_first=True evita a "Armadilha das Dummies" (Multicolinearidade Perfeita)
    df_final = pd.get_dummies(df, columns=['padrao', 'zona'], drop_first=True, dtype=int)

    return df_final

# --- EXECUÇÃO ---
if __name__ == "__main__":
    df_imoveis = gerar_dados_imobiliarios(300) # Gerar 300 dados
    
    # Salvando em CSV
    nome_arquivo = 'dados_imoveis_sinteticos.csv'
    df_imoveis.to_csv(nome_arquivo, index=False, sep=',', decimal='.')
    
    print(f"\nArquivo '{nome_arquivo}' gerado com sucesso!")
    print("\nVisualizando as primeiras linhas:")
    print(df_imoveis.head())
    
    print("\nColunas geradas (incluindo Dummies):")
    print(df_imoveis.columns.tolist())

