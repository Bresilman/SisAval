import tkinter as tk
from tkinter import ttk, messagebox
import threading

class GooglePolesSubTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        fr_top = ttk.Frame(self, padding=10)
        fr_top.pack(fill='x')

        ttk.Label(fr_top, text="Definição de Pólos Valorizantes", font=("Arial", 11, "bold")).pack(anchor='w')
        ttk.Label(fr_top, text="O sistema calculará a distância de carro de todas as amostras até estes pontos.").pack(anchor='w')

        # Lista de Polos
        self.tree = ttk.Treeview(self, columns=("Nome", "Lat", "Lon"), show="headings", height=5)
        self.tree.heading("Nome", text="Nome do Pólo")
        self.tree.heading("Lat", text="Latitude")
        self.tree.heading("Lon", text="Longitude")
        self.tree.pack(fill='x', padx=10, pady=5)

        # Controles de Adição
        fr_add = ttk.Frame(self, padding=5)
        fr_add.pack(fill='x', padx=10)
        
        self.ent_name = ttk.Entry(fr_add, width=15); self.ent_name.insert(0, "Shopping")
        self.ent_name.pack(side='left', padx=2)
        
        self.ent_lat = ttk.Entry(fr_add, width=10); self.ent_lat.pack(side='left', padx=2)
        self.ent_lon = ttk.Entry(fr_add, width=10); self.ent_lon.pack(side='left', padx=2)
        
        ttk.Button(fr_add, text="Adicionar Manual", command=self._add_manual).pack(side='left', padx=5)
        ttk.Button(fr_add, text="Pegar do Mapa (Clique Dir.)", command=self._get_from_map).pack(side='left', padx=5)

        # Botão de Ação
        ttk.Button(self, text="🚗 Calcular Matriz de Distâncias (Google)", command=self._run_matrix).pack(pady=10)
        self.lbl_progress = ttk.Label(self, text="")
        self.lbl_progress.pack()

    def _add_manual(self):
        self.tree.insert("", "end", values=(self.ent_name.get(), self.ent_lat.get(), self.ent_lon.get()))

    def _get_from_map(self):
        # Pega do controller (definido na aba Mapa)
        coords = self.controller.current_map_target
        if coords:
            self.ent_lat.delete(0, tk.END); self.ent_lat.insert(0, str(coords[0]))
            self.ent_lon.delete(0, tk.END); self.ent_lon.insert(0, str(coords[1]))
        else:
            messagebox.showwarning("Aviso", "Selecione um ponto na aba Mapa > Visualização primeiro.")

    def _run_matrix(self):
        # Prepara dicionário de alvos
        targets = {}
        for item in self.tree.get_children():
            vals = self.tree.item(item)['values']
            targets[vals[0]] = (float(vals[1]), float(vals[2]))

        if not targets: return messagebox.showwarning("Aviso", "Adicione pólos primeiro.")

        self.controller.acao_calcular_google_matrix(targets)