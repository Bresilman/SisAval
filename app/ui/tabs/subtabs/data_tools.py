import tkinter as tk
from tkinter import ttk, Toplevel, messagebox

class DataToolsSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # 1. Transformations
        fr_trans = ttk.LabelFrame(self, text="🛠️ Transformação Numérica", padding=15)
        fr_trans.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(fr_trans, text="Criar Ln, X², 1/X...").pack(anchor='w')
        ttk.Button(fr_trans, text="Abrir Ferramenta", command=self.abrir_transformador).pack(fill='x', pady=5)

        # 2. Config
        fr_config = ttk.LabelFrame(self, text="⚙️ Configuração Global", padding=15)
        fr_config.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.var_log_global = tk.BooleanVar(value=False)
        ttk.Checkbutton(fr_config, text="Aplicar Ln(x) Globalmente", variable=self.var_log_global).pack(anchor='w')

        # 3. Categorical Encoder (NEW!)
        fr_cat = ttk.LabelFrame(self, text="🔤 Variáveis Qualitativas (Texto)", padding=15)
        fr_cat.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ttk.Label(fr_cat, text="Converta texto em números.\nEx: Alto=3, Médio=2, Baixo=1").pack(anchor='w')
        ttk.Button(fr_cat, text="Mapear Texto -> Número", command=self.abrir_codificador).pack(fill='x', pady=10)

        # 4. Cleaning
        fr_clean = ttk.LabelFrame(self, text="🧹 Saneamento", padding=15)
        fr_clean.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Button(fr_clean, text="Remover Outliers (> 2σ)", command=self.sanear_automatico).pack(fill='x', pady=10)

        # --- Section 5: Inteligência de Mercado (NEW) ---
        fr_intel = ttk.LabelFrame(self, text="🧠 Inteligência de Mercado", padding=15)
        fr_intel.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        ttk.Label(fr_intel, text="Usa o Banco de Dados Histórico para criar variáveis de localização.").pack(anchor='w')
        ttk.Button(fr_intel, text="Criar Variável: Valor Médio do Bairro", command=self.controller.acao_enriquecer_bairros).pack(fill='x', pady=5)

    def abrir_transformador(self):
        t = Toplevel(self); t.title("Transformar"); t.geometry("300x250")
        cols = self.controller.data_handler.get_numeric_columns()
        
        ttk.Label(t, text="Variável:").pack(pady=5)
        c_var = ttk.Combobox(t, values=cols, state="readonly"); c_var.pack()
        
        ttk.Label(t, text="Função:").pack(pady=5)
        c_fun = ttk.Combobox(t, values=["Ln", "Inv", "Quad", "Raiz"], state="readonly"); c_fun.pack()
        
        ttk.Button(t, text="Criar", command=lambda: [self.controller.acao_transformar(c_var.get(), c_fun.get()), t.destroy()]).pack(pady=20)

    def abrir_codificador(self):
        """Opens the Dummy Encoder Tool."""
        cols_text = self.controller.data_handler.get_text_columns()
        
        if not cols_text:
            messagebox.showinfo("Aviso", "Não há colunas de texto carregadas.")
            return

        t = Toplevel(self)
        t.title("Codificador de Variáveis (Dummy)")
        t.geometry("400x500")
        
        # 1. Select Column
        fr_sel = ttk.Frame(t, padding=10); fr_sel.pack(fill='x')
        ttk.Label(fr_sel, text="Selecione a Coluna de Texto:").pack(anchor='w')
        cb_col = ttk.Combobox(fr_sel, values=cols_text, state="readonly")
        cb_col.pack(fill='x')
        
        # Container for values
        fr_vals = ttk.Frame(t, padding=10)
        fr_vals.pack(fill='both', expand=True)
        
        entries = {} # Store entry widgets

        def load_values(event=None):
            # Clear previous
            for w in fr_vals.winfo_children(): w.destroy()
            entries.clear()
            
            col = cb_col.get()
            if not col: return
            
            uniques = self.controller.data_handler.get_unique_values(col)
            
            ttk.Label(fr_vals, text=f"Atribua valores numéricos para '{col}':", font=("Arial", 9, "bold")).pack(pady=5)
            
            for val in uniques:
                row = ttk.Frame(fr_vals)
                row.pack(fill='x', pady=2)
                ttk.Label(row, text=str(val), width=20, anchor='e').pack(side='left')
                ent = ttk.Entry(row, width=10)
                ent.pack(side='left', padx=10)
                entries[val] = ent

        cb_col.bind("<<ComboboxSelected>>", load_values)
        
        def apply():
            mapping = {}
            try:
                for val, ent in entries.items():
                    num = float(ent.get().replace(',', '.'))
                    mapping[val] = num
                
                self.controller.acao_codificar_variavel(cb_col.get(), mapping)
                t.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Preencha todos os campos com números válidos.")

        ttk.Button(t, text="Aplicar Mapeamento", command=apply).pack(pady=10)

    def sanear_automatico(self):
        if messagebox.askyesno("Sanear", "Deseja remover outliers (> 2 desvios)?"):
            self.controller.acao_sanear_dados()