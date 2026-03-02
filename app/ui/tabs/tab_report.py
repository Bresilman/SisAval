# app/ui/tabs/tab_report.py
import customtkinter as ctk
import os
import threading
from tkinter import filedialog, messagebox

class TabReport(ctk.CTkFrame):
    """
    Aba de Configuração, Visualização e Exportação de Laudos.
    Implementa "Pre-Flight Checks" e Toggles de Seções.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        self._setup_options_panel()
        self._setup_preview_panel()

    def _setup_options_panel(self):
        """Painel lateral esquerdo com opções de customização e botões."""
        opts_frame = ctk.CTkFrame(self)
        opts_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(opts_frame, text="Configuração do Laudo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        # Toggles (Checkboxes de Inclusão)
        self.var_graficos = ctk.IntVar(value=1)
        self.var_auditoria = ctk.IntVar(value=1)
        self.var_estatistica = ctk.IntVar(value=1)
        
        ctk.CTkCheckBox(opts_frame, text="Incluir Gráficos de Diagnóstico", variable=self.var_graficos, command=self._refresh_preview).pack(anchor="w", padx=20, pady=5)
        ctk.CTkCheckBox(opts_frame, text="Incluir Selos NBR (Graus I, II, III)", variable=self.var_auditoria, command=self._refresh_preview).pack(anchor="w", padx=20, pady=5)
        ctk.CTkCheckBox(opts_frame, text="Incluir Tabelas Estatísticas", variable=self.var_estatistica, command=self._refresh_preview).pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(opts_frame, text="Anotações Complementares do Avaliador:").pack(anchor="w", padx=20, pady=(15, 5))
        self.txt_anotacoes = ctk.CTkTextbox(opts_frame, height=100)
        self.txt_anotacoes.pack(fill="x", padx=20)
        
        # Botões de Ação
        ctk.CTkButton(opts_frame, text="🔄 Atualizar Preview", fg_color="gray", command=self._refresh_preview).pack(pady=(20, 10), padx=20, fill="x")
        
        self.btn_export_pdf = ctk.CTkButton(opts_frame, text="📄 Exportar Laudo (PDF)", fg_color="#b30000", hover_color="#800000", height=40, command=self._on_export_pdf)
        self.btn_export_pdf.pack(pady=10, padx=20, fill="x")

        # Status
        self.lbl_status = ctk.CTkLabel(opts_frame, text="", text_color="green")
        self.lbl_status.pack(pady=10)

    def _setup_preview_panel(self):
        """Painel direito simulando o documento final (Live Highlight)."""
        prev_frame = ctk.CTkFrame(self)
        prev_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(prev_frame, text="Preview Dinâmico", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.txt_preview = ctk.CTkTextbox(prev_frame, font=ctk.CTkFont(family="Courier New", size=12), wrap="word")
        self.txt_preview.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_preview.insert("0.0", "Clique em 'Atualizar Preview' após concluir os cálculos na Calculadora.")

    def _get_ui_options(self):
        return {
            "incluir_graficos": self.var_graficos.get() == 1,
            "incluir_auditoria": self.var_auditoria.get() == 1,
            "incluir_estatistica": self.var_estatistica.get() == 1,
            "anotacoes": self.txt_anotacoes.get("0.0", "end").strip()
        }

    def _refresh_preview(self):
        """Solicita ao Controller um mock text para visualização antes de gerar o PDF."""
        # Se você tiver implementado um método get_preview_text() no Controller, chame-o aqui.
        # Caso contrário, mostra um texto formatado provisório.
        
        self.txt_preview.delete("0.0", "end")
        
        # Pre-Flight Check Simples Visual
        if not hasattr(self.controller, 'auditor') or not self.controller.auditor:
            self.txt_preview.insert("0.0", "⚠️ ALERTA: Nenhum modelo auditado. Volte à aba 'Regressão' e calcule um modelo.")
            return
            
        opts = self._get_ui_options()
        
        preview = "=== PREVIEW DO LAUDO ===\n\n"
        preview += "OBJETIVO: Avaliação de Imóvel Urbano (Inferência Estatística)\n\n"
        
        if opts['incluir_auditoria']:
            preview += "[SEÇÃO: ENQUADRAMENTO NBR 14.653-2]\n"
            preview += "-> Grau de Fundamentação: (Gerado pelo Auditor)\n"
            preview += "-> Grau de Precisão: (Gerado pela Calculadora)\n\n"
            
        if opts['incluir_graficos']:
            preview += "[SEÇÃO: GRÁFICOS DIAGNÓSTICOS]\n"
            preview += "-> (Imagens serão plotadas e inseridas no PDF final)\n\n"
            
        if opts['anotacoes']:
            preview += "[ANOTAÇÕES COMPLEMENTARES]\n"
            preview += f"{opts['anotacoes']}\n\n"
            
        preview += "Tudo pronto. Clique em 'Exportar Laudo (PDF)' para materializar o documento."
        self.txt_preview.insert("0.0", preview)

    def _on_export_pdf(self):
        """Pre-Flight Check e Roteamento para Exportação Assíncrona."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            title="Salvar Laudo Estatístico"
        )
        if not filepath: return
        
        # Bloqueia botão para evitar duplos cliques
        self.btn_export_pdf.configure(state="disabled", text="Gerando...")
        self.lbl_status.configure(text="Iniciando motor PDF...", text_color="blue")
        
        opcoes = self._get_ui_options()
        
        # Envia a ordem ao Controller para gerar (Deve ser implementado no AnalyzerController)
        # self.controller.acao_gerar_laudo(filepath, formato='pdf', opcoes_ui=opcoes)
        
        def run_export():
            try:
                # Simulando a chamada do Controller (Substitua por self.controller.acao_gerar_laudo)
                if hasattr(self.controller, 'acao_gerar_laudo'):
                    self.controller.acao_gerar_laudo(filepath, formato='pdf', opcoes_ui=opcoes)
                    msg = "Sucesso!"
                    color = "green"
                else:
                    msg = "Erro: Método acao_gerar_laudo() não implementado no Controller."
                    color = "red"
            except Exception as e:
                msg = f"Falha na Geração: {str(e)}"
                color = "red"
                
            if self.winfo_exists():
                self.after(0, lambda: self._finalize_export(msg, color, filepath))
                
        # Threading conforme Manual v2.0
        threading.Thread(target=run_export, daemon=True).start()

    def _finalize_export(self, msg, color, filepath):
        """Callback após término da Thread de exportação."""
        self.btn_export_pdf.configure(state="normal", text="📄 Exportar Laudo (PDF)")
        self.lbl_status.configure(text=msg, text_color=color)
        
        if color == "green":
            resposta = messagebox.askyesno("Sucesso", "Laudo gerado com sucesso! Deseja abrir o arquivo agora?")
            if resposta:
                try:
                    os.startfile(filepath) # Exclusivo Windows
                except:
                    pass
        else:
            messagebox.showerror("Erro de Exportação", msg)