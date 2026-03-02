import customtkinter as ctk
import tkinter as tk

class OptConfig(ctk.CTkFrame):
    """
    Sub-aba de Configuração do Solver.
    Utiliza IntVars para garantir que o estado dos Checkboxes seja capturado corretamente.
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Variáveis de Controle (Garante sincronia com a UI)
        self.var_log = tk.IntVar(value=1)
        self.var_sq = tk.IntVar(value=0)
        self.var_inv = tk.IntVar(value=0)
        
        # Grid Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) 
        
        # --- SEÇÃO 1: Método e Alvo ---
        f1 = ctk.CTkFrame(self)
        f1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(f1, text="1. Estratégia & Alvo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.combo_method = ctk.CTkComboBox(f1, values=["Algoritmo Genético", "Stepwise (Backward)", "Força Bruta"])
        self.combo_method.pack(fill="x", padx=10, pady=5)
        self.combo_target = ctk.CTkComboBox(f1, values=["Carregue dados..."], command=self._on_target_change)
        self.combo_target.pack(fill="x", padx=10, pady=5)

        # --- SEÇÃO 2: Parâmetros ---
        f2 = ctk.CTkFrame(self)
        f2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(f2, text="2. Parâmetros & Limites", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        f2_grid = ctk.CTkFrame(f2, fg_color="transparent")
        f2_grid.pack(fill="x", padx=5)
        self._add_entry(f2_grid, 0, "População:", "30", "entry_pop")
        self._add_entry(f2_grid, 1, "Gerações:", "15", "entry_gen")
        self._add_entry(f2_grid, 2, "Max VIF:", "10.0", "entry_vif")
        self._add_entry(f2_grid, 3, "Max P-Valor:", "0.10", "entry_pval")
        self._add_entry(f2_grid, 4, "Max Cond.No:", "1000", "entry_cond") 
        self._add_entry(f2_grid, 5, "Min P-Norm:", "0.05", "entry_norm")

        # --- SEÇÃO 3: Variáveis (X) ---
        f3 = ctk.CTkFrame(self)
        f3.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        header = ctk.CTkFrame(f3, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="3. Variáveis Candidatas (X)", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Todas", width=50, height=20, command=lambda: self._toggle_all(True)).pack(side="right", padx=2)
        ctk.CTkButton(header, text="Nenhuma", width=50, height=20, command=lambda: self._toggle_all(False)).pack(side="right", padx=2)
        self.scroll_vars = ctk.CTkScrollableFrame(f3)
        self.scroll_vars.pack(fill="both", expand=True, padx=5, pady=5)
        self.check_vars = {} 
        self.all_columns = []

        # --- SEÇÃO 4: Transformações ---
        f4 = ctk.CTkFrame(self)
        f4.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(f4, text="4. Transformações Permitidas", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        t_frame = ctk.CTkFrame(f4, fg_color="transparent")
        t_frame.pack(fill="x", padx=10)
        
        # Vinculando às IntVars para garantir captura de estado
        self.chk_log = ctk.CTkCheckBox(t_frame, text="Logaritmo (ln)", variable=self.var_log)
        self.chk_log.pack(side="left", padx=10, pady=5)
        self.chk_sq = ctk.CTkCheckBox(t_frame, text="Quadrado (x²)", variable=self.var_sq)
        self.chk_sq.pack(side="left", padx=10, pady=5)
        self.chk_inv = ctk.CTkCheckBox(t_frame, text="Inverso (1/x)", variable=self.var_inv)
        self.chk_inv.pack(side="left", padx=10, pady=5)

        # Botão de Ação
        self.btn_run = ctk.CTkButton(self, text="🚀 Executar Otimizador", fg_color="#5A189A", height=40)
        self.btn_run.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=15)

    def _add_entry(self, parent, row, label, default, attr_name):
        ctk.CTkLabel(parent, text=label, anchor="w").grid(row=row, column=0, padx=5, pady=2, sticky="w")
        e = ctk.CTkEntry(parent, width=60); e.grid(row=row, column=1, padx=5, pady=2)
        e.insert(0, default); setattr(self, attr_name, e)

    def update_candidates_list(self, columns):
        self.all_columns = columns
        self.combo_target.configure(values=columns)
        for w in self.scroll_vars.winfo_children(): w.destroy()
        self.check_vars = {}
        target = self.combo_target.get()
        for col in columns:
            if col == target: continue 
            chk = ctk.CTkCheckBox(self.scroll_vars, text=col); chk.pack(anchor="w", pady=2); chk.select() 
            self.check_vars[col] = chk

    def _on_target_change(self, choice):
        if self.all_columns: self.update_candidates_list(self.all_columns)

    def _toggle_all(self, state):
        for chk in self.check_vars.values(): chk.select() if state else chk.deselect()

    def get_settings(self):
        method_map = {"Algoritmo Genético": "genetic", "Stepwise (Backward)": "stepwise", "Força Bruta": "brute"}
        
        # Coleta usando as Variáveis de Controle
        transforms = ['linear']
        if self.var_log.get() == 1: transforms.append('log')
        if self.var_sq.get() == 1: transforms.append('square')
        if self.var_inv.get() == 1: transforms.append('inverse')
        
        return {
            'method': method_map.get(self.combo_method.get().split(" (")[0], 'genetic'),
            'target': self.combo_target.get(),
            'candidates': [col for col, chk in self.check_vars.items() if chk.get() == 1],
            'pop_size': int(self.entry_pop.get()),
            'generations': int(self.entry_gen.get()),
            'max_vif': float(self.entry_vif.get()),
            'max_p': float(self.entry_pval.get()),
            'max_cond_no': float(self.entry_cond.get()),
            'min_normality_p': float(self.entry_norm.get()),
            'allowed_transforms': transforms
        }