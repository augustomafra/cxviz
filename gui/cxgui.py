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
        self.create_fund_buttons(sorted(cxlist.list_funds(self.cxdb)))

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
                                  anchor='nw',
                                  tags='self.frame')
        self.frame.bind('<Configure>',
                        lambda event: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

    def plot(self, fund):
        cxfeed.plot_fund(self.cxdb, self.config, fund)

    def loop(self):
        cxfeed.show_feed(self.cxdb, self.config)
        self.root.mainloop()

