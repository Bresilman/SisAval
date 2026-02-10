import tkinter as tk
from tkinter import ttk, messagebox

class ScraperConfig(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        self.load_defaults()

    def setup_ui(self):
        # Configure layout weights
        self.columnconfigure(0, weight=1)
        
        # --- Network Settings Group ---
        net_group = ttk.LabelFrame(self, text="Configurações de Rede")
        net_group.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        net_group.columnconfigure(1, weight=1)

        # User-Agent
        ttk.Label(net_group, text="User-Agent:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_user_agent = ttk.Entry(net_group)
        self.ent_user_agent.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Timeout
        ttk.Label(net_group, text="Timeout (seg):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_timeout = ttk.Entry(net_group, width=10)
        self.ent_timeout.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Max Retries
        ttk.Label(net_group, text="Max Tentativas:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.ent_retries = ttk.Spinbox(net_group, from_=0, to=10, width=5)
        self.ent_retries.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # --- Proxy Settings Group ---
        proxy_group = ttk.LabelFrame(self, text="Proxy (Opcional)")
        proxy_group.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        proxy_group.columnconfigure(1, weight=1)

        # Proxy URL
        ttk.Label(proxy_group, text="URL do Proxy:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_proxy = ttk.Entry(proxy_group)
        self.ent_proxy.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # --- Advanced Settings ---
        adv_group = ttk.LabelFrame(self, text="Avançado")
        adv_group.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.var_headless = tk.BooleanVar(value=True)
        self.chk_headless = ttk.Checkbutton(adv_group, text="Modo Headless (Navegador oculto)", variable=self.var_headless)
        self.chk_headless.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.var_images = tk.BooleanVar(value=False)
        self.chk_images = ttk.Checkbutton(adv_group, text="Carregar Imagens (Mais lento)", variable=self.var_images)
        self.chk_images.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # --- Actions ---
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Salvar Configurações", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Restaurar Padrões", command=self.load_defaults).pack(side="left", padx=5)

    def load_defaults(self):
        """Load default values into the fields"""
        self.ent_user_agent.delete(0, tk.END)
        self.ent_user_agent.insert(0, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.ent_timeout.delete(0, tk.END)
        self.ent_timeout.insert(0, "30")
        
        self.ent_retries.set(3)
        self.ent_proxy.delete(0, tk.END)
        self.var_headless.set(True)
        self.var_images.set(False)

    def save_settings(self):
        """Collect values and send to controller/engine"""
        settings = {
            "user_agent": self.ent_user_agent.get(),
            "timeout": int(self.ent_timeout.get() or 30),
            "retries": int(self.ent_retries.get()),
            "proxy": self.ent_proxy.get(),
            "headless": self.var_headless.get(),
            "load_images": self.var_images.get()
        }
        
        # Here you would typically call: self.controller.update_settings(settings)
        print("Settings saved:", settings) # Debug
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")