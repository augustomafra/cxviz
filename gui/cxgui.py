import os
import sys
import tkinter as tk

sys.path.append(os.path.join(sys.path[0], '..', 'core'))
import cxfeed
import cxlist
import plotwindow
import scrollablecanvas

class CxGui(object):
    def __init__(self, cxdb_path, config_file):
        self.cxdb = cxdb_path
        self.config = config_file
        self.root = tk.Tk()
        self.root.title('cxviz')
        self.root.geometry('1000x600')
        self.init_config_canvas()
        self.init_plot_canvas()
        self.show_feed()

    def init_config_canvas(self):
        config_canvas = scrollablecanvas.ScrollableCanvas(self.root,
                                                          tk.VERTICAL)
        config_canvas.pack(expand=False, fill=tk.Y, side=tk.LEFT)
        config_frame = tk.Frame(config_canvas)
        config_canvas.configure_widget(config_frame, True)

        funds = sorted(cxlist.list_funds(self.cxdb))
        largest_name = max(funds, key=lambda fund: len(fund))
        width = len(largest_name)
        for fund in funds:
            tk.Button(config_frame,
                      text=fund,
                      width=width,
                      bg='gray',
                      command=lambda fund=fund: self.plot(fund)).pack()

    def init_plot_canvas(self):
        plot_canvas = scrollablecanvas.ScrollableCanvas(self.root,
                                                        tk.BOTH)
        self.plot_frame = tk.Frame(plot_canvas)
        plot_canvas.configure_widget(self.plot_frame)
        plot_canvas.pack(expand=True, fill=tk.BOTH, side=tk.RIGHT)

    def plot_figure(self, figure):
        plotwindow.PlotWindow(self.plot_frame, figure)

    def plot(self, fund):
        figure = cxfeed.plot_fund(self.cxdb, self.config, fund)
        self.plot_figure(figure)

    def show_feed(self):
        for figure in cxfeed.plot_feed(self.cxdb, self.config):
            self.plot_figure(figure)

    def loop(self):
        self.root.mainloop()

