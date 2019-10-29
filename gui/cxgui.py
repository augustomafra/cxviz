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
        self.root.geometry('1120x600')

        self.init_config_canvas()

        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.init_plot_canvas(right_frame)
        self.init_log_canvas(right_frame)

    def init_config_canvas(self):
        config_canvas = scrollablecanvas.ScrollableCanvas(self.root,
                                                          tk.VERTICAL)
        config_canvas.pack(expand=False, fill=tk.Y, side=tk.LEFT)
        self.config_frame = tk.Frame(config_canvas)
        config_canvas.configure_widget(self.config_frame, True)

    def create_config_buttons(self):
        funds = sorted(cxlist.list_funds(self.cxdb))
        largest_name = max(funds, key=lambda fund: len(fund))
        width = len(largest_name)
        for fund in funds:
            tk.Button(self.config_frame,
                      text=fund,
                      width=width,
                      bg='gray',
                      command=lambda fund=fund: self.plot(fund)).pack()

    def init_plot_canvas(self, right_frame):
        plot_canvas = scrollablecanvas.ScrollableCanvas(right_frame,
                                                        tk.BOTH)
        self.plot_frame = tk.Frame(plot_canvas)
        plot_canvas.configure_widget(self.plot_frame)
        plot_canvas.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

    def init_log_canvas(self, right_frame):
        self.log_widget = tk.Text(right_frame, height=8)
        self.log_widget.pack(expand=False, fill=tk.X)

    def log(self, text):
        self.log_widget.insert(tk.END, text)
        self.log_widget.see(tk.END)
        self.root.update()

    def logln(self, text):
        self.log('{}\n'.format(text))

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

