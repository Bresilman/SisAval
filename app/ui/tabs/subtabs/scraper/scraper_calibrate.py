import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os

class ScraperCalibrate(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Columns for the calibration table
        self.columns = ["field", "value", "selector", "status"]
        # Default fields to check - ensuring we cover all required data points
        self.target_fields = [
            "titulo", "preco", "area", "quartos", "banheiros", "suites", "vagas",
            "endereco", "bairro", "cidade", "estado", "tipo", "condominio", "iptu"
        ]
        self.current_profile = {}
        self.setup_ui()

    def setup_ui(self):
        # Layout weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- Top Control Panel ---
        control_frame = ttk.LabelFrame(self, text="Painel de Treinamento e Calibração")
        control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        control_frame.columnconfigure(1, weight=1)

        # Scraper Selector
        ttk.Label(control_frame, text="Perfil (Portal):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_portal = ttk.Combobox(control_frame, values=["Zap Imóveis", "VivaReal", "OLX", "Imovelweb", "Custom"])
        self.combo_portal.current(0)
        self.combo_portal.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_portal.bind("<<ComboboxSelected>>", self.load_profile_selectors)

        # Test URL
        ttk.Label(control_frame, text="URL Alvo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_test_url = ttk.Entry(control_frame)
        self.ent_test_url.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.ent_test_url.insert(0, "https://www.zapimoveis.com.br/imovel/...")

        # Buttons Row 1: Testing
        btn_frame_test = ttk.Frame(control_frame)
        btn_frame_test.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.btn_test_url = ttk.Button(btn_frame_test, text="1. Testar via URL (Online)", command=self.run_test_url)
        self.btn_test_url.pack(side="left", padx=5)
        
        self.btn_test_file = ttk.Button(btn_frame_test, text="1. Testar via Arquivo HTML (Offline)", command=self.run_test_file)
        self.btn_test_file.pack(side="left", padx=5)

        # Buttons Row 2: Training
        btn_frame_train = ttk.Frame(control_frame)
        btn_frame_train.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        self.btn_train = ttk.Button(btn_frame_train, text="2. Corrigir / Definir Seletor Manual", command=self.train_field)
        self.btn_train.pack(side="left", padx=5)
        
        self.btn_save = ttk.Button(btn_frame_train, text="3. Salvar Perfil de Seletores", command=self.save_selectors)
        self.btn_save.pack(side="left", padx=5)

        # --- Results Table (Treeview) ---
        table_frame = ttk.LabelFrame(self, text="Campos Extraídos (Duplo clique para editar seletor)")
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        self.tree = ttk.Treeview(
            table_frame, 
            columns=self.columns, 
            show="headings", 
            selectmode="browse"
        )
        
        # Headers
        self.tree.heading("field", text="Campo")
        self.tree.heading("value", text="Valor Encontrado")
        self.tree.heading("selector", text="Seletor (CSS/XPath)")
        self.tree.heading("status", text="Status")
        
        # Column Config
        self.tree.column("field", width=120)
        self.tree.column("value", width=200)
        self.tree.column("selector", width=350)
        self.tree.column("status", width=80)

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Bind double click to train
        self.tree.bind("<Double-1>", self.on_double_click)

    def run_test_url(self):
        """Simulate running the scraper on the single URL"""
        url = self.ent_test_url.get()
        if not url: return
        self.populate_table_mock(source="URL: " + url)

    def run_test_file(self):
        """Load a local HTML file to test selectors against"""
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo HTML salvo",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
        )
        if filepath:
            self.populate_table_mock(source="File: " + os.path.basename(filepath))

    def populate_table_mock(self, source=""):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # In a real scenario, this calls self.controller.test_scraper(url/file)
        # We fill with ALL target fields to show what is missing
        
        # Mocking data found vs missing to demonstrate functionality
        mock_data = {
            "titulo": ("Apartamento 3 quartos", ".title-class", "OK"),
            "preco": ("850000", ".price-value", "OK"),
            "area": ("120", ".area-span", "OK"),
            "quartos": ("3", ".bed-count", "OK"),
            "banheiros": ("2", ".bath-count", "OK"),
            "suites": ("", "", "VAZIO"), # Missing
            "vagas": ("2", ".parking", "OK"),
            "endereco": ("Rua Leonardo Mota, 1200", ".addr", "OK"),
            "bairro": ("Aldeota", ".neighborhood", "OK"),
            "cidade": ("Fortaleza", ".city", "OK"),
            "estado": ("CE", ".state", "OK"),
            "tipo": ("", "", "VAZIO"), # Missing
            "condominio": ("", "", "VAZIO"), # Missing
            "iptu": ("", "", "VAZIO") # Missing
        }

        for field in self.target_fields:
            if field in mock_data:
                val, sel, status = mock_data[field]
                self.tree.insert("", "end", values=(field, val, sel, status))
            else:
                self.tree.insert("", "end", values=(field, "", "", "PENDENTE"))

    def on_double_click(self, event):
        self.train_field()

    def train_field(self):
        """
        Manually input or correct the selector for a field.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um campo na tabela para editar.")
            return

        item = self.tree.item(selected[0])
        field_name = item['values'][0]
        current_sel = item['values'][2]
        
        # Prompt for new selector
        new_selector = simpledialog.askstring(
            "Editar Seletor", 
            f"Defina o seletor CSS/XPath para '{field_name}':",
            initialvalue=current_sel
        )

        if new_selector:
            # Update UI
            self.tree.set(selected[0], "selector", new_selector)
            self.tree.set(selected[0], "status", "MODIFICADO")
            # Update internal profile dict (mock)
            self.current_profile[field_name] = new_selector

    def save_selectors(self):
        portal_name = self.combo_portal.get()
        if not portal_name: return

        # Gather all selectors from the tree
        profile_data = {}
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)
            field = item['values'][0]
            selector = item['values'][2]
            if selector:
                profile_data[field] = selector
        
        # Save to file
        try:
            # Load existing
            all_profiles = {}
            if os.path.exists("scraper_profiles.json"):
                with open("scraper_profiles.json", "r") as f:
                    all_profiles = json.load(f)
            
            # Update
            all_profiles[portal_name] = profile_data
            
            # Write back
            with open("scraper_profiles.json", "w") as f:
                json.dump(all_profiles, f, indent=4)
                
            messagebox.showinfo("Sucesso", f"Perfil '{portal_name}' salvo em scraper_profiles.json")
            self.load_profile_selectors(None) # Reload to confirm
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar perfil: {str(e)}")

    def load_profile_selectors(self, event):
        """Load selectors for the selected portal into the tree"""
        portal_name = self.combo_portal.get()
        if not os.path.exists("scraper_profiles.json"):
            return

        try:
            with open("scraper_profiles.json", "r") as f:
                all_profiles = json.load(f)
            
            profile = all_profiles.get(portal_name, {})
            
            # Clear and repopulate based on profile
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for field in self.target_fields:
                selector = profile.get(field, "")
                status = "CARREGADO" if selector else "PENDENTE"
                self.tree.insert("", "end", values=(field, "", selector, status))
                
        except Exception as e:
            print(f"Error loading profile: {e}")