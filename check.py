import os
import shutil

def fix():
    # 1. Pastas necessárias
    dirs = [
        "app",
        "app/models",
        "app/controllers",
        "app/engines",
        "app/ui",
        "app/config"
    ]

    print("--- Verificando Estrutura ---")
    for d in dirs:
        # Cria a pasta se não existir
        os.makedirs(d, exist_ok=True)
        
        # Cria o __init__.py se não existir
        init_path = os.path.join(d, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("") # Arquivo vazio é suficiente
            print(f"[OK] Criado: {init_path}")
        else:
            print(f"[OK] Já existe: {init_path}")

    # 2. Limpar __pycache__ (evita leitura de arquivos compilados velhos)
    print("\n--- Limpando Cache ---")
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                try:
                    shutil.rmtree(path)
                    print(f"[Limpo] Cache removido: {path}")
                except Exception as e:
                    print(f"[Erro] Não foi possível limpar {path}: {e}")

    print("\n>>> Estrutura corrigida! Tente rodar o main.py agora.")

if __name__ == "__main__":
    fix()