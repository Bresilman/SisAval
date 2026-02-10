import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class DataTools(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        # Frame Layout (Do not pack self)
        
        # Left: File Ops
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="📂 Abrir CSV/Excel", command=self.load_file).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="💾 Salvar Como", command=self.export_file).pack(side="left", padx=2)
        
        # Right: Status
        self.lbl_status = ttk.Label(self, text="Nenhum dado carregado", font=("Segoe UI", 9, "italic"))
        self.lbl_status.pack(side="right", padx=10)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Dados", "*.csv *.xlsx *.xls")])
        if not path: return
        
        dh = self._get_handler()
        if not dh: return

        success, msg = dh.load_file(path)
        if success:
            self.update_status()
            # Refresh Parent Tab (TabData)
            if hasattr(self.master, 'master') and hasattr(self.master.master, 'refresh_ui'):
                self.master.master.refresh_ui() 
            elif hasattr(self.controller, 'view') and hasattr(self.controller.view, 'tab_data'):
                self.controller.view.tab_data.refresh_ui()
        else:
            messagebox.showerror("Erro", msg)

    def export_file(self):
        dh = self._get_handler()
        if not dh or dh.get_data() is None: return
        
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")])
        if path:
            try:
                df = dh.get_data()
                if path.endswith('.csv'): df.to_csv(path, index=False)
                else: df.to_excel(path, index=False)
                messagebox.showinfo("Sucesso", "Dados exportados.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def update_status(self):
        dh = self._get_handler()
        if not dh: return
        
        rep = dh.get_health_report()
        if not rep: return
        
        txt = f"Total: {rep['total_rows']} | Ativos: {rep['clean_rows']} | Nulos: {rep['rows_with_nan']}"
        self.lbl_status.config(text=txt, foreground="blue")

    def _get_handler(self):
        return getattr(self.controller, 'data_handler', getattr(self.controller, 'data_ctrl', None))