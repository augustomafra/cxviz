import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg \
        import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import os
import sys
import tkinter as tk

sys.path.append(os.path.join(sys.path[0], '..', 'core'))
import cxfeed
import cxlist

class CxGui(object):
    def __init__(self, cxdb_path, config_file):
        self.cxdb = cxdb_path
        self.config = config_file
        self.root = tk.Tk()
        self.root.title('cxviz')
        self.create_fund_buttons(sorted(cxlist.list_funds(self.cxdb)))
        self.plot_figure()

    def plot_figure(self):
        frame = tk.Frame(self.canvas)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.create_window((900, 4),
                                  window=frame,
                                  anchor=tk.NE,
                                  tags='frame')
        frame.bind('<Configure>',
                        lambda event:
                            self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))

        figure = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        plot = figure.add_subplot(1, 1, 1)
        plot.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        canvas = FigureCanvasTkAgg(figure, frame)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, frame)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_fund_buttons(self, funds):
        self.configure_scroll_canvas()
        largest_name = max(funds, key=lambda fund: len(fund))
        width = len(largest_name)

        for fund in funds:
            tk.Button(self.frame,
                      text=fund,
                      width=width,
                      bg='gray',
                      command=lambda fund=fund: self.plot(fund)).pack()

    def configure_scroll_canvas(self):
        self.canvas = tk.Canvas(self.root)
        self.frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self.root,
                                      orient=tk.VERTICAL,
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.create_window((4, 4),
                                  window=self.frame,
                                  anchor=tk.NW,
                                  tags='self.frame')
        self.frame.bind('<Configure>',
                        lambda event:
                            self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))

    def plot(self, fund):
        cxfeed.plot_fund(self.cxdb, self.config, fund)

    def loop(self):
        self.root.mainloop()

