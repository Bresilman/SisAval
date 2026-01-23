import tkinter as tk
from tkinter import ttk, Toplevel

class OptimizerConfigSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_main = ttk.Frame(self, padding=10)
        fr_main.pack(fill='both', expand=True)

        # 1. Strategy
        fr_head = ttk.LabelFrame(fr_main, text="1. Estratégia de Busca", padding=10)
        fr_head.pack(fill='x', pady=5)
        
        ttk.Label(fr_head, text="Algoritmo:").pack(side='left')
        self.combo_method = ttk.Combobox(fr_head, values=["Força Bruta", "Stepwise"], state="readonly", width=15)
        self.combo_method.set("Força Bruta")
        self.combo_method.pack(side='left', padx=5)

        ttk.Label(fr_head, text="Modelos:").pack(side='left', padx=(10,0))
        self.chk_linear = tk.BooleanVar(value=True)
        self.chk_log = tk.BooleanVar(value=True)
        ttk.Checkbutton(fr_head, text="Linear", variable=self.chk_linear).pack(side='left')
        ttk.Checkbutton(fr_head, text="Log-Log", variable=self.chk_log).pack(side='left')

        # NEW BUTTON: Smart Analysis
        ttk.Button(fr_head, text="🧠 Analisar Transformações", command=self._analyze_transforms).pack(side='right', padx=5)

        # 2. Variable Signs
        ttk.Label(fr_main, text="2. Variáveis e Coerência", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10,0))
        
        self.tree_vars = ttk.Treeview(fr_main, columns=("Var", "Sinal", "Trava"), show="headings", height=8)
        self.tree_vars.heading("Var", text="Variável"); self.tree_vars.column("Var", width=150)
        self.tree_vars.heading("Sinal", text="Sinal"); self.tree_vars.column("Sinal", width=100, anchor="center")
        self.tree_vars.heading("Trava", text="Fixar?"); self.tree_vars.column("Trava", width=80, anchor="center")
        self.tree_vars.pack(fill='both', expand=True, pady=5)
        
        fr_btns = ttk.Frame(fr_main)
        fr_btns.pack(fill='x')
        ttk.Button(fr_btns, text="🔄 Atualizar Lista", command=self._refresh_vars).pack(side='left', fill='x', expand=True)
        ttk.Button(fr_btns, text="+/- Sinal", command=self._toggle_sign).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(fr_btns, text="🔒 Fixar", command=self._toggle_lock).pack(side='left', fill='x', expand=True)

        # 3. Filters & Run
        fr_run = ttk.Frame(fr_main, padding=10)
        fr_run.pack(fill='x', pady=10)
        
        self.var_filter_p = tk.BooleanVar(value=True)
        ttk.Checkbutton(fr_run, text="P-Valor < 10%", variable=self.var_filter_p).pack(side='left')
        self.var_filter_vif = tk.BooleanVar(value=True)
        ttk.Checkbutton(fr_run, text="VIF < 10", variable=self.var_filter_vif).pack(side='left', padx=10)
        
        ttk.Button(fr_run, text="▶ RODAR OTIMIZADOR", command=self._run_optimizer).pack(side='right', fill='x', expand=True, padx=10)

    def _refresh_vars(self):
        self.tree_vars.delete(*self.tree_vars.get_children())
        cols = self.controller.data_handler.get_numeric_columns()
        try: y = self.controller.view.tab_data.combo_y.get()
        except: y = ""
        for c in cols:
            if c != y: self.tree_vars.insert("", "end", values=(c, "Livre", "Não"))

    def _toggle_sign(self):
        sel = self.tree_vars.selection()
        if not sel: return
        item = self.tree_vars.item(sel[0])
        curr = item['values'][1]
        nxt = "Positivo (+)" if curr == "Livre" else "Negativo (-)" if curr == "Positivo (+)" else "Livre"
        self.tree_vars.item(sel[0], values=(item['values'][0], nxt, item['values'][2]))

    def _toggle_lock(self):
        sel = self.tree_vars.selection()
        if not sel: return
        item = self.tree_vars.item(sel[0])
        curr = item['values'][2]
        nxt = "SIM 🔒" if curr == "Não" else "Não"
        tag = "LOCKED" if nxt == "SIM 🔒" else ""
        self.tree_vars.item(sel[0], values=(item['values'][0], item['values'][1], nxt), tags=(tag,))
        self.tree_vars.tag_configure("LOCKED", background="#e6f3ff", foreground="blue")

    def _run_optimizer(self):
        constraints = {}
        locked = []
        for item in self.tree_vars.get_children():
            v = self.tree_vars.item(item)['values']
            if "Positivo" in v[1]: constraints[v[0]] = 1
            elif "Negativo" in v[1]: constraints[v[0]] = -1
            else: constraints[v[0]] = 0
            if "SIM" in v[2]: locked.append(v[0])

        method_map = {"Força Bruta": "brute", "Stepwise": "stepwise"}
        
        config = {
            'method': method_map.get(self.combo_method.get(), "brute"),
            'models_to_test': [],
            'filter_p': self.var_filter_p.get(),
            'filter_vif': self.var_filter_vif.get(),
            'constraints': constraints,
            'locked': locked
        }
        
        if self.chk_linear.get(): config['models_to_test'].append('linear')
        if self.chk_log.get(): config['models_to_test'].append('log')
        
        if not config['models_to_test']: return
        
        self.controller.acao_otimizar_modelos_avancado(config)
        self.controller.view.tab_optimizer.notebook.select(1)

    def _analyze_transforms(self):
        """Calls controller to analyze best transformations."""
        self.controller.acao_analisar_transformacoes()