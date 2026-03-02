import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats

# --- 1. SIMULAÇÃO DO SEU CENÁRIO (PROBLEMÁTICO) ---
np.random.seed(42)
n = 300

# Variáveis (replicando seu output)
area = np.random.normal(120, 40, n)
idade = np.random.randint(0, 30, n)
dist_metro = np.random.uniform(50, 2000, n)
dist_parque = np.random.uniform(100, 3000, n)

# Dummies (Gerando conflito proposital)
# Se usarmos get_dummies sem drop_first, causamos multicolinearidade
zonas = np.random.choice(['Norte', 'Sul'], n)
padrao = np.random.choice(['Baixo', 'Médio', 'Alto'], n)

# Preço Real (Log-Linear na verdade)
# O mercado real é multiplicativo, não somativo!
preco_base = 250000 
fator_area = np.exp(0.005 * area) # Crescimento exponencial
fator_zona = np.where(zonas == 'Sul', 1.3, 1.0) # Sul vale 30% mais
fator_padrao = np.where(padrao == 'Alto', 1.5, np.where(padrao == 'Médio', 1.2, 1.0))

preco = preco_base * fator_area * fator_zona * fator_padrao * np.random.normal(1, 0.1, n)

df = pd.DataFrame({
    'area_privativa': area,
    'idade_anos': idade,
    'dist_metro': dist_metro,
    'dist_parque': dist_parque,
    'zona': zonas,
    'padrao': padrao,
    'preco_total': preco
})

# Criando Dummies (Simulando o seu erro de incluir muitas)
df = pd.get_dummies(df, columns=['zona', 'padrao'], dtype=int)
# O pandas cria: zona_Norte, zona_Sul, padrao_Alto, padrao_Baixo, padrao_Médio

print("--- DIAGNÓSTICO DO MODELO ORIGINAL (SEU ERRO) ---")
# Selecionamos variáveis que causam redundância (ex: zona_Norte E zona_Sul)
vars_erro = ['area_privativa', 'idade_anos', 'dist_metro', 'dist_parque', 
             'padrao_Baixo', 'padrao_Médio', 'zona_Norte', 'zona_Sul']

X_ruim = sm.add_constant(df[vars_erro])
mod_ruim = sm.OLS(df['preco_total'], X_ruim).fit()

print(f"Condition Number (Original): {mod_ruim.condition_number:.2e}")
print(f"Norm. Jarque-Bera (Original): {stats.jarque_bera(mod_ruim.resid)[0]:.2f} (Prob: {stats.jarque_bera(mod_ruim.resid)[1]:.4f})")
print("-> O modelo falha na normalidade e estabilidade.")

print("\n" + "="*50)
print("--- SOLUÇÃO: MODELO LOG-LINEAR CORRIGIDO ---")
print("="*50)

# CORREÇÃO 1: Transformação Log no Preço (Y)
# Isso lineariza a relação multiplicativa do mercado e resolve a Normalidade
df['ln_preco'] = np.log(df['preco_total'])

# CORREÇÃO 2: Seleção Correta de Dummies (Drop First)
# Removemos 'zona_Norte' (vira referência) e 'padrao_Alto' (vira referência)
vars_boas = ['area_privativa', 'idade_anos', 'dist_metro', 'dist_parque', 
             'padrao_Baixo', 'padrao_Médio', 'zona_Sul'] # Note: Sem Norte e sem Alto

X_bom = sm.add_constant(df[vars_boas])
mod_bom = sm.OLS(df['ln_preco'], X_bom).fit()

print(mod_bom.summary())

# --- CHECKLIST FINAL ---
print("\n--- CHECKLIST DE VALIDAÇÃO (NBR 14.653) ---")
print(f"1. R² Ajustado: {mod_bom.rsquared_adj:.4f} (Meta: > 0.75)")

# Teste de Normalidade
jb_stat, jb_p = stats.jarque_bera(mod_bom.resid)
print(f"2. Normalidade (JB): P-valor = {jb_p:.4f}")
if jb_p > 0.05:
    print("   -> APROVADO! Os resíduos agora são normais.")
else:
    print("   -> AINDA REPROVADO. Verifique outliers residuais.")

# Teste de Multicolinearidade (Condition Number)
print(f"3. Condition Number: {mod_bom.condition_number:.2f}")
if mod_bom.condition_number < 1000:
    print("   -> EXCELENTE! Multicolinearidade resolvida.")
elif mod_bom.condition_number < 2000:
    print("   -> ACEITÁVEL. (Provavelmente devido à escala da Área vs Distância).")
else:
    print("   -> CRÍTICO. Tente dividir as distâncias por 1000 (km) para melhorar.")

# Interpretação dos Coeficientes (Log-Linear)
beta_sul = mod_bom.params['zona_Sul']
impacto_sul = (np.exp(beta_sul) - 1) * 100
print(f"\nINTERPRETAÇÃO ECONÔMICA:")
print(f"Imóvel na Zona Sul vale {impacto_sul:.2f}% a mais que na Norte (Referência).")