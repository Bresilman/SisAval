# Tabelas de Referência para Engenharia de Avaliações

# Tabela de Vida Útil (Referência: IBAPE/SP e outras literaturas)
VIDA_UTIL_REFERENCIA = {
    "Residencial Casa (Alvenaria)": 60,
    "Residencial Apartamento": 60,
    "Residencial Madeira": 40,
    "Comercial / Escritórios": 60,
    "Galpão (Alvenaria/Metálica)": 40,
    "Galpão (Pré-Moldado)": 40,
    "Loja": 60,
    "Indústria": 40
}

# Tabela de Depreciação por Estado de Conservação (Ross-Heidecke)
# Valores representam a penalidade (depreciação extra) a ser somada
# à depreciação por idade.
# Fonte: Adaptação da Tabela Ross-Heidecke (Curva Média 'e')
DEPRECIACAO_ESTADO = {
    "Novo": 0.000,
    "Entre Novo e Regular": 0.032, # Equivalente a 'Bom' em algumas literaturas
    "Bom": 0.032,
    "Regular": 0.132,
    "Entre Regular e Reparos Simples": 0.252,
    "Reparos Simples": 0.352,
    "Entre Reparos Simples e Importantes": 0.486,
    "Reparos Importantes": 0.620,
    "Entre Reparos Importantes e Sem Valor": 0.810,
    "Sem Valor": 1.000
}

# Valor Residual Mínimo (Sucata)
VALOR_RESIDUAL_MINIMO = 0.20 # 20%