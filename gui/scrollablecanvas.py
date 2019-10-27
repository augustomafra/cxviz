import tkinter as tk

class InvalidDirection(BaseException):
    def __init__(self, direction):
        self.direction = direction

class ScrollableCanvas(tk.Canvas):
    def __init__(self, parent, scroll_direction):
        super().__init__(parent)
        if not (scroll_direction == tk.HORIZONTAL
                or scroll_direction == tk.VERTICAL
                or scroll_direction == tk.BOTH):
            raise InvalidDirection(orient)
        self.orient = scroll_direction

    def create_horizontal_scroll(self, widget):
        scrollbar = tk.Scrollbar(widget if widget else self,
                                 orient=tk.HORIZONTAL,
                                 command=self.xview)
        self.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        return scrollbar

    def create_vertical_scroll(self, widget):
        scrollbar = tk.Scrollbar(widget if widget else self,
                                 orient=tk.VERTICAL,
                                 command=self.yview)
        self.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        return scrollbar

    def configure_widget(self, widget, scroll_in_widget=False):
        scroll_owner = widget if scroll_in_widget else None
        if self.orient == tk.HORIZONTAL:
            self.create_horizontal_scroll(scroll_owner)
        if self.orient == tk.VERTICAL:
            self.create_vertical_scroll(scroll_owner)
        if self.orient == tk.BOTH:
            self.create_horizontal_scroll(scroll_owner)
            self.create_vertical_scroll(scroll_owner)

        self.create_window((4, 4),
                           window=widget,
                           anchor=tk.NW,
                           tags='scrollable_canvas_widget')
        widget.bind('<Configure>',
                    lambda event:
                        self.configure(scrollregion=self.bbox(tk.ALL)))

