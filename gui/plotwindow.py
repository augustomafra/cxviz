import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg \
        import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import tkinter as tk

class PlotWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.pack(side=tk.LEFT, expand=False)
        figure = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        plot = figure.add_subplot(1, 1, 1)
        plot.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        canvas = FigureCanvasTkAgg(figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

