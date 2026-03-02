import os

# --- Identificação do Sistema ---
APP_NAME = "SisAval"
APP_VERSION = "2.0.0 (Analista)"

# --- Caminhos do Sistema ---
# Base dir é a pasta raiz (onde está run_analyzer.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# --- Configurações de Interface ---
THEME_MODE = "System"  # Opções: "System", "Dark", "Light"
COLOR_THEME = "blue"   # Opções: "blue", "green", "dark-blue"

# --- Configurações Estatísticas (Padrão NBR 14.653) ---
DEFAULT_CONFIDENCE = 0.80  # 80% de Confiança
DEFAULT_TOLERANCE = 0.15   # 15% de Campo de Arbítrio

# Garante que as pastas essenciais existam
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Optimizer Settings
# Controls the maximum number of variables combined in Brute Force search.
# Higher values (e.g. 7) increase processing time exponentially.
OPTIMIZER_MAX_VARS_COMBO = 5 

# Statistical Parameters
# Alpha 0.20 corresponds to an 80% Confidence Interval (Standard for NBR 14.653)
STATS_CONFIDENCE_LEVEL = 0.80
STATS_ALPHA = 1 - STATS_CONFIDENCE_LEVEL

# Outlier Detection
# Threshold for Z-Score (Standard Deviations). 2.0 is common (~95%), 1.64 is stricter (~90%).
STATS_ZSCORE_THRESHOLD = 2.0

# NBR Precision Grades (Max Amplitude %)
GRADE_III_LIMIT = 30
GRADE_II_LIMIT = 50