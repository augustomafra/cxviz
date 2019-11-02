import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg \
        import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import tkinter as tk

class PlotWindow(tk.Frame):
    def __init__(self, parent, figure):
        super().__init__(parent)
        self.figure = figure
        self.create_close_button()
        fig_canvas = self.plot_figure()
        self.create_toolbar(fig_canvas)
        self.pack(side=tk.LEFT, expand=False)

    def create_close_button(self):
        tk.Button(self,
                  text='X',
                  bg='white',
                  command=self.destroy).pack(side=tk.TOP, anchor=tk.E)

    def plot_figure(self):
        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        return canvas

    def create_toolbar(self, canvas):
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def destroy(self):
        matplotlib.pyplot.close(self.figure)
        super().destroy()

