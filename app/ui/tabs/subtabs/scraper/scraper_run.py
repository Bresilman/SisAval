import tkinter as tk
from tkinter import ttk, messagebox
import queue

class ScraperRun(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Input
        input_frame = ttk.LabelFrame(self, text="URLs Alvo (uma por linha)")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.txt_urls = tk.Text(input_frame, height=5)
        self.txt_urls.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.txt_urls.insert("1.0", "https://www.example.com/imovel/123")

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.btn_scrape = ttk.Button(btn_frame, text="Iniciar Coleta em Lote", command=self.on_btn_scrape_click)
        self.btn_scrape.pack(side="right", padx=5)
        
        ttk.Button(btn_frame, text="Limpar", command=lambda: self.txt_urls.delete("1.0", tk.END)).pack(side="right", padx=5)

        # Status
        self.lbl_status = ttk.Label(self, text="Pronto", foreground="blue")
        self.lbl_status.grid(row=1, column=0, sticky="w", padx=10)

        # Log
        log_frame = ttk.LabelFrame(self, text="Log de Execução")
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        self.txt_log = tk.Text(log_frame, height=10)
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

    def on_btn_scrape_click(self):
        if self.is_running: return
        
        raw_text = self.txt_urls.get("1.0", tk.END).strip()
        url_list = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        if not url_list:
            messagebox.showwarning("Erro", "Lista de URLs vazia.")
            return

        self.controller.start_bulk_scraping(url_list)
        
        self.is_running = True
        self.btn_scrape.configure(state="disabled")
        self.lbl_status.configure(text="Coletando...", foreground="orange")
        self.txt_log.delete(1.0, tk.END) 
        self.monitor_scraping()

    def monitor_scraping(self):
        try:
            while True:
                msg_type, content = self.controller.msg_queue.get_nowait()
                
                if msg_type == "STATUS":
                    self.lbl_status.configure(text=content)
                elif msg_type == "LOG":
                    self.txt_log.insert(tk.END, f"{content}\n")
                    self.txt_log.see(tk.END)
                elif msg_type == "DATA":
                    # CRITICAL: Send data to controller buffer
                    self.controller.add_scraped_result(content)
                    self.txt_log.insert(tk.END, f"SUCESSO: {content.get('endereco', 'Imóvel sem end.')}\n")
                elif msg_type == "ERROR":
                    self.txt_log.insert(tk.END, f"ERRO: {content}\n")
                elif msg_type == "DONE":
                    self.is_running = False
                    self.btn_scrape.configure(state="normal")
                    self.lbl_status.configure(text="Concluído.", foreground="green")
                    return 

        except queue.Empty:
            pass
            
        if self.is_running:
            self.after(100, self.monitor_scraping)