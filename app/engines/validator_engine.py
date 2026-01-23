class NBRValidator:
    def validar(self, stats_data):
        report = []
        diag = stats_data.get('Diagnosticos', {})
        n = stats_data['N_Amostras']
        k = stats_data['N_Variaveis']
        
        # 1. Grau de Fundamentação (Amostra)
        # Grau III: n >= 6(k+1) | Grau II: n >= 4(k+1) | Grau I: n >= 3(k+1)
        # NBR 14653-2 Tabela 1 Item 4
        k_real = k + 1 # considera intercepto
        g3 = 6 * k_real
        g2 = 4 * k_real
        g1 = 3 * k_real
        
        grau = "Reprovado"
        if n >= g3: grau = "Grau III (Excelente)"
        elif n >= g2: grau = "Grau II (Padrão)"
        elif n >= g1: grau = "Grau I (Básico)"
        
        status_n = "OK" if grau != "Reprovado" else "ERRO"
        report.append({
            "item": "Tamanho da Amostra (n)",
            "valor": f"{n}",
            "limite": f"Min: {g1}",
            "status": status_n,
            "msg": grau
        })

        # 2. R2
        r2 = stats_data['R2']
        s_r2 = "OK" if r2 >= 0.7 else "ALERTA"
        report.append({"item": "Determinação (R²)", "valor": f"{r2:.3f}", "limite": ">= 0.7", "status": s_r2, "msg": "Explicabilidade"})

        # 3. Teste F
        fp = stats_data['F_pvalue']
        s_f = "OK" if fp < 0.05 else "ERRO"
        report.append({"item": "Significância (F)", "valor": f"{fp:.2e}", "limite": "< 0.05", "status": s_f, "msg": "Validade do Modelo"})

        # 4. Normalidade
        sp = diag.get('Shapiro_P', 0)
        s_p = "OK" if sp > 0.05 else "ALERTA"
        report.append({"item": "Normalidade (Shapiro)", "valor": f"{sp:.3f}", "limite": "> 0.05", "status": s_p, "msg": "Distribuição Resíduos"})

        # 5. Homocedasticidade
        bp = diag.get('BreuschPagan_P', 0)
        s_bp = "OK" if bp > 0.05 else "ALERTA"
        report.append({"item": "Homocedasticidade", "valor": f"{bp:.3f}", "limite": "> 0.05", "status": s_bp, "msg": "Variância Constante"})

        # 6. Multicolinearidade
        vifs = diag.get('VIF', {})
        if vifs:
            max_v = max(vifs.values())
            s_vif = "OK" if max_v < 10 else "ALERTA"
            report.append({"item": "Multicolinearidade (VIF)", "valor": f"{max_v:.1f}", "limite": "< 10", "status": s_vif, "msg": "Correlação entre X"})

        return report