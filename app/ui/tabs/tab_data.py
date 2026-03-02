import customtkinter as ctk
import pandas as pd

class TabData(ctk.CTkFrame):
    """
    Aba Avançada para Inspeção, Transformação e Criação de Índices.
    Segue o manual SYSTEM_TRANSFORMATIONS_MANUAL.md.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_columns = []
        
        # Layout Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sub-abas
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        self.tab_view.add("Visualização (Grid)")
        self.tab_view.add("Estatística Descritiva")
        self.tab_view.add("Estrutura & Nulos")
        self.tab_view.add("Transformações & Índices") 
        
        self._setup_grid_tab()
        self._setup_describe_tab()
        self._setup_structure_tab()
        self._setup_transform_tab()
        
    def _setup_grid_tab(self):
        self.txt_data = ctk.CTkTextbox(self.tab_view.tab("Visualização (Grid)"), 
                                     wrap="none", 
                                     font=ctk.CTkFont(family="Courier New", size=11))
        self.txt_data.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_data.insert("0.0", "Carregue um arquivo CSV/Excel para visualizar.")

    def _setup_describe_tab(self):
        self.txt_desc = ctk.CTkTextbox(self.tab_view.tab("Estatística Descritiva"), 
                                     wrap="none",
                                     font=ctk.CTkFont(family="Courier New", size=11))
        self.txt_desc.pack(fill="both", expand=True, padx=5, pady=5)

    def _setup_structure_tab(self):
        self.txt_info = ctk.CTkTextbox(self.tab_view.tab("Estrutura & Nulos"), 
                                     font=ctk.CTkFont(family="Courier New", size=11))
        self.txt_info.pack(fill="both", expand=True, padx=5, pady=5)

    def _setup_transform_tab(self):
        # Frame dividido em três: Simples (Esq), Composta (Meio), Fórmulas (Dir/Baixo)
        frame = self.tab_view.tab("Transformações & Índices")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        # Se quisermos adicionar um painel inferior, usamos grid rows
        frame.grid_rowconfigure(0, weight=1) 
        frame.grid_rowconfigure(1, weight=0) # Painel de Fórmulas
        
        # --- PAINEL 1: Transformação Simples (Univariada) ---
        p1 = ctk.CTkFrame(frame)
        p1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(p1, text="1. Transformação Individual", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        ctk.CTkLabel(p1, text="Selecione uma coluna para transformar:", text_color="gray").pack(pady=(0,5))
        
        self.combo_vars = ctk.CTkComboBox(p1, values=["Carregue dados..."], width=250)
        self.combo_vars.pack(pady=5)
        
        # Botões de Ação
        btn_grid = ctk.CTkFrame(p1, fg_color="transparent")
        btn_grid.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkButton(btn_grid, text="Log Natural (ln)", command=lambda: self._request_transform('log')).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_grid, text="Ao Quadrado (x²)", command=lambda: self._request_transform('quad')).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_grid, text="Raiz Quadrada (√x)", command=lambda: self._request_transform('sqrt')).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_grid, text="Inverso (1/x)", command=lambda: self._request_transform('inv')).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkFrame(p1, height=2, fg_color="gray").pack(fill="x", padx=20, pady=15)
        ctk.CTkButton(p1, text="🗑️ Remover Coluna Selecionada", fg_color="#C62828", hover_color="#8E0000",
                      command=lambda: self._request_transform('drop')).pack(pady=5, padx=20, fill="x")

        # --- PAINEL 2: Variáveis Compostas (Multivariada) ---
        p2 = ctk.CTkFrame(frame)
        p2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(p2, text="2. Criar Índice (Multivariado)", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10)
        
        ctk.CTkLabel(p2, text="Nome do Novo Índice:", anchor="w").pack(fill="x", padx=20)
        self.entry_idx_name = ctk.CTkEntry(p2, placeholder_text="Ex: Indice_Comercio")
        self.entry_idx_name.pack(pady=(0,10), padx=20, fill="x")
        
        ctk.CTkLabel(p2, text="Método de Agregação:", anchor="w").pack(fill="x", padx=20)
        self.combo_method = ctk.CTkComboBox(p2, values=[
            "Índice de Comodidade (Soma dos Logs)", 
            "Média Simples", 
            "Soma Simples"
        ])
        self.combo_method.set("Índice de Comodidade (Soma dos Logs)")
        self.combo_method.pack(pady=(0,10), padx=20, fill="x")
        
        ctk.CTkLabel(p2, text="Selecione as variáveis (Checkboxes):", text_color="gray").pack(pady=(10, 0))
        self.scroll_vars = ctk.CTkScrollableFrame(p2, height=150) # Altura reduzida para caber fórmula embaixo se necessário
        self.scroll_vars.pack(fill="both", expand=True, padx=10, pady=5)
        self.check_vars_idx = {} 
        
        ctk.CTkButton(p2, text="➕ Criar Índice", fg_color="#1565C0", hover_color="#0D47A1",
                      command=self._request_create_index).pack(pady=10, padx=20, fill="x")

        # --- PAINEL 3: FÓRMULAS PERSONALIZADAS (NOVO) ---
        # Ocupa a parte inferior inteira
        p3 = ctk.CTkFrame(frame)
        p3.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(p3, text="3. Fórmula Personalizada (Avançado)", font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=10, pady=5)
        
        f3_grid = ctk.CTkFrame(p3, fg_color="transparent")
        f3_grid.pack(fill="x", padx=10, pady=5)
        
        # Input Nome
        ctk.CTkLabel(f3_grid, text="Nome da Variável:").pack(side="left", padx=5)
        self.entry_formula_name = ctk.CTkEntry(f3_grid, width=150, placeholder_text="Ex: preco_m2")
        self.entry_formula_name.pack(side="left", padx=5)
        
        # Input Fórmula
        ctk.CTkLabel(f3_grid, text="=").pack(side="left")
        self.entry_formula = ctk.CTkEntry(f3_grid, width=300, placeholder_text="Ex: preco / area_total")
        self.entry_formula.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botão Executar
        ctk.CTkButton(f3_grid, text="Calcula", width=80, fg_color="#E65100", hover_color="#EF6C00",
                    command=self._request_formula).pack(side="left", padx=5)
        
        lbl_hint = ctk.CTkLabel(p3, text="Dica: Use nomes exatos das colunas. Operações suportadas: +, -, *, /, ** (potência), np.log(), np.sqrt()", 
                              text_color="gray", font=ctk.CTkFont(size=10))
        lbl_hint.pack(anchor="w", padx=15, pady=(0,5))

    def _request_transform(self, method):
        col = self.combo_vars.get()
        if not col or col == "Carregue dados...": return
        self.controller.acao_transformar_coluna(col, method)

    def _request_create_index(self):
        new_name = self.entry_idx_name.get()
        method_desc = self.combo_method.get()
        if not new_name:
            print("Erro: Digite um nome para o índice.") 
            return
        if "Log" in method_desc: method_code = 'sum_ln'
        elif "Média" in method_desc: method_code = 'mean'
        else: method_code = 'sum'
        
        selected_cols = [col for col, chk in self.check_vars_idx.items() if chk.get() == 1]
        if not selected_cols:
            print("Erro: Selecione pelo menos uma coluna.")
            return
        self.controller.acao_criar_indice(new_name, method_code, selected_cols)

    def _request_formula(self):
        """Coleta a fórmula e envia para o controller."""
        name = self.entry_formula_name.get()
        formula = self.entry_formula.get()
        
        if not name or not formula:
            print("Erro: Preencha nome e fórmula.") # Ideal usar messagebox no futuro
            return
            
        # Envia para o controller
        # Nota: Precisaremos adicionar acao_calcular_formula no controller
        if hasattr(self.controller, 'acao_calcular_formula'):
            self.controller.acao_calcular_formula(name, formula)
        else:
            print("Erro: Controller não suporta fórmulas ainda.")

    def update_table(self, df: pd.DataFrame):
        """Refresca todas as abas com os dados novos."""
        self.txt_data.delete("0.0", "end")
        self.txt_desc.delete("0.0", "end")
        self.txt_info.delete("0.0", "end")
        
        if df is None or df.empty:
            self.txt_data.insert("0.0", "Nenhum dado carregado.")
            return

        self.current_columns = list(df.columns)
        
        # --- ATUALIZA INPUTS ---
        current_sel = self.combo_vars.get()
        self.combo_vars.configure(values=self.current_columns)
        if current_sel in self.current_columns:
            self.combo_vars.set(current_sel)
        elif self.current_columns:
            self.combo_vars.set(self.current_columns[0])
            
        for w in self.scroll_vars.winfo_children(): w.destroy()
        self.check_vars_idx = {}
        for col in self.current_columns:
            chk = ctk.CTkCheckBox(self.scroll_vars, text=col)
            chk.pack(anchor="w", pady=2)
            self.check_vars_idx[col] = chk

        # --- ATUALIZA VISUALIZAÇÕES DE TEXTO ---
        info_header = f"Amostras: {df.shape[0]} | Variáveis: {df.shape[1]}\n" + "="*60 + "\n"
        self.txt_data.insert("0.0", info_header + df.head(100).to_string())

        try:
            df_num = df.select_dtypes(include=['number'])
            if not df_num.empty:
                desc = df_num.describe().T
                pd.options.display.float_format = '{:.2f}'.format
                self.txt_desc.insert("0.0", desc.to_string())
            else:
                self.txt_desc.insert("0.0", "Nenhuma coluna numérica encontrada.")
        except Exception as e:
            self.txt_desc.insert("0.0", f"Erro ao gerar estatísticas: {e}")

        buffer = [f"{'Coluna':<25} | {'Tipo':<10} | {'Nulos':<8} | {'% Nulos':<8} | {'Exemplo':<15}"]
        buffer.append("-" * 90)
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulls = df[col].isnull().sum()
            perc = (nulls / len(df)) * 100
            ex = str(df[col].iloc[0])[:15] if len(df) > 0 else ""
            buffer.append(f"{col:<25} | {dtype:<10} | {nulls:<8} | {perc:.1f}%   | {ex:<15}")
            
        self.txt_info.insert("0.0", "\n".join(buffer))