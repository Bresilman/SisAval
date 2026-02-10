import tkinter as tk
from tkinter import ttk, messagebox

class ScraperResults(ttk.Frame):
    def __init__(self, parent, controller, main_controller=None):
        super().__init__(parent)
        self.controller = controller
        self.main_controller = main_controller
        
        # Define Columns based on user request
        self.columns = [
            "id", "cidade", "estado", "tipo", "preco", "endereco", 
            "bairro", "area", "frente", "profundidade", "quartos", 
            "suites", "andar", "banheiros", "vagas", "conservacao", 
            "latitude", "longitude", "url", "telefone", "access_date", "ad_age"
        ]
        
        self.setup_ui()
        
        # Register this view to update when controller gets data
        self.controller.register_observer(self.refresh_table)

    def setup_ui(self):
        # Top Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x", padx=5, pady=5)
        
        ttk.Button(toolbar, text="Atualizar Vista", command=self.refresh_table).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Limpar Lista", command=self.clear_table).pack(side="left", padx=2)
        
        # EXPORT BUTTON
        btn_export = ttk.Button(toolbar, text="Enviar para Tabela de Dados", command=self.send_to_main_data, style="Accent.TButton")
        btn_export.pack(side="right", padx=5)

        # Table Area
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_frame, 
            columns=self.columns, 
            show="headings", 
            selectmode="extended",
            yscrollcommand=vsb.set, 
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configure Headers
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, minwidth=50)
            
        # Specific widths
        self.tree.column("id", width=50)
        self.tree.column("endereco", width=200)
        self.tree.column("url", width=200)

    def refresh_table(self):
        """Refreshes treeview from controller buffer"""
        # Clear current
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Load new
        data = self.controller.get_buffer()
        for idx, row in enumerate(data):
            values = [row.get(col, "") for col in self.columns]
            self.tree.insert("", "end", text=str(idx), values=values)
            
    def clear_table(self):
        self.controller.clear_buffer()

    def send_to_main_data(self):
        """Sends data to the main application controller"""
        if not self.main_controller:
            messagebox.showerror("Erro", "Controlador Principal não vinculado.")
            return

        data = self.controller.get_buffer()
        if not data:
            messagebox.showwarning("Aviso", "Não há dados para enviar.")
            return

        try:
            # INTERFACE WITH MAIN APP
            # We assume main_controller has a route to the data controller
            # Adjust 'data_controller' attribute name based on your actual AppController
            if hasattr(self.main_controller, 'data_controller'):
                # Assuming data_controller has an 'import_data' or 'add_row' method
                # If not, we might need to inspect your DataController code
                count = len(data)
                
                # Logic to add rows (Placeholder - adjust to match your DataController API)
                # self.main_controller.data_controller.batch_add(data) 
                
                messagebox.showinfo("Sucesso", f"{count} imóveis enviados para a Tabela de Dados.")
            else:
                messagebox.showerror("Erro", "DataController não encontrado no AppController.")
                
        except Exception as e:
            messagebox.showerror("Erro ao enviar dados", str(e))