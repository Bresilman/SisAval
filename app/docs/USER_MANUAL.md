📘 SisAval - Documentation & User Manual
1. Introduction

SisAval is a software for Real Estate Appraisal (Engenharia de Avaliações) developed in Python. It complies with NBR 14.653-2 (Urban Properties), offering tools for Statistical Inference (Regression), Evolutionary Method (Cost), and Spatial Analysis.
2. Interface Reference (The Tabs)
Tab 1: Dados (Data Management)

The command center for your sample data.

    Sub-tab: Tabela (Table): View raw data. Right-click to delete outliers.

    Sub-tab: Definição (Definition): Select dependent (Y) and independent (X) variables.

    Sub-tab: Ferramentas (Tools):

        Creator: Create transformations (Ln, 1/x, x²) to linearize data.

        Encoder: Convert text (e.g., "Good", "Bad") into numbers (2, 1).

        Sanitizer: Automatically remove statistical outliers (Z-Score > 2).

    Sub-tab: Estatística Descritiva: Check averages and Coefficient of Variation (CV) before modeling.

Tab 2: Estatística (Regression & Diagnostics)

Where the mathematical model is calculated.

    Sub-tab: Resumo: Dashboard with R², F-Test, and P-Values. Includes an interpretation guide.

    Sub-tab: Tabela de Resíduos: Shows predicted vs. real prices. Highlights outliers in red.

    Sub-tab: Gráficos: Visual diagnostics (Adherence, Histogram, Homoscedasticity, QQ-Plot).

    Sub-tab: Correlação: Heatmap to detect Multicollinearity (variables fighting each other).

Tab 3: Gráficos (Deep Analysis)

    Exploratory: Histograms and BoxPlots to understand data distribution.

    Diagnostic: Cook's Distance (Influence) and Residuals vs. X.

    Scenarios: Sensitivity curves (Ceteris Paribus).

Tab 4: Validação NBR (Legal Compliance)

    Checklist: Automated Pass/Fail for statistical tests.

    Enquadramento: Scorecard to determine Grade I, II, or III.

    Precisão & Fronteiras: Checks if the calculated value is within sample limits (Extrapolation) and calculates prediction amplitude.

Tab 5: Otimizador (The Robot)

    Config: Set expected signs (e.g., Area must be positive) and filters (P-value < 10%).

    Results: Lists top models found by Brute Force or Stepwise algorithms.

Tab 6: Calculadora (Valuation)

    Input attributes of the subject property.

    Automatically calculates Unit Value and Total Value.

    Shows the "Field of Arbitrament" (Interval).

Tab 7: Método Evolutivo (Cost Approach)

    Constructions: Calculate main building cost using CUB, BDI, and Ross-Heidecke depreciation.

    Complementary: Calculate walls, pools, paving.

    Summary: Sums Land + Constructions to get Final Value.

Tab 8: Fatores (Homogenization)

    Used when data is scarce. Adjusts samples using coefficients (Offer, Location, Pattern) to calculate a homogenized mean.

Tab 9: Mapa (Spatial)

    Plots samples on a map (OpenStreetMap/Google).

    Generates Value Heatmaps based on sample prices.

Tab 10: Banco de Dados (History)

    Stores historical data from previous appraisals.

    Allows importing/exporting data for market trend analysis.

3. Workflow: How to perform an Evaluation
Step 1: Data Collection

    Use the Scraper (in Data Tab) to download HTMLs from portals.

    Or load an Excel file with your field research.

    Sanitize: Use the "Ferramentas" tab to convert text variables to numbers (Encoder) and check for typing errors.

Step 2: Exploratory Analysis

    Go to Tab 3 (Graphics). Check Histograms.

    If data looks skewed (not a bell curve), apply Ln(x) in Tab 1 (Data).

Step 3: Modeling

    Manual: Select X and Y in Tab 1 and click "Calcular".

    Automatic: Go to Tab 5 (Optimizer). Set expected signs (e.g., Conservation = +). Run Stepwise. Load the best model.

Step 4: Refinement

    Go to Tab 2 (Statistics) -> Tabela de Resíduos.

    Look for red rows (Outliers). Identify them by ID.

    Go back to Tab 1, delete the bad rows, and recalculate.

    Repeat until diagnostics (Normality, Homoscedasticity) pass in Tab 4 (Validation).

Step 5: Valuation

    Go to Tab 6 (Calculator).

    Input the subject property details.

    Check Tab 4 (Validation -> Fronteiras) to ensure you are not extrapolating.

Step 6: Reporting

    Go to Configurações: Set your name and title.

    Go to Tab 12 (Relatório): Write the Market Diagnosis.

    Click "Gerar PDF".

4. Interpretation Guide (The "Cheat Sheet")
Statistical Metrics

    R² (Determination): How much of the price is explained by the math?

        > 0.75: Excellent (Grade III potential).

        < 0.50: Poor model. Missing variables?

    Significance F: Must be <0.05. If higher, the model is accidental/random.

    t-Student (P-Value): Must be <0.10 for each variable. If Pool has P-Value 0.40, it means the pool doesn't affect the price in this market. Remove it.

    VIF (Multicollinearity): Must be <10. If Area and Rooms both have VIF 15, they are saying the same thing. Remove one.

Depreciation (Ross-Heidecke)

    New: k=1.00.

    Regular: k≈0.70 to 0.80.

    Needs Repairs: k<0.50.

    SisAval calculates this automatically based on Age and Life Span.