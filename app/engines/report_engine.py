# app/engines/report_engine.py
import os
import tempfile
import time
import math
import shutil  # <--- NOVA IMPORTAÇÃO CRÍTICA PARA RESOLVER [Errno 18]
import numpy as np

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# Hierarquia de Exceções Customizadas
class PayloadValidationError(Exception): pass
class ReportGenerationError(Exception): pass

class PDFReport(FPDF):
    """Classe auxiliar do FPDF para customizar Cabeçalhos e Rodapés dinâmicos."""
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    def header(self):
        # Cabeçalho: Nome da Empresa
        self.set_font(self.config['estilos']['font_family'], 'B', 10)
        self.set_text_color(*self.config['estilos']['cores']['primaria'])
        self.cell(0, 10, self.config['branding']['empresa_nome'], border=0, ln=1, align='R')
        self.line(self.config['estilos']['margens']['left'], self.get_y(), 
                  210 - self.config['estilos']['margens']['right'], self.get_y())
        self.ln(5)

    def footer(self):
        # Rodapé: Texto Institucional e Paginação
        self.set_y(-15)
        self.set_font(self.config['estilos']['font_family'], 'I', 8)
        self.set_text_color(128, 128, 128)
        self.line(self.config['estilos']['margens']['left'], self.get_y() - 2, 
                  210 - self.config['estilos']['margens']['right'], self.get_y() - 2)
        
        footer_text = self.config['branding']['footer_text']
        self.cell(0, 10, f"{footer_text} | Página {self.page_no()}", align='C')


