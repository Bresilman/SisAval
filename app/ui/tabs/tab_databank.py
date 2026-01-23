import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import os

class DatabankTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_file = "master_databank.csv"
        self._setup_ui()
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not os.path.exists(self.db_file):
            # Create empty DB with standard columns
            df = pd.DataFrame(columns=["Date_Added", "Source", "Address", "Neighborhood", "Area", "Price", "Unit_Price", "Latitude", "Longitude"])
            df.to_csv(self.db_file, index=False)

    def _setup_ui(self):
        # Top Controls
        fr_top = ttk.Frame(self, padding=10)
        fr_top.pack(fill='x')

        ttk.Label(fr_top, text="Banco de Dados Histórico", font=("Arial", 12, "bold")).pack(side='left')
        
        # Actions
        fr_actions = ttk.LabelFrame(fr_top, text="Ações", padding=5)
        fr_actions.pack(side='right')
        
        ttk.Button(fr_actions, text="🔄 Recarregar", command=self.load_data).pack(side='left', padx=5)
        ttk.Button(fr_actions, text="📥 Importar da Aba Dados", command=self.import_from_current).pack(side='left', padx=5)
        ttk.Button(fr_actions, text="📤 Usar Filtrados na Análise", command=self.export_to_current).pack(side='left', padx=5)

        # Filters
        fr_filter = ttk.LabelFrame(self, text="Filtros", padding=10)
        fr_filter.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(fr_filter, text="Bairro:").pack(side='left')
        self.ent_neighborhood = ttk.Entry(fr_filter)
        self.ent_neighborhood.pack(side='left', padx=5)
        
        ttk.Button(fr_filter, text="Filtrar", command=self.filter_data).pack(side='left', padx=10)

        # Table
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.place(relx=1.0, rely=0.3, relheight=0.7, anchor='ne')
        self.tree.configure(yscrollcommand=sb.set)

    def load_data(self):
        try:
            df = pd.read_csv(self.db_file)
            self._update_table(df)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler banco de dados: {e}")

    def _update_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        
        for c in df.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
            
        for i, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def import_from_current(self):
        """Imports data currently in the Data Tab into the master DB."""
        current_df = self.controller.data_handler.get_data()
        if current_df is None or current_df.empty:
            messagebox.showwarning("Aviso", "Nenhum dado na aba 'Dados' para importar.")
            return

        try:
            # Load existing DB
            if os.path.exists(self.db_file):
                master_df = pd.read_csv(self.db_file)
            else:
                master_df = pd.DataFrame()

            # Prepare new data
            # We try to map columns intelligently, or just append everything
            new_data = current_df.copy()
            new_data['Date_Added'] = datetime.now().strftime("%Y-%m-%d")
            
            # Append
            combined_df = pd.concat([master_df, new_data], ignore_index=True)
            
            # Save
            combined_df.to_csv(self.db_file, index=False)
            messagebox.showinfo("Sucesso", f"{len(new_data)} registros adicionados ao Banco de Dados Histórico.")
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar no banco: {e}")

    def filter_data(self):
        neighborhood = self.ent_neighborhood.get().strip()
        if not neighborhood:
            self.load_data()
            return

        try:
            df = pd.read_csv(self.db_file)
            # Filter logic (case insensitive)
            # Assuming there is a column that might contain neighborhood info
            # We search in all string columns for the term
            mask = df.apply(lambda x: x.astype(str).str.contains(neighborhood, case=False).any(), axis=1)
            filtered_df = df[mask]
            self._update_table(filtered_df)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar: {e}")

    def export_to_current(self):
        """Sends the currently visible (filtered) items in the treeview back to the Data Tab."""
        # This effectively allows "loading" from the database
        # We need to reconstruct a DataFrame from the treeview items
        
        columns = self.tree["columns"]
        items = self.tree.get_children()
        
        if not items:
            return

        data = []
        for item in items:
            values = self.tree.item(item)['values']
            data.append(values)
            
        df_export = pd.DataFrame(data, columns=columns)
        
        # Load into Data Handler
        self.controller.data_handler.df = df_export
        # Trigger UI update in Data Tab
        self.controller._atualizar_view_dados()
        
        messagebox.showinfo("Exportar", f"{len(data)} registros carregados para a aba de Análise.")
        self.controller.view.notebook.select(0) # Switch to Data Tab