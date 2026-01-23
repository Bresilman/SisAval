import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class GoogleConfigSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr = ttk.Frame(self, padding=20)
        fr.pack(fill='both', expand=True)

        ttk.Label(fr, text="Configuração Google Maps Platform", font=("Arial", 12, "bold")).pack(anchor='w')
        
        msg = ("Para usar recursos avançados (Trânsito Real, Places), você precisa de uma API Key.\n"
               "O Google oferece US$ 200/mês grátis, mas exige cartão de crédito.")
        ttk.Label(fr, text=msg, foreground="gray").pack(anchor='w', pady=10)
        
        fr_key = ttk.LabelFrame(fr, text="Credenciais", padding=15)
        fr_key.pack(fill='x', pady=10)
        
        ttk.Label(fr_key, text="API Key:").pack(side='left')
        self.ent_key = ttk.Entry(fr_key, width=40, show="*")
        self.ent_key.pack(side='left', padx=10)
        
        ttk.Button(fr_key, text="Conectar / Testar", command=self._connect).pack(side='left')

        link = ttk.Label(fr, text="Obter Chave no Google Cloud Console", foreground="blue", cursor="hand2")
        link.pack(pady=20)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://console.cloud.google.com/google/maps-apis/credentials"))

        self.lbl_status = ttk.Label(fr, text="Status: Desconectado", foreground="red")
        self.lbl_status.pack()

    def _connect(self):
        key = self.ent_key.get().strip()
        if not key: return
        
        ok = self.controller.google_engine.connect(key)
        if ok:
            self.lbl_status.config(text="Status: CONECTADO ✅", foreground="green")
            messagebox.showinfo("Sucesso", "Google API Conectada!")
        else:
            self.lbl_status.config(text="Status: Erro na Conexão", foreground="red")
            messagebox.showerror("Erro", "Chave inválida ou erro de rede.")