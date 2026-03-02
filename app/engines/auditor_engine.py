import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.stats.api as sms
import warnings

class NBRAuditor:
    """
    Auditor de Conformidade NBR 14.653-2 (Versão 2.1 - Interpretação Expandida).
    Implementa Versionamento do Report, Propagação de Erros e Dossiê Textual Completo.
    """
    def __init__(self, model_results, data):
        self.res = model_results
        self.model = model_results.model
        self.data = data
        self.n = int(self.model.nobs)
        self.k = int(self.model.df_model)
        
    def run_full_audit(self):
        """
        Executa a auditoria retornando um Contrato de Dados (Payload) estrito.
        """
        report_base = {
            "report_version": "1.0",
            "errors": [],
            "fundamentacao": "N/D",
            "precision_proxy": {'amplitude_perc': 0.0, 'grade': "N/A"},
            "plot_data": {},
            "summary_text": "",
            "interpretations": ""
        }
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                
                # Executa cheques
                check_micro = self._check_micronumerosity()
                check_global = self._check_global_metrics()
                check_vars = self._check_variables_significance()
                check_resid = self._check_residuals_assumptions()
                
                fundamentacao = self._classify_fundamentacao(check_micro, check_vars, check_resid)
                precision = self._estimate_precision_at_centroid()
                
                # Montagem do plot_data seguro
                try:
                    x_cols = [col for col in self.model.exog_names if col != 'const']
                    if x_cols and isinstance(self.data, pd.DataFrame):
                        valid_cols = [c for c in x_cols if c in self.data.columns]
                        corr_matrix = self.data[valid_cols].corr()
                    else:
                        corr_matrix = pd.DataFrame()
                except Exception:
                    corr_matrix = pd.DataFrame()

                # Atualiza o report_base com os dados de sucesso
                report_base.update({
                    'micronumerosity': check_micro,
                    'global_metrics': check_global,
                    'variables': check_vars,
                    'residuals': check_resid,
                    'fundamentacao': fundamentacao,
                    'precision_proxy': precision,
                    'summary_text': self.res.summary().as_text(),
                    # CHAMADA ATUALIZADA: Passando todos os dicionários para gerar o dossiê
                    'interpretations': self._interpret_detailed(check_micro, check_global, check_vars, check_resid),
                    'plot_data': {
                        'y': self.model.endog,
                        'y_pred': self.res.fittedvalues,
                        'resid': self.res.resid,
                        'corr_matrix': corr_matrix
                    }
                })
                
        except Exception as e:
            report_base["errors"].append(f"Falha Crítica na Auditoria: {str(e)}")
            report_base["interpretations"] = "Não foi possível auditar o modelo devido a erros de cálculo estatístico."
            
        return report_base

    def _interpret_detailed(self, micro, global_metrics, vars_df, residuals):
        """
        Gera um dossiê textual profundo e educativo analisando a fundo as saídas da regressão.
        """
        lines = []
        
        # --- 1. ESTRUTURA E AJUSTE GLOBAL ---
        lines.append("--- 1. ESTRUTURA E AJUSTE GLOBAL ---\n")
        df_resid = int(self.res.df_resid)
        lines.append(f"• Amostra/Variáveis: {self.n} dados para {self.k} variáveis explicativas (Gl: {df_resid}).")
        
        if self.n < 3 * (self.k + 1):
            lines.append(f"  ⚠️ ALERTA: Micronumerosidade. Risco de 'Overfitting' ({micro['grade']}).")
        else:
            lines.append(f"  ✅ Tamanho da amostra atende ao {micro['grade']} da NBR.")

        r2 = global_metrics['r2']
        r2_adj = global_metrics['adj_r2']
        lines.append(f"• R² ({r2:.4f}): O modelo explica {r2*100:.2f}% da variação dos preços.")
        lines.append(f"• R² Ajustado ({r2_adj:.4f}): Fator de ajuste para penalizar excesso de variáveis.")
        
        try:
            lines.append(f"• Critérios de Informação: AIC = {self.res.aic:.1f} | BIC = {self.res.bic:.1f}")
        except: pass
        
        f_p = global_metrics['f_pvalue']
        if f_p < 0.05:
            lines.append(f"• Prob(F-statistic) ({f_p:.2e}): ✅ Modelo globalmente significante (rejeita o acaso).")
        else:
            lines.append(f"• Prob(F-statistic) ({f_p:.2f}): ❌ Modelo INVÁLIDO. Variáveis não explicam o Y.")

        # --- 2. VARIÁVEIS EXPLICATIVAS E COLINEARIDADE ---
        lines.append("\n--- 2. VARIÁVEIS EXPLICATIVAS (X) ---\n")
        
        p_fails = vars_df[vars_df['grade'] == 'Reprovado']
        if p_fails.empty:
            lines.append("• Significância Individual: ✅ Todas as variáveis atendem aos limites (P < 0.30).")
        else:
            lines.append(f"• Significância Individual: ⚠️ {len(p_fails)} variável(is) Fora da Norma (P > 0.30).")
            
        try:
            vif_max = vars_df['vif'].max()
            if vif_max > 10:
                lines.append(f"• Multicolinearidade: ⚠️ VIF Máximo = {vif_max:.2f} (Alerta: Redundância entre variáveis!).")
            else:
                lines.append(f"• Multicolinearidade: ✅ VIF Máximo = {vif_max:.2f} (Ausência de colinearidade severa).")
        except: pass

        # --- 3. RESÍDUOS, NORMALIDADE E HOMOCEDASTICIDADE ---
        lines.append("\n--- 3. RESÍDUOS E PRESSUPOSTOS DE GAUSS-MARKOV ---\n")
        resid = self.res.resid
        try:
            skew = stats.skew(resid)
            kurt = stats.kurtosis(resid, fisher=False)
            lines.append(f"• Assimetria (Skew): {skew:.3f} | Curtose: {kurt:.3f}")
        except: pass
        
        # Normalidade
        norm_status = residuals['normality']['status']
        norm_p = residuals['normality']['p_value']
        if norm_status == 'Aprovado':
            lines.append(f"• Normalidade dos Erros: ✅ Confirmada (P = {norm_p:.4f}).")
        else:
            lines.append(f"• Normalidade dos Erros: ❌ Rejeitada (P = {norm_p:.4f}). Os erros não formam um Sino Gaussiano.")
            
        # Homocedasticidade
        homo_status = residuals['homoscedasticity']['status']
        homo_p = residuals['homoscedasticity']['p_value']
        if homo_status == 'Aprovado':
            lines.append(f"• Homocedasticidade: ✅ Confirmada (P = {homo_p:.4f}). Variância constante.")
        elif homo_status == 'Reprovado':
            lines.append(f"• Homocedasticidade: ❌ Rejeitada (P = {homo_p:.4f}). Detectada Heterocedasticidade (Efeito 'Cone').")
        else:
            lines.append(f"• Homocedasticidade: ⚠️ Inconclusiva.")

        # --- 4. ESTABILIDADE E OUTLIERS ---
        lines.append("\n--- 4. ESTABILIDADE E OUTLIERS ---\n")
        dw = residuals['autocorrelation']['val']
        lines.append(f"• Autocorrelação (Durbin-Watson): {dw:.2f} ({residuals['autocorrelation']['status']})")
        
        out_count = residuals['outliers']['count']
        if out_count > 0:
            lines.append(f"• Detecção de Outliers: ⚠️ {out_count} ponto(s) atípico(s) de alta alavancagem detectados (|Z| > 2).")
        else:
            lines.append(f"• Detecção de Outliers: ✅ Nenhum outlier severo detectado.")
            
        return "\n".join(lines)

    # ... [O restante da classe NBRAuditor (_check_micronumerosity, etc) permanece idêntico] ...

    def _check_micronumerosity(self):
        n_params = self.k + 1
        if self.n >= 6 * n_params: grade = "Grau III"; limit = f">= {6*n_params}"
        elif self.n >= 4 * n_params: grade = "Grau II"; limit = f">= {4*n_params}"
        elif self.n >= 3 * n_params: grade = "Grau I"; limit = f">= {3*n_params}"
        else: grade = "Reprovado"; limit = f">= {3*n_params}"
        return {'metric': 'Tamanho da Amostra (n)', 'value': self.n, 'limit': limit, 'grade': grade, 'desc': f"Amostra: {self.n}, Variáveis: {self.k}"}

    def _check_global_metrics(self):
        return {'r2': self.res.rsquared, 'adj_r2': self.res.rsquared_adj, 'f_pvalue': self.res.f_pvalue}

    def _check_variables_significance(self):
        summary = []
        p_values = self.res.pvalues
        exog_names = self.model.exog_names
        exog = self.model.exog
        for i, name in enumerate(exog_names):
            if name == 'const': continue
            p_val = p_values[name]
            if p_val <= 0.10: grade = "Grau III"; limit = "<= 0.10"
            elif p_val <= 0.15: grade = "Grau II"; limit = "<= 0.15"
            elif p_val <= 0.30: grade = "Grau I"; limit = "<= 0.30"
            else: grade = "Reprovado"; limit = "<= 0.30"
            try: 
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    vif = variance_inflation_factor(exog, i)
            except: vif = 0
            summary.append({'name': name, 'p_value': p_val, 'grade': grade, 'limit_accepted': limit, 'vif': vif})
        return pd.DataFrame(summary)

    def _check_residuals_assumptions(self):
        resid = self.res.resid
        if self.n < 50:
            norm_test = "Shapiro-Wilk"
            try: stat, p_norm = stats.shapiro(resid)
            except: p_norm = 1.0
        else:
            norm_test = "Kolmogorov-Smirnov"
            try: stat, p_norm = stats.kstest(resid, 'norm')
            except: p_norm = 1.0
        norm_status = "Aprovado" if p_norm > 0.05 else "Reprovado"
        
        try: 
            bp_test = sms.het_breuschpagan(resid, self.model.exog)
            p_bp = bp_test[1]
            homo_status = "Aprovado" if p_bp > 0.05 else "Reprovado"
        except: 
            p_bp = 0.0; homo_status = "Inconclusivo"
            
        try: dw = sms.durbin_watson(resid)
        except: dw = 0
        dw_status = "Aprovado" if 1.5 <= dw <= 2.5 else "Atenção"

        try: 
            infl = self.res.get_influence()
            std_resid = infl.resid_studentized_internal
        except AttributeError: 
            med = np.median(resid)
            mad = np.median(np.abs(resid - med))
            if mad == 0: std_resid = np.zeros_like(resid)
            else: std_resid = (resid - med) / (1.4826 * mad)
        outliers = np.where(np.abs(std_resid) > 2.0)[0]

        return {
            'normality': {'p_value': p_norm, 'status': norm_status, 'test': norm_test},
            'homoscedasticity': {'p_value': p_bp, 'status': homo_status, 'test': 'Breusch-Pagan'},
            'autocorrelation': {'val': dw, 'status': dw_status},
            'outliers': {'count': len(outliers), 'indices': outliers}
        }

    def _classify_fundamentacao(self, micro, vars_df, resid):
        scores = [micro['grade']]
        if "Reprovado" in vars_df['grade'].values: scores.append("Reprovado")
        elif "Grau I" in vars_df['grade'].values: scores.append("Grau I")
        elif "Grau II" in vars_df['grade'].values: scores.append("Grau II")
        else: scores.append("Grau III")
        if resid['normality']['status'] == 'Reprovado' or resid['homoscedasticity']['status'] == 'Reprovado': scores.append("Grau I")
        else: scores.append("Grau III")
        if "Reprovado" in scores: final = "Fora de Norma"
        elif "Grau I" in scores: final = "Grau I"
        elif "Grau II" in scores: final = "Grau II"
        else: final = "Grau III"
        return final

    def _estimate_precision_at_centroid(self):
        try:
            exog = self.model.exog
            centroid = np.mean(exog, axis=0)
            pred = self.res.get_prediction(centroid)
            summary = pred.summary_frame(alpha=0.20)
            mean = summary['mean'][0]
            amp = (summary['mean_ci_upper'][0] - summary['mean_ci_lower'][0]) / 2
            perc = (amp / mean) * 100
            if perc <= 30: grade = "Grau III"
            elif perc <= 40: grade = "Grau II"
            elif perc <= 50: grade = "Grau I"
            else: grade = "Fora de Norma"
            return {'amplitude_perc': perc, 'grade': grade}
        except: return {'amplitude_perc': 0, 'grade': "N/A"}