class ReportEngine:
    """
    Motor Físico Assíncrono para geração de laudos em PDF e Word.
    Implementa validação estrita, proteção Anti-NaN e Escrita Atômica (Safe-Move).
    """
    def __init__(self, payload, config):
        self.payload = payload
        self.config = config
        
        if FPDF is None:
            raise ReportGenerationError("A biblioteca 'fpdf' não está instalada. Execute: pip install fpdf")

    def validate_payload(self):
        """Pre-Flight Check: Schema Validation & Anti-NaN/Inf Protection."""
        if not self.payload:
            raise PayloadValidationError("Payload vazio recebido do Controller.")
            
        imovel = self.payload.get('imovel_avaliando', {})
        val_adotado = imovel.get('valor_adotado', None)
        
        if val_adotado is None:
            raise PayloadValidationError("Falta a chave crítica: 'valor_adotado'.")
            
        if np.isnan(val_adotado) or np.isinf(val_adotado):
            raise PayloadValidationError(f"Valor Matemático Inválido (NaN ou Inf) no valor adotado: {val_adotado}")

    def generate_pdf(self, final_filepath):
        """Gera o arquivo PDF usando Escrita Atômica e Retentativa de File Lock."""
        self.validate_payload()
        
        # 1. Configuração do Documento
        pdf = PDFReport(config=self.config, orientation='P', unit='mm', format='A4')
        margens = self.config['estilos']['margens']
        pdf.set_margins(left=margens['left'], top=margens['top'], right=margens['right'])
        pdf.add_page()
        
        # Estilos base
        font_fam = self.config['estilos']['font_family']
        cor_txt = self.config['estilos']['cores']['texto']
        cor_pri = self.config['estilos']['cores']['primaria']
        
        # 2. Renderização do Conteúdo
        # 2.1 Título
        pdf.set_font(font_fam, 'B', self.config['estilos']['tamanhos']['titulo'])
        pdf.set_text_color(*cor_pri)
        pdf.cell(0, 15, "LAUDO TÉCNICO DE AVALIAÇÃO ESTATÍSTICA", ln=1, align='C')
        pdf.ln(5)
        
        # 2.2 Textos Introdutórios
        pdf.set_font(font_fam, '', self.config['estilos']['tamanhos']['corpo'])
        pdf.set_text_color(*cor_txt)
        pdf.multi_cell(0, 6, self.config['textos']['introducao'])
        pdf.ln(4)
        pdf.multi_cell(0, 6, self.config['textos']['metodologia'])
        pdf.ln(10)
        
        # 2.3 Resultado Final (Destaque)
        pdf.set_font(font_fam, 'B', self.config['estilos']['tamanhos']['subtitulo'])
        pdf.set_text_color(*cor_pri)
        pdf.cell(0, 10, "1. VALOR ESTIMADO DO IMÓVEL", ln=1)
        
        pdf.set_font(font_fam, '', self.config['estilos']['tamanhos']['corpo'])
        pdf.set_text_color(*cor_txt)
        imovel = self.payload.get('imovel_avaliando', {})
        val_adotado = imovel.get('valor_adotado', 0.0)
        pdf.cell(0, 8, f"Valor Final Adotado: R$ {val_adotado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=1)
        pdf.cell(0, 8, f"Intervalo de Confiança (80%): R$ {imovel.get('limite_inferior', 0):,.2f} a R$ {imovel.get('limite_superior', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=1)
        pdf.ln(10)
        
        # 2.4 Qualidade Normativa (Apenas se o Toggle UI permitir)
        opcoes = self.payload.get('opcoes_ui', {})
        if opcoes.get('incluir_auditoria', True):
            pdf.set_font(font_fam, 'B', self.config['estilos']['tamanhos']['subtitulo'])
            pdf.set_text_color(*cor_pri)
            pdf.cell(0, 10, "2. ENQUADRAMENTO NORMATIVO (NBR 14.653-2)", ln=1)
            
            pdf.set_font(font_fam, '', self.config['estilos']['tamanhos']['corpo'])
            pdf.set_text_color(*cor_txt)
            audit = self.payload.get('auditoria_nbr', {})
            pdf.cell(0, 8, f"Grau de Fundamentação: {audit.get('grau_fundamentacao', 'N/D')}", ln=1)
            pdf.cell(0, 8, f"Grau de Precisão: {audit.get('grau_precisao', 'N/D')}", ln=1)
            pdf.ln(5)
        
        # 2.5 Inserção de Gráficos (Degradação Graciosa)
        if opcoes.get('incluir_graficos', True):
            pdf.add_page()
            pdf.set_font(font_fam, 'B', self.config['estilos']['tamanhos']['subtitulo'])
            pdf.set_text_color(*cor_pri)
            pdf.cell(0, 10, "3. DIAGNÓSTICO GRÁFICO", ln=1)
            pdf.ln(5)
            
            graficos = self.payload.get('graficos_paths', {})
            path_ad = graficos.get('path_aderencia', '')
            
            # Verificação de Existência (Evita Crash)
            if path_ad and os.path.exists(path_ad):
                try:
                    pdf.image(path_ad, x=30, w=150)
                except Exception as e:
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(0, 10, f"[Aviso: Imagem de aderência corrompida. Erro: {e}]", ln=1)
            else:
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 10, "[Gráfico de Aderência Indisponível]", border=1, align='C', ln=1)
        
        # 3. Escrita Atômica (Atomic Write) & Retentativas (File Lock)
        # Gera arquivo temporário
        temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(temp_fd) # Libera descritor do SO
        
        try:
            pdf.output(temp_path)
            
            # Retentativa de Escrita (Caso usuário esteja com o PDF final aberto)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # CORREÇÃO: Usar shutil.move para suportar cópia entre partições diferentes
                    shutil.move(temp_path, final_filepath)
                    break # Sucesso!
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        time.sleep(1) # Aguarda 1 segundo e tenta de novo
                    else:
                        raise PermissionError(f"O arquivo '{os.path.basename(final_filepath)}' está aberto em outro programa. Feche-o e tente novamente.")
                except OSError as e:
                    # Fallback de segurança para outros erros de sistema de arquivos
                    raise ReportGenerationError(f"Falha ao mover arquivo gerado para o destino: {e}")
        finally:
            # Limpeza do temporário caso algo dê errado ou sobre após o shutil.move
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except: pass