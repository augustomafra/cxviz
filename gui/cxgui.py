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
        self.init_root()
        self.init_config_canvas()
        right_frame = self.create_right_frame()
        self.init_plot_canvas(right_frame)
        self.init_log_canvas(right_frame)

    def init_root(self):
        self.root = tk.Tk()
        self.root.title('cxviz')
        self.root.geometry('1120x600')

    def init_config_canvas(self):
        self.config_canvas = scrollablecanvas.ScrollableCanvas(self.root,
                                                               tk.VERTICAL)
        self.config_canvas.pack(expand=False, fill=tk.Y, side=tk.LEFT)
        self.config_frame = tk.Frame(self.config_canvas)
        self.config_canvas.configure_widget(self.config_frame, True)

    def create_right_frame(self):
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        return right_frame

    def init_plot_canvas(self, right_frame):
        plot_canvas = scrollablecanvas.ScrollableCanvas(right_frame,
                                                        tk.BOTH)
        self.plot_frame = tk.Frame(plot_canvas)
        plot_canvas.configure_widget(self.plot_frame)
        plot_canvas.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

    def init_log_canvas(self, right_frame):
        self.log_widget = tk.Text(right_frame, height=8)
        self.log_widget.pack(expand=False, fill=tk.X)

        def clipboard_handler(event):
            selection = None
            try:
                selection = self.log_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError as error:
                return 'break'
            if selection:
                self.log_widget.clipboard_clear()
                self.log_widget.clipboard_append(selection)
            return 'break'

        self.log_widget.bind('<Key>', lambda event: 'break')
        self.log_widget.bind('<Control-c>', clipboard_handler)

    def create_config_buttons(self):
        funds = sorted(cxlist.list_funds(self.cxdb))
        if len(funds) == 0:
            raise Exception('Error: cxdb is empty: {}'.format(self.cxdb))
        largest_name = max(funds, key=lambda fund: len(fund))
        width = len(largest_name)
        self.config_canvas.config(width=9 * width)
        for fund in funds:
            tk.Button(self.config_frame,
                      text=fund,
                      width=width,
                      bg='gray',
                      command=lambda fund=fund: self.plot(fund)).pack()

    def log(self, text):
        self.log_widget.insert(tk.END, text)
        self.log_widget.see(tk.END)
        self.root.update()

    def logln(self, text):
        self.log('{}\n'.format(text))

    def create_plot_window(self, figure):
        plotwindow.PlotWindow(self.plot_frame,
                              figure).pack(side=tk.LEFT, expand=False)

    def plot(self, fund):
        figure = cxfeed.plot_fund(self.cxdb, self.config, fund)
        self.create_plot_window(figure)

    def show_feed(self):
        for figure in cxfeed.plot_feed(self.cxdb, self.config):
            self.create_plot_window(figure)

    def loop(self):
        self.root.mainloop()

