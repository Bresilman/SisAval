import sys
import os
import tkinter as tk
from tkinter import messagebox

# Adiciona o diretório atual ao path para garantir que imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.controllers.app_controller import AppController

def main():
    try:
        app = AppController()
        app.run()
    except Exception as e:
        # Fallback para erros críticos antes da UI carregar
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Crítico", f"Falha ao iniciar o SisAval:\n{str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()