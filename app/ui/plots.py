from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.stats as stats

class PlotManager:
    def __init__(self, parent):
        self.figure = Figure(figsize=(8, 6), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def plotar_diagnostico(self, obs, prev, resid):
        self.figure.clear()
        
        # 1. Aderência
        ax1 = self.figure.add_subplot(221)
        ax1.scatter(obs, prev, alpha=0.5)
        m = min(obs.min(), prev.min())
        M = max(obs.max(), prev.max())
        ax1.plot([m, M], [m, M], 'r--')
        ax1.set_title("Aderência")
        ax1.grid(True, alpha=0.3)

        # 2. Histograma
        ax2 = self.figure.add_subplot(222)
        ax2.hist(resid, bins=15, color='skyblue', edgecolor='black')
        ax2.set_title("Histograma Resíduos")

        # 3. Homocedasticidade
        ax3 = self.figure.add_subplot(223)
        ax3.scatter(prev, resid, alpha=0.5, color='green')
        ax3.axhline(0, color='red', linestyle='--')
        ax3.set_title("Resíduos vs Previsto")
        ax3.set_xlabel("Valor Previsto")

        # 4. QQ Plot
        ax4 = self.figure.add_subplot(224)
        stats.probplot(resid, dist="norm", plot=ax4)
        ax4.set_title("QQ Plot")

        self.figure.tight_layout()
        self.canvas.draw()