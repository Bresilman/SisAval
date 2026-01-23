from fpdf import FPDF
from datetime import datetime
import pandas as pd

class PDFReport(FPDF):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.set_auto_page_break(auto=True, margin=15)
        self.set_title(settings.get('titulo', "Laudo de Avaliação"))

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.settings.get('titulo', "LAUDO DE AVALIAÇÃO"), border=False, ln=True, align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 5, f"Responsável Técnico: {self.settings.get('avaliador', '')}", ln=True, align="C")
        self.ln(5)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"SisAval - Página {self.page_no()}", align="C")

    def chapter_title(self, label):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, label, ln=True, fill=True, border=0)
        self.ln(4)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, text)
        self.ln(5)

class PDFEngine:
    def gerar_pdf(self, filename, context):
        pdf = PDFReport(context['settings'])
        pdf.add_page()
        
        # 1. IDENTIFICAÇÃO
        pdf.chapter_title("1. IDENTIFICAÇÃO")
        info = [
            ["Solicitante", context['texts'].get('cliente', '')],
            ["Finalidade", context['texts'].get('finalidade', '')],
            ["Cidade/Data", f"{context['settings'].get('cidade', '')}, {datetime.now().strftime('%d/%m/%Y')}"]
        ]
        with pdf.table(col_widths=(40, 150)) as table:
            for row in info:
                r = table.row()
                r.cell(row[0], style="B")
                r.cell(row[1])
        pdf.ln()

        # 2. DIAGNÓSTICO DE MERCADO
        pdf.chapter_title("2. DIAGNÓSTICO DE MERCADO")
        pdf.body_text(context['texts'].get('diagnostico', ''))

        # 3. METODOLOGIA E ESTATÍSTICA
        pdf.chapter_title("3. TRATAMENTO ESTATÍSTICO (MÉTODO COMPARATIVO)")
        s = context['stats']
        
        # Metrics Table
        metrics = [
            ["Métrica", "Resultado", "Diagnóstico"],
            ["Coef. Determinação (R²)", f"{s['R2']:.4f}", "Grau III" if s['R2'] >= 0.75 else "Grau II" if s['R2'] >= 0.50 else "Grau I"],
            ["Significância (Teste F)", f"{s['F_pvalue']:.2e}", "Aprovado" if s['F_pvalue'] < 0.05 else "Reprovado"],
            ["Normalidade (Shapiro)", f"{s['Diagnosticos'].get('Shapiro_P', 0):.4f}", "Normal" if s['Diagnosticos'].get('Shapiro_P', 0) > 0.05 else "Não Normal"],
            ["Homocedasticidade", f"{s['Diagnosticos'].get('BreuschPagan_P', 0):.4f}", "Homocedástico" if s['Diagnosticos'].get('BreuschPagan_P', 0) > 0.05 else "Heterocedástico"]
        ]
        
        with pdf.table(text_align="C") as table:
            for data_row in metrics:
                row = table.row()
                for datum in data_row:
                    row.cell(str(datum))
        pdf.ln(5)
        
        # Equation
        pdf.set_font("Courier", "", 9)
        pdf.multi_cell(0, 5, f"Equação do Modelo:\n{s.get('Equacao_Texto', 'Y = ...')}")
        pdf.set_font("Helvetica", "", 11)
        pdf.ln()

        # 4. GRÁFICOS
        if context.get('plot_image_path'):
            pdf.chapter_title("4. GRÁFICOS DE DIAGNÓSTICO")
            # Center image
            pdf.image(context['plot_image_path'], x=15, w=180)
            pdf.ln()

        # 5. DADOS DA AMOSTRA (Optional)
        if context['options']['include_data'] and context['df'] is not None:
            pdf.add_page()
            pdf.chapter_title("5. DADOS DA AMOSTRA")
            df = context['df']
            
            # Select relevant columns (Limit width)
            display_cols = list(df.columns)[:7] # Take first 7 columns
            
            pdf.set_font("Helvetica", "", 7)
            with pdf.table() as table:
                header = table.row()
                for col in display_cols:
                    header.cell(str(col), style="B")
                
                for _, row_data in df.iterrows():
                    row = table.row()
                    for col in display_cols:
                        val = str(row_data[col])
                        if len(val) > 20: val = val[:17] + "..." # Truncate
                        row.cell(val)
            pdf.ln()

        # 6. MÉTODO EVOLUTIVO (Important for you!)
        evol = context.get('evolutionary')
        has_evol = evol and (evol['principal'] or evol['complementary'])
        
        if has_evol:
            pdf.add_page()
            pdf.chapter_title("6. MÉTODO EVOLUTIVO (CUSTO DE REEDIÇÃO)")
            
            # Main Constructions
            if evol['principal']:
                pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 8, "Edificações Principais", ln=True)
                pdf.set_font("Helvetica", "", 9)
                cols_p = ["Nome", "Área", "CUB", "BDI", "Valor Novo", "K", "Valor Atual"]
                with pdf.table() as table:
                    h = table.row()
                    for c in cols_p: h.cell(c, style="B")
                    for item in evol['principal']:
                        r = table.row()
                        for v in item: r.cell(str(v))
                pdf.ln(5)

            # Complementary
            if evol['complementary']:
                pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 8, "Obras Complementares", ln=True)
                pdf.set_font("Helvetica", "", 9)
                # Adjust columns based on what tools_controller sends (Desc, Qtde, Unit, BDI, Novo, K, Atual)
                cols_c = ["Descrição", "Qtde", "Unit.", "BDI", "Valor Novo", "K", "Valor Atual"]
                with pdf.table() as table:
                    h = table.row()
                    for c in cols_c: h.cell(c, style="B")
                    for item in evol['complementary']:
                        r = table.row()
                        for v in item: r.cell(str(v))
                pdf.ln(5)

            # Summary Evolutivo
            if evol['summary']:
                pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 8, "Fechamento do Método Evolutivo", ln=True)
                summ = evol['summary']
                data_sum = [
                    ["Valor do Terreno", summ.get('land', 'R$ 0,00')],
                    ["Total Benfeitorias Principais", summ.get('main', 'R$ 0,00')],
                    ["Total Obras Complementares", summ.get('comp', 'R$ 0,00')],
                    ["VALOR TOTAL", summ.get('total', 'R$ 0,00')],
                ]
                with pdf.table() as table:
                    for row in data_sum:
                        r = table.row()
                        r.cell(row[0], style="B")
                        r.cell(row[1])
                pdf.ln()

        # 7. CONCLUSÃO FINAL
        pdf.add_page()
        pdf.chapter_title("7. CONCLUSÃO E ENQUADRAMENTO")
        
        val = context.get('valuation')
        if val:
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 8, f"Valor Unitário Médio: {val.get('unit_value', '-')}", ln=True)
            
            # Big Box for Final Value
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_fill_color(220, 255, 220) # Light Green
            pdf.cell(0, 15, f"VALOR DE MERCADO: {val.get('total_value', 'R$ 0,00')}", ln=True, align="C", fill=True, border=1)
            pdf.ln(10)
            
            # Grades
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, "Enquadramento NBR 14.653-2:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 6, f"• {val.get('fundamentation_grade', 'Não calculado')}", ln=True)
            pdf.cell(0, 6, f"• {val.get('precision_grade', 'Não calculado')}", ln=True)
        
        # 8. CLOSING
        pdf.ln(20)
        pdf.multi_cell(0, 5, "Declaramos que não temos interesse direto ou indireto no imóvel avaliado e que este laudo foi elaborado seguindo rigorosamente os preceitos éticos e técnicos da engenharia de avaliações.")
        
        pdf.ln(30)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.cell(0, 5, context['settings'].get('avaliador', 'Engenheiro Responsável'), align="C", ln=True)
        pdf.cell(0, 5, context['settings'].get('titulo_profissional', ''), align="C", ln=True)
        pdf.cell(0, 5, context['settings'].get('crea', ''), align="C", ln=True)

        pdf.output(filename)