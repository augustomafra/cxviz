import tkinter as tk

class CxGui(object):
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.label = tk.Label(self.frame, text='CxGui')
        self.label.pack()

    def loop(self):
        self.root.mainloop()

