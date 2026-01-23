# Tabelas de Fatores para Homogeneização (NBR 14.653)

# Fator Oferta (Elasticidade)
PADRAO_OFERTA = 0.90 # Desconto padrão de 10%

# Tabela de Profundidade (Exemplo Simplificado - Método Abunahman/Incra)
# Fórmula base: (Profundidade_Padrao / Profundidade_Real) ^ Exponente
# Exponente varia de 0.5 (Raiz) a 1.0 dependendo da região
CONFIG_PROFUNDIDADE = {
    "padrao_min": 20,
    "padrao_max": 30,
    "exponente": 0.5
}

# Tabela de Topografia (Sugestão IBAPE)
# Fator para trazer para o Paradigma (Plano)
# Se o paradigma é plano (1.0) e a amostra é declive (0.7), 
# valor da amostra deve ser dividido ou multiplicado? 
# Homogeneização: V_homog = V_amostra * F_transposição
# Se amostra é pior (declive), ela vale menos. Para comparar com plano, aumentamos.
FATORES_TOPOGRAFIA = {
    "Plano": 1.00,
    "Aclive Leve (<5%)": 0.95,
    "Aclive Médio": 0.90,
    "Aclive Acentuado": 0.80,
    "Declive Leve": 0.90,
    "Declive Acentuado": 0.70
}

# Fator Frente (Testada)
# Referência: Frente Projetada / Frente Referência
FATORES_FRENTE_EXP = 0.25 # Raiz quarta é comum