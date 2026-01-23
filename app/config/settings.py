APP_TITLE = "SisAval - Avaliação de Imóveis (NBR 14.653)"
APP_SIZE = "1280x800"

# Colors
COLOR_OK = "#d4edda"
COLOR_ALERTA = "#fff3cd"
COLOR_ERRO = "#f8d7da"

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