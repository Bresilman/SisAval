from datetime import datetime

class ReportEngine:
    """
    Gera o Memorial de Avaliação com Análise de Sensibilidade e Elasticidade.
    """
    
    def gerar_texto(self, stats_data):
        if not stats_data:
            return "Nenhum modelo estatístico calculado."

        # Extração de dados
        r2 = stats_data['R2']
        r_corr = stats_data['R_Correlation']
        n = stats_data['N_Amostras']
        diag = stats_data['Diagnosticos']
        usar_log = stats_data.get('Log_Ativo', False)
        
        # Dados novos
        importancia = stats_data.get('Importancia_Vars', {})
        elasticidade = stats_data.get('Elasticidade_Vars', {})
        
        data_hj = datetime.now().strftime("%d de %B de %Y")

        # --- INÍCIO DO LAUDO ---
        txt = "MEMORIAL DE AVALIAÇÃO ESTATÍSTICA (NBR 14.653)\n"
        txt += "="*60 + "\n\n"
        
        txt += "1. IDENTIFICAÇÃO\n"
        txt += f"Data de Emissão: {data_hj}\n"
        txt += "Software: SisAval (Engine Python/Statsmodels)\n\n"

        txt += "2. DADOS DA AMOSTRA\n"
        txt += f"Elementos pesquisados: {n}\n"
        if usar_log:
            txt += "Modelo: Regressão Linear Múltipla com transformação Logarítmica (Ln).\n\n"
        else:
            txt += "Modelo: Regressão Linear Múltipla (Escala Natural).\n\n"

        # --- 3. INDICADORES DE QUALIDADE ---
        txt += "3. DIAGNÓSTICO DO MODELO\n"
        
        # R2
        qualidade = "Fraca"
        if r2 > 0.8: qualidade = "Forte"
        elif r2 > 0.6: qualidade = "Moderada"
        txt += f"- Determinação (R²): {r2:.4f} ({qualidade} explicação da variância).\n"
        
        # Correlação
        txt += f"- Correlação (R): {r_corr:.4f}\n"
        
        # Teste F
        fp = stats_data['F_pvalue']
        txt += f"- Significância (Teste F): {fp:.2e} "
        txt += "(Aprovado)\n" if fp < 0.05 else "(Reprovado - Modelo ao acaso)\n"

        # Normalidade
        sp = diag.get('Shapiro_P', 0)
        txt += f"- Normalidade (Shapiro-Wilk): {sp:.4f} "
        txt += "(Resíduos Normais)\n" if sp > 0.05 else "(Não há normalidade)\n"

        # Homocedasticidade
        bp = diag.get('BreuschPagan_P', 0)
        txt += f"- Homocedasticidade (Breusch-Pagan): {bp:.4f} "
        txt += "(Variância Constante)\n" if bp > 0.05 else "(Heterocedasticidade detectada)\n"

        # Autocorrelação
        dw = diag.get('Durbin_Watson', 0)
        txt += f"- Autocorrelação (Durbin-Watson): {dw:.2f} "
        if 1.5 <= dw <= 2.5:
            txt += "(Sem autocorrelação - Bom)\n\n"
        else:
            txt += "(Indício de autocorrelação - Atenção)\n\n"

        # --- 4. ANÁLISE ECONÔMICA (NOVO) ---
        txt += "4. ANÁLISE ECONÔMICA DAS VARIÁVEIS\n"
        
        # 4.1 Importância (Quem manda mais)
        txt += "4.1 Grau de Influência (Importância Relativa):\n"
        if importancia:
            for var, peso in sorted(importancia.items(), key=lambda item: item[1], reverse=True):
                txt += f"   - {var}: {peso:.1f}%\n"
            txt += "   Interpretação: As variáveis no topo da lista são as determinantes principais do valor de mercado.\n\n"
        else:
            txt += "   (Cálculo não disponível)\n\n"

        # 4.2 Elasticidade (Sensibilidade)
        txt += "4.2 Elasticidade (Variação da Função):\n"
        txt += "   Representa a variação percentual no preço para cada 1% de variação na característica.\n"
        if elasticidade:
            for var, val in elasticidade.items():
                sinal = "Valorização" if val > 0 else "Desvalorização"
                txt += f"   - {var}: {val:.4f} ({sinal})\n"
        else:
            txt += "   (Cálculo não disponível)\n\n"

        # --- 5. RESULTADO FINAL ---
        txt += "5. EQUAÇÃO DE ESTIMATIVA\n"
        const = stats_data['Params']['const']
        if usar_log:
            txt += f"Ln(Unitário) = {const:.4f}"
            for var, coef in stats_data['Params'].items():
                if var != 'const':
                    txt += f" + ({coef:.4f} * Ln({var}))"
        else:
            txt += f"Unitário = {const:.4f}"
            for var, coef in stats_data['Params'].items():
                if var != 'const':
                    txt += f" + ({coef:.4f} * {var})"
        
        txt += "\n\n" + "="*60
        
        return txt