import customtkinter as ctk

class TabRegression(ctk.CTkFrame):
    # ... (todo o código __init__, setup_panels anteriores iguais) ...
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self._setup_left_panel()
        self._setup_right_panel()

    def _setup_left_panel(self):
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        lbl_title = ctk.CTkLabel(self.left_frame, text="Configuração do Modelo", font=ctk.CTkFont(weight="bold", size=14))
        lbl_title.pack(pady=(10, 15))
        lbl_y = ctk.CTkLabel(self.left_frame, text="Variável Dependente (Y):", anchor="w")
        lbl_y.pack(fill="x", padx=10, pady=(5, 0))
        self.combo_target = ctk.CTkComboBox(self.left_frame, values=["Carregue dados primeiro..."])
        self.combo_target.pack(fill="x", padx=10, pady=(0, 15))
        lbl_x = ctk.CTkLabel(self.left_frame, text="Variáveis Independentes (X):", anchor="w")
        lbl_x.pack(fill="x", padx=10, pady=(5, 0))
        self.scroll_x = ctk.CTkScrollableFrame(self.left_frame, label_text="Selecione as Variáveis")
        self.scroll_x.pack(fill="both", expand=True, padx=10, pady=5)
        self.check_vars = {} 
        self.chk_robust = ctk.CTkCheckBox(self.left_frame, text="Ativar Defesa Robusta (RLM)")
        self.chk_robust.pack(pady=15, padx=10, anchor="w")
        btn_run = ctk.CTkButton(self.left_frame, text="Calcular Regressão", fg_color="green", hover_color="darkgreen", height=40, command=self.controller.acao_calcular_regressao)
        btn_run.pack(pady=20, padx=10, fill="x")

    def _setup_right_panel(self):
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        lbl_res = ctk.CTkLabel(self.right_frame, text="Sumário Estatístico (Output)", font=ctk.CTkFont(weight="bold", size=14))
        lbl_res.pack(pady=(10, 5))
        self.txt_results = ctk.CTkTextbox(self.right_frame, font=ctk.CTkFont(family="Courier New", size=12), wrap="none")
        self.txt_results.pack(fill="both", expand=True, padx=10, pady=10)

    def update_variable_lists(self, columns):
        self.combo_target.configure(values=columns)
        default_y = columns[0]
        for candidate in ["valor_total", "preco", "valor", "price"]:
            if candidate in columns:
                default_y = candidate
                break
        self.combo_target.set(default_y)
        for widget in self.scroll_x.winfo_children():
            widget.destroy()
        self.check_vars = {}
        for col in columns:
            if col != self.combo_target.get(): 
                chk = ctk.CTkCheckBox(self.scroll_x, text=col)
                chk.pack(anchor="w", pady=2)
                chk.select() 
                self.check_vars[col] = chk

    def get_target_variable(self): return self.combo_target.get()
    def get_selected_features(self): return [c for c, chk in self.check_vars.items() if chk.get() == 1]
    def get_use_robust(self): return self.chk_robust.get() == 1
    def display_results(self, summary_text, method_name="OLS"):
        self.txt_results.delete("0.0", "end")
        header = f"=== RESULTADOS DO MODELO: {method_name} ===\n"+"="*60 + "\n\n"
        self.txt_results.insert("0.0", header + summary_text)

    # --- MÉTODO NOVO PARA O SOLVER ---
    def set_variables_programmatically(self, features_list):
        """
        Permite que o Controller (via Solver) marque as caixas automaticamente.
        """
        # 1. Desmarca tudo
        for chk in self.check_vars.values():
            chk.deselect()
            
        # 2. Atualiza a lista caso tenham surgido colunas novas (transformações)
        # O controller já deve ter chamado update_variable_lists antes, mas por segurança:
        existing_keys = set(self.check_vars.keys())
        needed_keys = set(features_list)
        
        # Se houver chaves novas que não estão na UI, recriamos tudo? 
        # Sim, é mais seguro se o Solver criou "ln_Area" e ela ainda não aparece.
        # Mas assumimos que o controller chamou 'update_variable_lists' no passo anterior.
        
        # 3. Marca as solicitadas
        for feat in features_list:
            if feat in self.check_vars:
                self.check_vars[feat].select()
            else:
                # Se não achou, cria on-the-fly (fallback)
                chk = ctk.CTkCheckBox(self.scroll_x, text=feat)
                chk.pack(anchor="w", pady=2)
                chk.select()
                self.check_vars[feat] = chk