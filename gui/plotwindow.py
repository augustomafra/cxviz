import sys
import matplotlib
import numpy

matplotlib.use('TkAgg')
if sys.platform == 'win32':
    from matplotlib.backends.backend_tkagg \
            import FigureCanvasTkAgg, NavigationToolbar2Tk
else:
    from matplotlib.backends.backend_tkagg \
        import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import tkinter as tk

class Cursor:
    def __init__(self, event):
        self.axes = event.inaxes
        self.dates = self.axes.lines[0].get_xdata()
        self.values = self.axes.lines[0].get_ydata()

        self.vline = self.axes.axvline(x=self.get_date(event), color='k')
        self.hline = self.axes.axhline(y=self.get_value(event), color='k')
        self.legend = self.axes.text(0.7, 1.05, '', transform=self.axes.transAxes)

    def mouse_moved(self, event):
        date = self.get_date(event)
        idx = min(numpy.searchsorted(self.dates, date), len(self.dates) - 1)
        date, value = self.dates[idx], self.values[idx]

        self.vline.set_xdata(date)
        self.hline.set_ydata(value)
        self.legend.set_text(self.format(date, value))
        self.axes.figure.canvas.draw()

    def get_date(self, event):
        return matplotlib.dates.num2date(event.xdata)

    def get_value(self, event):
        return event.ydata

    def format(self, date, value):
        return '{} : {}'.format(date.strftime('%Y-%m-%d'),
                                value if not numpy.isnan(value) else '-')

class PlotWindow(tk.Frame):
    def __init__(self, parent, figure):
        super().__init__(parent)
        self.figure = figure
        self.create_close_button()
        fig_canvas = self.plot_figure()
        self.create_toolbar(fig_canvas)
        self.cursors = {}

        def dispatch_cursor(event):
            axes = event.inaxes
            if not axes:
                return
            if axes not in self.cursors:
                self.cursors[axes] = Cursor(event)
            else:
                self.cursors[axes].mouse_moved(event)

        self.figure.canvas.mpl_connect('motion_notify_event', dispatch_cursor)

    def create_close_button(self):
        tk.Button(self,
                  text='X',
                  bg='white',
                  command=self.destroy).pack(side=tk.TOP, anchor=tk.E)

    def plot_figure(self):
        canvas = FigureCanvasTkAgg(self.figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        return canvas

    def create_toolbar(self, canvas):
        if sys.platform == 'win32':
            toolbar = NavigationToolbar2Tk(canvas, self)
        else:
            toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def destroy(self):
        matplotlib.pyplot.close(self.figure)
        super().destroy()

