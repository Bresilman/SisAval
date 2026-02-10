import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# Try importing tksheet, fallback to None if missing
try:
    from tksheet import Sheet
except ImportError:
    Sheet = None

class DataTable(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.var_states = {} 
        self.excluded_indices = set() 
        self.sheet = None
        
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main Split
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # --- LEFT: Data Table ---
        frame_preview = ttk.LabelFrame(paned, text="Tabela de Dados (Editor)")
        paned.add(frame_preview, weight=4)
        
        if Sheet:
            # TKSHEET IMPLEMENTATION
            self.sheet = Sheet(frame_preview, theme="light green")
            self.sheet.enable_bindings((
                "single_select", "drag_select", "column_drag_and_drop", "row_drag_and_drop",
                "column_select", "row_select", "column_width_resize", "double_click_column_resize",
                "row_width_resize", "column_height_resize", "arrowkeys", "row_height_resize",
                "double_click_row_resize", "right_click_popup_menu", "rc_select", "rc_insert_column",
                "rc_delete_column", "rc_insert_row", "rc_delete_row", "copy", "cut", "paste", "delete",
                "undo", "edit_cell"
            ))
            self.sheet.pack(fill="both", expand=True)
            
            # Context menu binding is handled internally by tksheet usually, 
            # but we can add extra commands via the popup menu if needed.
            self.sheet.extra_bindings("end_edit_cell", self.on_cell_edit)
            
        else:
            # FALLBACK TO TREEVIEW
            self._setup_treeview_fallback(frame_preview)

        # --- RIGHT: Variable Manager ---
        frame_vars = ttk.LabelFrame(paned, text="Variáveis (Colunas)")
        paned.add(frame_vars, weight=1)
        
        cols = ("var", "type", "role", "log")
        self.tree_vars = ttk.Treeview(frame_vars, columns=cols, show="headings", selectmode="browse")
        
        self.tree_vars.heading("var", text="Variável")
        self.tree_vars.heading("type", text="Tipo")
        self.tree_vars.heading("role", text="Função")
        self.tree_vars.heading("log", text="Log")
        
        self.tree_vars.column("var", width=90)
        self.tree_vars.column("type", width=40)
        self.tree_vars.column("role", width=50)
        self.tree_vars.column("log", width=40)
        
        self.tree_vars.pack(fill="both", expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(frame_vars)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Definir Y (Alvo)", command=self.set_y).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Alternar X (Input)", command=self.toggle_x).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Log Sim/Não", command=self.toggle_log).pack(fill="x", pady=2)

    def _setup_treeview_fallback(self, parent):
        lbl = ttk.Label(parent, text="Instale 'tksheet' para edição avançada (pip install tksheet). Usando modo somente leitura.", foreground="red")
        lbl.pack(side="top", fill="x")
        
        vsb = ttk.Scrollbar(parent, orient="vertical")
        hsb = ttk.Scrollbar(parent, orient="horizontal")
        self.tree_data = ttk.Treeview(parent, selectmode="extended", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.tree_data.yview)
        hsb.config(command=self.tree_data.xview)
        
        self.tree_data.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

    def refresh_view(self):
        dh = getattr(self.controller, 'data_handler', None) or getattr(self.controller, 'data_ctrl', None)
        if not dh: return

        df = dh.get_data(include_excluded=True)
        report = dh.get_health_report()

        if df is None or df.empty:
            if self.sheet: self.sheet.set_sheet_data([])
            elif hasattr(self, 'tree_data'): self.tree_data.delete(*self.tree_data.get_children())
            return

        # 1. Update Sheet / Table
        if self.sheet:
            # Tksheet update
            # Convert DF to list of lists, preserving types where possible or converting to str
            data_list = df.values.tolist()
            headers = list(df.columns)
            
            self.sheet.set_sheet_data(data_list)
            self.sheet.headers(headers)
            
            # Highlight excluded rows
            # Tksheet logic for bg color would go here (iterating excluded indices)
            
        elif hasattr(self, 'tree_data'):
            # Treeview update
            self.tree_data.delete(*self.tree_data.get_children())
            display_cols = ["#Index"] + list(df.columns)
            self.tree_data["columns"] = display_cols
            self.tree_data["displaycolumns"] = display_cols
            
            for c in display_cols:
                self.tree_data.heading(c, text=c)
                self.tree_data.column(c, width=90)
                
            for idx, row in df.head(500).iterrows():
                vals = [idx] + list(row)
                self.tree_data.insert("", "end", iid=idx, values=vals)

        # 2. Update Variables
        self.tree_vars.delete(*self.tree_vars.get_children())
        for col_info in report.get("columns_info", []):
            name = col_info['name']
            state = self.var_states.get(name, {"role": None, "log": False})
            self.var_states[name] = state
            
            role_txt = state['role'] if state['role'] else "-"
            log_txt = "Sim" if state['log'] else ""
            
            self.tree_vars.insert("", "end", iid=name, values=(name, col_info['type'], role_txt, log_txt))
            self._color_var_row(name, state['role'])

    def on_cell_edit(self, event):
        """Callback when a cell is edited in tksheet"""
        # event structure: [row, col, "edit_cell", "end_edit_cell", old_value, new_value]
        try:
            row, col = event[0], event[1]
            new_val = event[5]
            
            dh = getattr(self.controller, 'data_handler', None)
            if dh and dh.get_data() is not None:
                # Update DataFrame directly
                # Note: This is a simplistic update. Tksheet might have reordered rows if sorted.
                # Assuming 1:1 mapping for now.
                col_name = self.sheet.headers()[col]
                dh.get_data().iat[row, col] = new_val
                # print(f"Updated {col_name} at row {row} to {new_val}")
        except Exception as e:
            print(f"Error updating data model: {e}")

    # --- Variable Management (Unchanged logic) ---
    def set_y(self):
        sel = self.tree_vars.selection()
        if not sel: return
        name = sel[0]
        for v in self.var_states:
            if self.var_states[v]['role'] == 'Y':
                self.var_states[v]['role'] = None
                self._update_var_row(v)
        self.var_states[name]['role'] = 'Y'
        self._update_var_row(name)

    def toggle_x(self):
        sel = self.tree_vars.selection()
        if not sel: return
        name = sel[0]
        curr = self.var_states[name]['role']
        self.var_states[name]['role'] = 'X' if curr != 'X' else None
        self._update_var_row(name)

    def toggle_log(self):
        sel = self.tree_vars.selection()
        if not sel: return
        name = sel[0]
        self.var_states[name]['log'] = not self.var_states[name]['log']
        self._update_var_row(name)

    def _update_var_row(self, name):
        state = self.var_states[name]
        curr = self.tree_vars.item(name)['values']
        new_vals = (curr[0], curr[1], state['role'] or "-", "Sim" if state['log'] else "")
        self.tree_vars.item(name, values=new_vals)
        self._color_var_row(name, state['role'])

    def _color_var_row(self, iid, role):
        tags = ('y_row',) if role == 'Y' else ('x_row',) if role == 'X' else ()
        self.tree_vars.item(iid, tags=tags)
        self.tree_vars.tag_configure('y_row', background='#d4edda')
        self.tree_vars.tag_configure('x_row', background='#cce5ff')

    def get_selection(self):
        y = None
        x = []
        for name, s in self.var_states.items():
            if s['role'] == 'Y': y = name
            elif s['role'] == 'X': x.append(name)
        return y, x