import tkinter as tk
from tkinter import ttk
from app.config import settings

class ValidationChecklistSubTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # Layout Split
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill='both', expand=True)

        # 1. Table
        fr_table = ttk.Frame(paned)
        paned.add(fr_table, weight=3)

        cols = ("item", "valor", "limite", "status", "msg")
        self.tree = ttk.Treeview(fr_table, columns=cols, show="headings")
        
        headers = ["Critério", "Valor", "Meta", "Status", "Diagnóstico"]
        widths = [180, 80, 80, 80, 250]
        
        for c, h, w in zip(cols, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center" if c != "item" else "w")

        self.tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree.tag_configure("OK", background=settings.COLOR_OK)
        self.tree.tag_configure("ALERTA", background=settings.COLOR_ALERTA)
        self.tree.tag_configure("ERRO", background=settings.COLOR_ERRO)

        # 2. Educational Panel
        fr_help = ttk.LabelFrame(paned, text="📖 Entendendo os Testes", padding=10)
        paned.add(fr_help, weight=2)

        self.txt_help = tk.Text(fr_help, wrap="word", font=("Arial", 9), bg="#f4f4f4", relief="flat")
        self.txt_help.pack(fill='both', expand=True)
        
        # Static explanation content
        explanation = (
            "1. DETERMINAÇÃO (R²): Indica o quanto o seu modelo 'explica' a realidade. "
            "Se R²=0.80, significa que 80% do preço vem das variáveis (área, vagas), e 20% é subjetivo.\n\n"
            
            "2. TESTE F (Significância): Prova que o modelo não foi sorte. "
            "Se estiver vermelho, seus dados não têm lógica nenhuma.\n\n"
            
            "3. NORMALIDADE (Shapiro): Os erros (resíduos) devem se distribuir como uma curva de sino. "
            "Se falhar, seu Intervalo de Confiança pode estar errado. Tente aplicar Ln(x) ou remover outliers.\n\n"
            
            "4. HOMOCEDASTICIDADE (Breusch-Pagan): O modelo deve ser justo. Ele não pode errar pouco nos imóveis "
            "baratos e errar muito nos caros. Se falhar, o modelo é instável.\n\n"
            
            "5. MULTICOLINEARIDADE (VIF): Variáveis repetidas. Ex: Usar 'Área Total' e 'Área Construída' se elas "
            "são quase iguais. Isso confunde o cálculo. Remova uma delas."
        )
        self.txt_help.insert("end", explanation)
        self.txt_help.configure(state="disabled")

    def update_data(self, report):
        self.tree.delete(*self.tree.get_children())
        for r in report:
            self.tree.insert("", "end", values=(
                r['item'], r['valor'], r['limite'], r['status'], r['msg']
            ), tags=(r['status'],))