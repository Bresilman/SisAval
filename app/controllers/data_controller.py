import pandas as pd
import numpy as np

class DataController:
    def __init__(self, main_controller=None):
        self.main_controller = main_controller
        self.df = None
        self.filepath = ""
        self.excluded_indices = []

    def load_file(self, filepath):
        self.filepath = filepath
        self.excluded_indices = [] # Reset on new load
        try:
            if filepath.endswith('.csv'):
                try:
                    df = pd.read_csv(filepath)
                except UnicodeDecodeError:
                    df = pd.read_csv(filepath, encoding='latin1', sep=None, engine='python')
            elif filepath.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(filepath)
            else:
                return False, "Formato não suportado."

            self.df = self._sanitize_dataframe(df)
            
            rows = len(self.df)
            return True, f"Carregado: {rows} linhas."

        except Exception as e:
            return False, f"Erro: {str(e)}"

    def _sanitize_dataframe(self, df):
        # 1. Clean Headers
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^\w]', '', regex=True)
        
        # 2. Fix Numeric
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    clean_series = df[col].astype(str).str.replace('R$', '', regex=False).str.strip()
                    if clean_series.str.contains(',').any():
                        clean_series = clean_series.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    
                    numeric = pd.to_numeric(clean_series, errors='coerce')
                    if numeric.notna().sum() / len(df) > 0.7:
                        df[col] = numeric
                except: pass
        return df

    def get_data(self, include_excluded=False):
        """
        Returns the DataFrame. 
        If include_excluded is False (default), returns only active rows.
        """
        if self.df is None: return None
        
        if not include_excluded and self.excluded_indices:
            # Filter out excluded indices
            return self.df.drop(index=self.excluded_indices, errors='ignore')
            
        return self.df

    def set_excluded_indices(self, indices_list):
        """Sets the list of indices to be ignored in analysis"""
        self.excluded_indices = indices_list
        # print(f"DataController: Ignorando {len(indices_list)} linhas.")

    def get_health_report(self):
        if self.df is None: return {}
        
        active_df = self.get_data() # Respects exclusion
        total = len(active_df)
        nan_rows = active_df.isnull().any(axis=1).sum()
        
        report = {
            "total_rows": total,
            "rows_with_nan": nan_rows,
            "clean_rows": total - nan_rows,
            "columns_info": []
        }
        
        for col in active_df.columns:
            dtype = str(active_df[col].dtype)
            missing = active_df[col].isnull().sum()
            report["columns_info"].append({
                "name": col,
                "type": "Num" if "float" in dtype or "int" in dtype else "Txt",
                "missing": missing
            })
        return report

    def get_numeric_columns(self):
        df = self.get_data()
        if df is None: return []
        return df.select_dtypes(include=[np.number]).columns.tolist()