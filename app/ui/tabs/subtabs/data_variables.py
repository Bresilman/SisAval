import tkinter as tk
from tkinter import ttk, messagebox

class DataVariables(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var_states = {} 
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # LEFT: Variable List
        frame_list = ttk.LabelFrame(paned, text="Definição do Modelo (X e Y)")
        paned.add(frame_list, weight=2)
        
        cols = ("var", "type", "role", "log")
        self.tree = ttk.Treeview(frame_list, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("var", text="Variável")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("role", text="Papel")
        self.tree.heading("log", text="Log")
        
        self.tree.column("var", width=120)
        self.tree.column("type", width=60)
        self.tree.column("role", width=60)
        self.tree.column("log", width=40)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # RIGHT: Controls
        frame_ctrl = ttk.Frame(paned)
        paned.add(frame_ctrl, weight=1)
        
        lbl = ttk.Label(frame_ctrl, text="Ações Selecionadas", font=("Segoe UI", 10, "bold"))
        lbl.pack(pady=10)
        
        ttk.Button(frame_ctrl, text="🎯 Definir como Dependente (Y)", command=self.set_y).pack(fill="x", padx=10, pady=5)
        ttk.Button(frame_ctrl, text="➕ Adicionar/Remover Independente (X)", command=self.toggle_x).pack(fill="x", padx=10, pady=5)
        ttk.Button(frame_ctrl, text="📈 Aplicar Logaritmo (Ln)", command=self.toggle_log).pack(fill="x", padx=10, pady=5)
        
        ttk.Separator(frame_ctrl, orient="horizontal").pack(fill="x", pady=20)
        
        # RESTORED REGRESSION BUTTON
        self.btn_calc = ttk.Button(frame_ctrl, text="▶ Calcular Regressão", command=self.run_regression, style="Accent.TButton")
        self.btn_calc.pack(fill="x", padx=10, pady=10)

        # Tags
        self.tree.tag_configure('Y', background='#d4edda')
        self.tree.tag_configure('X', background='#cce5ff')

    def refresh_view(self):
        dh = getattr(self.controller, 'data_handler', None)
        if not dh: return
        
        report = dh.get_health_report()
        self.tree.delete(*self.tree.get_children())
        
        for col_info in report.get("columns_info", []):
            name = col_info['name']
            
            # Init state if new
            if name not in self.var_states:
                self.var_states[name] = {'role': None, 'log': False}
            
            s = self.var_states[name]
            role = s['role'] if s['role'] else "-"
            log = "Sim" if s['log'] else ""
            
            self.tree.insert("", "end", iid=name, values=(name, col_info['type'], role, log))
            self._apply_color(name, s['role'])

    def set_y(self):
        sel = self.tree.selection()
        if not sel: return
        name = sel[0]
        
        # Clear old Y
        for k, v in self.var_states.items():
            if v['role'] == 'Y': 
                v['role'] = None
                self._update_row(k)
        
        self.var_states[name]['role'] = 'Y'
        self._update_row(name)

    def toggle_x(self):
        sel = self.tree.selection()
        if not sel: return
        name = sel[0]
        
        curr = self.var_states[name]['role']
        self.var_states[name]['role'] = 'X' if curr != 'X' else None
        self._update_row(name)

    def toggle_log(self):
        sel = self.tree.selection()
        if not sel: return
        name = sel[0]
        self.var_states[name]['log'] = not self.var_states[name]['log']
        self._update_row(name)

    def _update_row(self, name):
        s = self.var_states[name]
        # Get current values to preserve type info
        curr_vals = self.tree.item(name)['values']
        new_vals = (curr_vals[0], curr_vals[1], s['role'] or "-", "Sim" if s['log'] else "")
        self.tree.item(name, values=new_vals)
        self._apply_color(name, s['role'])

    def _apply_color(self, iid, role):
        tag = role if role in ['X', 'Y'] else ''
        self.tree.item(iid, tags=(tag,))

    def get_selection(self):
        y = None
        x = []
        for k, v in self.var_states.items():
            if v['role'] == 'Y': y = k
            elif v['role'] == 'X': x.append(k)
        return y, x

    def run_regression(self):
        # Call controller bridge
        if hasattr(self.controller, 'acao_calcular'):
            self.controller.acao_calcular()
        else:
            messagebox.showerror("Erro", "Controlador não possui 'acao_calcular'.")