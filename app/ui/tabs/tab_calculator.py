import customtkinter as ctk
from tkinter import messagebox

class TabCalculator(ctk.CTkFrame):
    """
    Aba Calculadora de Avaliação.
    Gera campos dinâmicos baseados no modelo treinado para estimar valor de novos imóveis.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.input_widgets = {} # {var_name: entry_widget}
        
        # Layout Principal
        self.grid_columnconfigure(0, weight=1) # Inputs
        self.grid_columnconfigure(1, weight=1) # Resultados
        self.grid_rowconfigure(0, weight=1)
        
        # --- PAINEL ESQUERDO (INPUTS) ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.left_frame, text="Características do Avaliando", 
                   font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.lbl_model_info = ctk.CTkLabel(self.left_frame, text="Nenhum modelo calibrado.", text_color="gray")
        self.lbl_model_info.pack(pady=5)
        
        # Área de Scroll para Inputs Dinâmicos
        self.scroll_inputs = ctk.CTkScrollableFrame(self.left_frame)
        self.scroll_inputs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.btn_calc = ctk.CTkButton(self.left_frame, text="Calcular Valor", 
                                    state="disabled", fg_color="green",
                                    command=self._on_calculate)
        self.btn_calc.pack(pady=20, padx=20, fill="x")

        # --- PAINEL DIREITO (RESULTADOS) ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.right_frame, text="Laudo de Avaliação (Estimativa)", 
                   font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Display de Resultados
        self.res_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.res_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Labels de Resultado
        self.lbl_val_central = self._create_result_label("Valor de Mercado (Central):", 24, "blue")
        self.lbl_intervalo = self._create_result_label("Intervalo de Confiança (80%):", 14)
        self.lbl_precisao = self._create_result_label("Grau de Precisão:", 14)
        self.lbl_extrapolacao = self._create_result_label("", 12, "orange") # Alerta

        # Campo de Arbítrio
        self.arb_frame = ctk.CTkFrame(self.right_frame)
        self.arb_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(self.arb_frame, text="Campo de Arbítrio (+/- 15%):").pack(anchor="w", padx=10, pady=5)
        
        self.slider_arb = ctk.CTkSlider(self.arb_frame, from_=0.85, to=1.15, number_of_steps=30, command=self._update_arbitrio)
        self.slider_arb.set(1.0)
        self.slider_arb.pack(fill="x", padx=10, pady=5)
        
        self.lbl_val_final = ctk.CTkLabel(self.arb_frame, text="Valor Final Adotado: R$ ---", font=ctk.CTkFont(weight="bold"))
        self.lbl_val_final.pack(pady=10)
        
        # Variáveis internas para cálculo de arbítrio
        self.current_value = 0.0

    def _create_result_label(self, title, size, color=None):
        frame = ctk.CTkFrame(self.res_frame, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        lbl = ctk.CTkLabel(frame, text="---", font=ctk.CTkFont(size=size, weight="bold"), text_color=color)
        lbl.pack(anchor="w")
        return lbl

    def setup_inputs(self, features_list):
        """
        Chamado pelo Controller. Constrói o formulário baseado nas variáveis X do modelo.
        """
        # Limpa anteriores
        for widget in self.scroll_inputs.winfo_children():
            widget.destroy()
        self.input_widgets = {}
        
        # Atualiza Status
        self.lbl_model_info.configure(text=f"Modelo Ativo: {len(features_list)} variáveis explicativas")
        self.btn_calc.configure(state="normal")
        
        for feat in features_list:
            if feat == 'const': continue
            
            # Tratamento de Label (Remove ln_, log_, etc para ficar bonito)
            clean_label = feat
            if feat.startswith("ln_"): clean_label = feat[3:] + " (Log)"
            elif feat.startswith("log_"): clean_label = feat[4:] + " (Log)"
            
            # Container do Campo
            row = ctk.CTkFrame(self.scroll_inputs, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=clean_label.replace("_", " ").title() + ":", anchor="w").pack(fill="x")
            entry = ctk.CTkEntry(row)
            entry.pack(fill="x")
            
            self.input_widgets[feat] = entry

    def _on_calculate(self):
        """Coleta dados e envia para o Controller."""
        inputs = {}
        try:
            for feat, widget in self.input_widgets.items():
                val_str = widget.get().replace(",", ".") # Suporte a vírgula BR
                if not val_str:
                    messagebox.showwarning("Aviso", f"Preencha o campo {feat}")
                    return
                inputs[feat] = float(val_str)
            
            # Envia para o Controller calcular
            self.controller.acao_calcular_valor(inputs)
            
        except ValueError:
            messagebox.showerror("Erro", "Digite apenas números válidos.")

    def display_results(self, result_data):
        """Recebe os resultados calculados e exibe."""
        val_central = result_data['value']
        lower = result_data['lower']
        upper = result_data['upper']
        precision = result_data['precision_grade']
        is_extrapolated = result_data.get('extrapolated', False)
        
        # Guarda para o slider de arbítrio
        self.current_value = val_central
        self.slider_arb.set(1.0)
        
        # Formatação Moeda
        fmt = lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        self.lbl_val_central.configure(text=fmt(val_central))
        self.lbl_intervalo.configure(text=f"{fmt(lower)}  a  {fmt(upper)}")
        
        # Cor da Precisão
        p_color = "green" if "Grau III" in precision else "orange" if "Grau II" in precision else "red"
        self.lbl_precisao.configure(text=precision, text_color=p_color)
        
        # Alerta de Extrapolação
        if is_extrapolated:
            self.lbl_extrapolacao.configure(text="⚠️ ALERTA: Valores inseridos extrapolam a amostra (Fronteira dos Dados).")
        else:
            self.lbl_extrapolacao.configure(text="")
            
        # Atualiza Arbítrio
        self._update_arbitrio(1.0)

    def _update_arbitrio(self, value):
        factor = float(value)
        final_val = self.current_value * factor
        fmt = f"R$ {final_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.lbl_val_final.configure(text=f"Valor Final Adotado ({factor:.2f}x): {fmt}")