import tkinter as tk
from tkinter import ttk, messagebox

class CalculatorTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.inputs = {}
        self.vars_x = []
        self._setup_ui()

    def _setup_ui(self):
        # --- Left Panel: Inputs ---
        pnl_left = ttk.Frame(self, padding=10)
        pnl_left.pack(side='left', fill='both', expand=True)

        ttk.Label(pnl_left, text="1. Características do Imóvel Avaliando", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 10))
        
        # Scrollable Frame
        self.canvas = tk.Canvas(pnl_left, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(pnl_left, orient="vertical", command=self.canvas.yview)
        self.fr_inputs = ttk.Frame(self.canvas)

        self.fr_inputs.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.fr_inputs, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Right Panel: Results ---
        pnl_right = ttk.Frame(self, padding=10, relief="sunken", borderwidth=1)
        pnl_right.pack(side='right', fill='y', padx=5, pady=5)

        ttk.Label(pnl_right, text="2. Resultado da Avaliação", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 10))

        # Main Button
        ttk.Button(pnl_right, text="▶ CALCULAR VALOR UNITÁRIO", command=self.controller.acao_estimar).pack(fill='x', pady=10)

        # Unit Value
        fr_res_unit = ttk.LabelFrame(pnl_right, text="Valor Unitário Estimado (R$/m²)", padding=10)
        fr_res_unit.pack(fill='x', pady=5)
        
        self.lbl_unit = ttk.Label(fr_res_unit, text="R$ 0,00", font=("Arial", 14, "bold"), foreground="blue")
        self.lbl_unit.pack(anchor='center')
        
        self.lbl_interval = ttk.Label(fr_res_unit, text="Campo de Arbítrio (Intervalo): ...", font=("Arial", 9), foreground="gray")
        self.lbl_interval.pack(anchor='center', pady=5)

        # Total Value Calculator
        fr_total = ttk.LabelFrame(pnl_right, text="3. Valor Total do Imóvel", padding=10)
        fr_total.pack(fill='x', pady=20)
        
        ttk.Label(fr_total, text="Área Total do Imóvel (m²):").pack(anchor='w')
        self.ent_area_total = ttk.Entry(fr_total, font=("Arial", 10))
        self.ent_area_total.pack(fill='x', pady=5)
        self.ent_area_total.bind("<KeyRelease>", self._auto_calc_total) # Live calculation
        
        ttk.Button(fr_total, text="Calcular Total", command=self._calc_total).pack(fill='x', pady=2)
        
        self.lbl_total = ttk.Label(fr_total, text="R$ 0,00", font=("Arial", 16, "bold"), foreground="#28a745")
        self.lbl_total.pack(anchor='center', pady=10)

    def build_inputs(self, vars_x, df_data=None):
        """
        Rebuilds inputs with Reference Limits (Min/Max).
        """
        for w in self.fr_inputs.winfo_children(): w.destroy()
        
        self.inputs = {}
        self.vars_x = [v for v in vars_x if v != 'const']
        
        # Headers
        ttk.Label(self.fr_inputs, text="Variável", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(self.fr_inputs, text="Valor do Imóvel", font=("Arial", 9, "bold")).grid(row=0, column=1, sticky='w', padx=5)
        ttk.Label(self.fr_inputs, text="Limites da Amostra (Min - Máx)", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky='w', padx=5)

        for i, var in enumerate(self.vars_x):
            row = i + 1
            # Clean variable name for display (remove prefix Ln_, Inv_, etc)
            display_name = var.replace("Ln_", "").replace("Inv_", "").replace("Quad_", "").replace("Raiz_", "")
            
            ttk.Label(self.fr_inputs, text=f"{display_name}:").grid(row=row, column=0, sticky='e', padx=5, pady=5)
            
            ent = ttk.Entry(self.fr_inputs, width=15)
            ent.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            self.inputs[var] = ent
            
            # Limits
            limit_text = "-"
            if df_data is not None and var in df_data.columns:
                min_v = df_data[var].min()
                max_v = df_data[var].max()
                limit_text = f"[{min_v:,.2f} ... {max_v:,.2f}]"
            
            ttk.Label(self.fr_inputs, text=limit_text, foreground="gray").grid(row=row, column=2, sticky='w', padx=5)

            # Auto-fill Total Area if variable looks like Area
            if "area" in var.lower() or "área" in var.lower():
                ent.bind("<KeyRelease>", lambda event, s=ent: self._sync_area(s))

    def _sync_area(self, source_entry):
        val = source_entry.get()
        self.ent_area_total.delete(0, tk.END)
        self.ent_area_total.insert(0, val)
        self._auto_calc_total()

    def show_result(self, val, min_p, max_p):
        # Format Brazilian currency manually to avoid locale issues
        self.lbl_unit.config(text=f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        min_s = f"R$ {min_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        max_s = f"R$ {max_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        self.lbl_interval.config(text=f"Campo de Arbítrio:\n{min_s} a {max_s}")
        
        self._calc_total() # Trigger total calculation

    def _parse_value(self, val_str):
        """
        Parses string to float handling both 1.200,00 and 1200.00
        """
        if not val_str: return 0.0
        # Remove currency symbol and spaces
        clean = val_str.replace("R$", "").strip()
        
        # Strategy:
        # If it has "," and ".", assume standard logic (comma is decimal if at end)
        # Or simple brute force: remove dots, replace comma with dot
        if "," in clean and "." in clean:
             # Ex: 1.200,50 -> Remove dot, replace comma
             clean = clean.replace(".", "").replace(",", ".")
        elif "," in clean:
             # Ex: 1200,50 -> Replace comma
             clean = clean.replace(",", ".")
        # If only dots, could be 1.200 (1200) or 1.2 (1.2). 
        # Python float handles 1.2 fine. But 1.200 is treated as 1.2.
        # We assume input is standard float OR brazilian format.
        
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def _auto_calc_total(self, event=None):
        self._calc_total()

    def _calc_total(self):
        try:
            # Get Unit Value (already formatted in label)
            txt_unit = self.lbl_unit.cget("text")
            
            # Manual un-formatting of R$ 1.200,50
            # 1. Remove R$
            clean_unit = txt_unit.replace("R$", "").strip()
            # 2. Remove thousands separator (.)
            clean_unit = clean_unit.replace(".", "")
            # 3. Replace decimal comma with dot
            clean_unit = clean_unit.replace(",", ".")
            
            val_unit = float(clean_unit)
            
            # Get Area (Input)
            area_str = self.ent_area_total.get()
            # Same parsing logic for input
            if "," in area_str:
                area_str = area_str.replace(".", "").replace(",", ".")
            
            val_area = float(area_str)
            
            total = val_unit * val_area
            
            # Format Output (Brazilian)
            total_fmt = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.lbl_total.config(text=total_fmt)
            
        except ValueError:
            pass # Silent fail while typing