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
        self.show_feed()

    def init_config_canvas(self):
        self.config_canvas = tk.Canvas(self.root)
        self.config_canvas.pack(expand=False, fill=tk.Y, side=tk.LEFT)
        self.create_fund_buttons(sorted(cxlist.list_funds(self.cxdb)))

    def init_plot_canvas(self):
        self.plot_canvas = tk.Canvas(self.root)
        self.plot_canvas.pack(expand=True, fill=tk.BOTH, side=tk.RIGHT)

        self.plot_frame = tk.Frame(self.plot_canvas)

        hscrollbar = tk.Scrollbar(self.plot_canvas,
                                 orient=tk.HORIZONTAL,
                                 command=self.plot_canvas.xview)
        vscrollbar = tk.Scrollbar(self.plot_canvas,
                                 orient=tk.VERTICAL,
                                 command=self.plot_canvas.yview)
        self.plot_canvas.configure(xscrollcommand=hscrollbar.set)
        self.plot_canvas.configure(yscrollcommand=vscrollbar.set)
        hscrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.plot_canvas.create_window((4, 4),
                                       window=self.plot_frame,
                                       anchor=tk.NW,
                                       tags='plot_frame')
        self.plot_frame.bind('<Configure>',
                             lambda event:
                                 self.plot_canvas.configure(scrollregion=self.plot_canvas.bbox(tk.ALL)))

    def plot_figure(self, figure):
        plot_window = plotwindow.PlotWindow(self.plot_frame, figure)

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
        scrollbar = tk.Scrollbar(config_frame,
                                 orient=tk.VERTICAL,
                                 command=self.config_canvas.yview)
        self.config_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.config_canvas.create_window((4, 4),
                                         window=config_frame,
                                         anchor=tk.NW,
                                         tags='config_frame')
        config_frame.bind('<Configure>',
                          lambda event:
                              self.config_canvas.configure(scrollregion=self.config_canvas.bbox(tk.ALL)))
        return config_frame

    def plot(self, fund):
        figure = cxfeed.plot_fund(self.cxdb, self.config, fund)
        self.plot_figure(figure)

    def show_feed(self):
        for figure in cxfeed.plot_feed(self.cxdb, self.config):
            self.plot_figure(figure)

    def loop(self):
        self.root.mainloop()

