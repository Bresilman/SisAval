from app.config.tables import DEPRECIACAO_ESTADO, VALOR_RESIDUAL_MINIMO, VIDA_UTIL_REFERENCIA

class EvolutionaryEngine:
    def __init__(self):
        self.vida_util_referencia = VIDA_UTIL_REFERENCIA
        self.penalidade_estado = DEPRECIACAO_ESTADO
        self.k_min = VALOR_RESIDUAL_MINIMO

    def calcular_ross_heidecke(self, idade, vida_util, estado_conservacao):
        if vida_util <= 0: vida_util = 60 
        percent_vida = (idade / vida_util) * 100
        if percent_vida > 100: percent_vida = 100

        x = percent_vida / 100.0
        dep_idade = (x**2 + x) / 2.0
        penalidade = self.penalidade_estado.get(estado_conservacao, 0.0)
        
        dep_total = dep_idade + penalidade
        if dep_total > 1.0: dep_total = 1.0
        
        k = 1.0 - dep_total
        if k < self.k_min: k = self.k_min
        return round(k, 4)

    def calcular_benfeitoria_principal(self, area, cub, bdi, idade, vida, estado):
        """
        Calcula valor da construção principal com BDI.
        """
        # Custo Novo = Area * CUB * (1 + BDI/100)
        fator_bdi = 1 + (bdi / 100.0)
        custo_novo = area * cub * fator_bdi
        
        # Depreciação
        k = self.calcular_ross_heidecke(idade, vida, estado)
        valor_atual = custo_novo * k

        return {
            "Custo_Novo": custo_novo,
            "Valor_Atual": valor_atual,
            "Fator_K": k,
            "BDI_Aplicado": bdi
        }

    def calcular_total_evolutivo(self, v_terreno, soma_principal, soma_complementar, fc):
        """
        Soma: Terreno + (Principal + Complementar) * FC? 
        NÃO. O FC (Fator Comercialização) aplica-se sobre a soma (Terreno + Benfeitorias).
        """
        soma_benfeitorias = soma_principal + soma_complementar
        
        # Valor de Mercado = (Terreno + Benfeitorias) * FC
        valor_total = (v_terreno + soma_benfeitorias) * fc
        
        return {
            "Valor_Terreno": v_terreno,
            "Soma_Principal": soma_principal,
            "Soma_Complementar": soma_complementar,
            "Total_Benfeitorias": soma_benfeitorias,
            "Fator_Comercializacao": fc,
            "Valor_Final": valor_total
        }