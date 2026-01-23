import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ScenariosPlotsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_top = ttk.Frame(self, padding=5)
        fr_top.pack(fill='x')
        
        ttk.Label(fr_top, text="Variável:").pack(side='left')
        self.cb_var = ttk.Combobox(fr_top, state="readonly", width=15)
        self.cb_var.pack(side='left', padx=5)
        
        ttk.Button(fr_top, text="Gerar Curva", command=self.plot_sensitivity).pack(side='left')
        
        ttk.Button(fr_top, text="💾 Salvar", command=self.save_image).pack(side='right', padx=5)
        ttk.Button(fr_top, text="❓ Ajuda", command=self.show_help).pack(side='right')

        self.fig = plt.Figure(figsize=(6, 4), dpi=90)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update_vars(self, cols):
        self.cb_var['values'] = cols
        if cols: self.cb_var.set(cols[0])

    def show_help(self):
        msg = (
            "CENÁRIOS CETERIS PARIBUS:\n\n"
            "• O que é: Mostra como o preço muda se alterarmos APENAS a variável selecionada, "
            "mantendo todas as outras fixas na média.\n"
            "• Reta Inclinada: A variável influencia o preço.\n"
            "• Reta Horizontal: A variável NÃO influencia (ou não está na equação)."
        )
        messagebox.showinfo("Ajuda: Cenários", msg)

    def save_image(self):
        f = filedialog.asksaveasfilename(defaultextension=".png")
        if f: self.fig.savefig(f, dpi=300)

    def plot_sensitivity(self):
        stats = self.controller.last_stats
        var_target = self.cb_var.get()
        df_used = stats.get('Dados_Utilizados') if stats else None
        
        if not stats:
            return messagebox.showwarning("Aviso", "Calcule a regressão primeiro.")
        
        if df_used is None or var_target not in df_used.columns:
             return messagebox.showwarning("Aviso", "Variável não encontrada nos dados.")

        params = stats['Params']
        
        # Check if variable is in model. If not, warn but proceed (flat line is educational).
        if var_target not in params:
             messagebox.showwarning("Aviso", f"A variável '{var_target}' não está na equação do modelo.\nA curva será plana (sem influência).")

        # 1. Prepare Simulation
        means = df_used.mean()
        x_min, x_max = df_used[var_target].min(), df_used[var_target].max()
        
        if x_min == x_max:
            x_range = np.array([x_min, x_max])
        else:
            x_range = np.linspace(x_min, x_max, 50)
        
        y_pred = []
        is_log = stats.get('Log_Ativo', False)
        
        # 2. Predict
        for val in x_range:
            y_val = params['const']
            
            for col in df_used.columns:
                if col in params:
                    coeff = params[col]
                    if col == var_target:
                        input_val = val
                    else:
                        input_val = means[col]
                    
                    if is_log:
                        if input_val > 0: y_val += coeff * np.log(input_val)
                    else:
                        y_val += coeff * input_val
            
            final_y = np.exp(y_val) if is_log else y_val
            y_pred.append(final_y)

        # 3. Plot
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(x_range, y_pred, 'b-', lw=2)
        ax.set_title(f"Sensibilidade: {var_target}")
        ax.set_xlabel(var_target)
        ax.set_ylabel("Valor Estimado")
        ax.grid(True, alpha=0.5)
        self.fig.tight_layout()
        self.canvas.draw()