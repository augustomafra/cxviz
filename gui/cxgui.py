import os
import sys
import tkinter as tk

sys.path.append(os.path.join(sys.path[0], '..', 'core'))
import cxfeed
import cxlist
import plotwindow

class CxGui(object):
    def __init__(self, cxdb_path, config_file):
        self.cxdb = cxdb_path
        self.config = config_file
        self.root = tk.Tk()
        self.root.title('cxviz')
        self.init_config_canvas()
        self.init_plot_canvas()

    def init_config_canvas(self):
        self.config_canvas = tk.Canvas(self.root)
        self.config_canvas.pack(expand=False, fill=tk.Y, side=tk.LEFT)
        self.create_fund_buttons(sorted(cxlist.list_funds(self.cxdb)))

    def init_plot_canvas(self):
        self.plot_canvas = tk.Canvas(self.root)
        self.plot_canvas.pack(expand=True, fill=tk.BOTH, side=tk.RIGHT)
        self.plot_figure()
        self.plot_figure()

    def plot_figure(self):
        plot_window = plotwindow.PlotWindow(self.plot_canvas)

    def create_fund_buttons(self, funds):
        config_frame = self.create_config_frame()
        largest_name = max(funds, key=lambda fund: len(fund))
        width = len(largest_name)

        for fund in funds:
            tk.Button(config_frame,
                      text=fund,
                      width=width,
                      bg='gray',
                      command=lambda fund=fund: self.plot(fund)).pack()

    def create_config_frame(self):
        config_frame = tk.Frame(self.config_canvas)
        self.scrollbar = tk.Scrollbar(config_frame,
                                      orient=tk.VERTICAL,
                                      command=self.config_canvas.yview)
        self.config_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.config_canvas.create_window((4, 4),
                                         window=config_frame,
                                         anchor=tk.NW,
                                         tags='config_frame')
        config_frame.bind('<Configure>',
                          lambda event:
                              self.config_canvas.configure(scrollregion=self.config_canvas.bbox(tk.ALL)))
        return config_frame

    def plot(self, fund):
        cxfeed.plot_fund(self.cxdb, self.config, fund)

    def loop(self):
        self.root.mainloop()

