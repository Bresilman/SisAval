import numpy as np
import pandas as pd
from scipy import stats
from app.config.factors_db import FATORES_TOPOGRAFIA, CONFIG_PROFUNDIDADE

class FactorsEngine:
    def __init__(self):
        pass

    def calcular_homogeneizacao(self, amostras, paradigma):
        """
        Calcula o valor homogeneizado para cada amostra.
        amostras: List of dicts (dados coletados)
        paradigma: Dict com dados do imóvel avaliando (Alvo)
        """
        resultados = []
        
        for amo in amostras:
            # 1. Valor Unitário Original
            vu_original = float(amo['preco']) / float(amo['area'])
            
            # 2. Fator Oferta (Transação vs Oferta)
            f_oferta = 0.90 if amo.get('tipo_valor') == 'Oferta' else 1.0
            
            # 3. Fator Localização (Manual por enquanto, ou percentual)
            f_local = float(amo.get('fator_local', 1.0))
            
            # 4. Fator Profundidade (Fórmula: (P_padrao / P_amostra)^0.5)
            # Trazendo a amostra para a realidade do paradigma
            prof_amostra = float(amo.get('profundidade', 0))
            prof_paradigma = float(paradigma.get('profundidade', 30))
            
            if prof_amostra > 0 and prof_paradigma > 0:
                # Se amostra tem 50m (pior) e paradigma 30m (melhor), amostra vale menos.
                # Precisamos subir o valor da amostra para comparar com o paradigma.
                # Formula Abunahman simplificada:
                f_prof = (prof_amostra / prof_paradigma) ** 0.5
            else:
                f_prof = 1.0

            # 5. Fator Topografia
            # Se amostra é Declive (0.7) e Paradigma é Plano (1.0).
            # Amostra vale 70% do plano. Para virar plano, multiplicamos por (1/0.7) = 1.42
            topo_amostra = amo.get('topografia', 'Plano')
            coef_amostra = FATORES_TOPOGRAFIA.get(topo_amostra, 1.0)
            
            # Normalização para o Paradigma (que assumimos ser Plano=1.0 base)
            # V_homog = V_orig * (1 / Coef_Amostra)
            f_topo = 1.0 / coef_amostra if coef_amostra > 0 else 1.0

            # Cálculo Final
            fator_total = f_oferta * f_local * f_prof * f_topo
            vu_homog = vu_original * fator_total
            
            resultados.append({
                "id": amo.get('id'),
                "vu_original": vu_original,
                "fatores": {
                    "oferta": f_oferta,
                    "local": f_local,
                    "prof": f_prof,
                    "topo": f_topo
                },
                "vu_homogeneizado": vu_homog
            })
            
        return resultados

    def calcular_estatisticas(self, lista_valores):
        """
        Calcula Média, Desvio, CV e Intervalo de Confiança (t-Student).
        """
        arr = np.array(lista_valores)
        n = len(arr)
        if n < 3: return None # NBR exige mínimo 3
        
        media = np.mean(arr)
        desvio = np.std(arr, ddof=1) # Amostral
        cv = (desvio / media) * 100
        
        # Intervalo de Confiança (80%)
        # t-student para n-1 graus de liberdade
        t_val = stats.t.ppf(1 - 0.10, df=n-1) # 0.10 pois é bicaudal (20% total -> 10% cada ponta)
        margem = t_val * (desvio / np.sqrt(n))
        
        ic_min = media - margem
        ic_max = media + margem
        
        # Saneamento (Critério de Chauvenet ou +/- 30% da média para simplificar)
        # NBR recomenda Chauvenet. Vamos usar Z-Score > 2 para simplificar este MVP
        z_scores = np.abs((arr - media) / desvio)
        outliers_indices = np.where(z_scores > 2)[0]
        
        return {
            "media": media,
            "desvio": desvio,
            "cv": cv,
            "ic_min": ic_min,
            "ic_max": ic_max,
            "outliers_idx": list(outliers_indices),
            "n": n
        }