import concurrent.futures
import itertools
import platform
import tkinter as tk

from PIL import Image, ImageTk

__all__ = ["ScrollFrame", "CollapsibleFrame", "PageViewer"]


# ************************ #
#  Scrollable Frame Class  #
# ************************ #
# (inspired by:
#  - https://github.com/RomneyDa/tkinter-scrollable-frame/blob/master/ScrollableFrame/ScrollableFrame.py   # skipcq
#  - https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01
# )
class ScrollFrame(tk.Frame):
    """A Scrollable Frame Class"""

    def __init__(self, parent, event_handler, *args, **kwargs):
        super().__init__(parent)
        self.handler = event_handler
        self.handler.set_funcs("set-document", self.set_document)

        self.canvas = tk.Canvas(self, borderwidth=0, background="green")
        self.viewPort = tk.Frame(
            self.canvas, background="#ffffff"
        )  # place a frame on the canvas, this frame will hold the child widgets

        # CUSTOM OPTION
        # Determines if there will be just a horizontal, just a vertical or both scroll bars
        if "direction" in kwargs and kwargs["direction"] in [
            "both",
            "horizontal",
            "vertical",
        ]:
            self.direction = kwargs["direction"]
            kwargs.pop("direction")
        else:
            self.direction = "both"

        # config_sf function applies any remaining keyword properties
        self.config_sf(**kwargs)

        self.viewPort.bind("<Configure>", self._on_frame_change)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.viewPort, anchor="nw"
        )

        self.xscrollbar = tk.Scrollbar(
            self, orient="horizontal", command=self.canvas.xview
        )
        self.canvas.configure(xscrollcommand=self.xscrollbar.set)
        self.yscrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.yscrollbar.set)

        # These functions prevent the canvas from scrolling unless the cursor is in it
        self.canvas.bind("<Enter>", self._enter_frame)
        self.canvas.bind("<Leave>", self._leave_frame)

        # This method places the scrollbars onto the containing frame
        self.set_direction(self.direction)

        # Place the canvas onto the container and weigh relevant rows/cols for proper expansion
        self.canvas.grid(row=0, column=0, sticky=tk.S + tk.E + tk.N + tk.W)
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 1, weight=0)
        tk.Grid.columnconfigure(self, 1, weight=0)

    def _on_frame_change(self, _event):
        """Function called when frame size changed"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        """Cross platform scroll wheel event"""
        if platform.system() == "Windows":
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == "Darwin":
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def _on_shift_mouse_wheel(self, event):
        """Function to scroll horizontally while holding shift"""
        if platform.system() == "Windows":
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == "Darwin":
            self.canvas.xview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.xview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.xview_scroll(1, "units")

    def _enter_frame(self, _event):
        """Bind all scrolling events when entering frame"""
        if platform.system() == "Linux":
            if self.direction != "horizontal":
                self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)
                self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)
            if self.direction != "vertical":
                self.canvas.bind_all("<Shift-Button-4>", self._on_shift_mouse_wheel)
                self.canvas.bind_all("<Shift-Button-5>", self._on_shift_mouse_wheel)
        else:
            if self.direction != "horizontal":
                self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
            if self.direction != "vertical":
                self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mouse_wheel)

    def _leave_frame(self, _event):
        """Unbind all scrolling events when leaving frame"""
        if platform.system() == "Linux":
            if self.direction != "horizontal":
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")
            if self.direction != "vertical":
                self.canvas.unbind_all("<Shift-Button-4>")
                self.canvas.unbind_all("<Shift-Button-5>")
        else:
            if self.direction != "horizontal":
                self.canvas.unbind_all("<MouseWheel>")
            if self.direction != "vertical":
                self.canvas.unbind_all("<Shift-MouseWheel>")

    def set_direction(self, direction):
        """Set scrollbars"""
        if direction in ["both", "horizontal", "vertical"]:
            self.direction = direction
            self.xscrollbar.grid_forget()
            self.yscrollbar.grid_forget()
            if self.direction != "horizontal":
                self.yscrollbar.grid(row=0, column=1, sticky=tk.S + tk.E + tk.N + tk.W)
            if self.direction != "vertical":
                self.xscrollbar.grid(row=1, column=0, sticky=tk.S + tk.E + tk.N + tk.W)
        else:
            raise ValueError("Direction must be 'horizontal', 'vertical', or 'both'")

    def config_sf(self, **options):
        """Overwrites the config for containing frame and sends options to the scrollable frame"""  # skipcq

        # Some options will only apply to the canvas
        if "highlightbackground" in options:
            self.canvas.configure(
                highlightbackground=options.get("highlightbackground")
            )
            options.pop("highlightbackground")

        if "highlightcolor" in options:
            self.canvas.configure(highlightcolor=options.get("highlightcolor"))
            options.pop("highlightcolor")

        if "highlightthickness" in options:
            self.canvas.configure(highlightthickness=options.get("highlightthickness"))
            options.pop("highlightthickness")

        # Some options will apply to both the frame and canvas
        if "bg" in options and "background" in options:
            raise KeyError("Can't use both bg and background options")
        if "bg" in options:
            self.canvas.configure(bg=options.get("bg"))
        elif "background" in options:
            self.canvas.configure(bg=options.get("background"))

        if "bd" in options and "borderwidth" in options:
            raise KeyError("Can't use both bd and borderwidth options")
        if "bd" in options:
            self.canvas.configure(bd=options.get("bd"))
            options.pop("bd")
        elif "borderwidth" in options:
            self.canvas.configure(bd=options.get("borderwidth"))
            options.pop("borderwidth")

        self.canvas.configure(height=options.get("height"))
        self.canvas.configure(width=options.get("width"))
        self.canvas.configure(cursor=options.get("cursor"))

        # Apply all non-popped options to frame
        self.viewPort.configure(**options)

    def set_document(self):
        """Placeholder is called when new document is opened"""
        raise NotImplementedError()


# *********************** #
# Collapsable Frame Class #
# *********************** #
class CollapsibleFrame(tk.Frame):
    """A Collapsible Frame Class"""

    def __init__(self, parent, event_handler, *args, **kwargs):
        # == attributes ==
        # state in which the frame starts in
        if "state" in kwargs:
            if kwargs["state"] in ("show", "hide"):
                self.state = kwargs["state"]
            else:
                raise ValueError("Attribute state must be ether show or hide")
            kwargs.pop("state")
        else:
            self.state = "show"

        # stores the characters shown on the button
        if "char" in kwargs:
            self.char: tuple = kwargs["char"]
        else:
            self.char = ("<", ">")

        # stores the order of frame and button
        if "alignment" in kwargs:
            if kwargs["alignment"] == "left":
                self.align = ("left", "right")
            elif kwargs["alignment"] == "right":
                self.align = ("right", "left")
            else:
                raise ValueError("Attribute align must be ether left or right")
        else:
            self.align = ("left", "right")

        super().__init__(master=parent, *args, **kwargs)
        self.handler = event_handler
        self.handler.set_funcs("set-document", self.set_document)

        # == Components ==
        # -- declare components of the widget --
        self.frame = tk.Frame(master=self)
        self._hideButton = tk.Button(
            master=self, text=self.char[0], padx=1, command=self._hide
        )

        # -- display components --
        self._hideButton.pack(fill="y", side=self.align[1])
        if self.state == "show":
            self._show()
        else:
            self._hide()

    def set_document(self):
        """Placeholder is called when new document is opened"""
        raise NotImplementedError()

    def _hide(self) -> None:
        """Hide content expects the button"""
        if self.handler.check_value(hook=str(self) + "-hide"):
            self.handler.call(hook=str(self) + "-hide", value_hook=str(self) + "-hide")
        self.frame.pack_forget()
        self._hideButton.config(text=self.char[1], command=self._show)

    def _show(self) -> None:
        """Reshow content"""
        if self.handler.check_value(hook=str(self) + "-show"):
            self.handler.call(hook=str(self) + "-show", value_hook=str(self) + "-show")
        # self.handler.check(hook=str(self) + "-show")
        self.frame.pack(fill="both", side=self.align[0])
        self._hideButton.config(text=self.char[0], command=self._hide)


# ************************ #
#  Scrollable Frame Class  #
# ************************ #
class PageViewer(ScrollFrame):
    """Scrollable Frame to display pages of a pdf document"""

    def __init__(self, parent, *args, **kwargs):
        self.page_label = []

        if "column" in kwargs:
            self.column = kwargs["column"]
            kwargs.pop("column")
        else:
            self.column = 1

        # constants
        self._scaling = 1
        self.canvas_width = 0
        self.canvas_height = 0
        self.offset_vertical = 10
        self.offset_horizontal = 10

        super().__init__(parent, *args, **kwargs)
        self.pages = []
        self.handler.add_funcs("set-document", self.set_document)

    @property
    def scaling(self):
        """Placeholder for calculated scaling implementations"""
        return self._scaling

    def set_document(self):
        """Fetches the new opened document"""
        self.pages = self.handler.get_values("document")
        self.load_pages()

    def load_pages(self) -> None:
        """Displays all pages of the document vertically"""

        if len(self.pages) == 0:
            return None

        # clear viewPort frame
        self.clear()

        # get page viewer properties
        self.get_properties()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            imgs = executor.map(
                self.convert_page,
                self.pages,
                itertools.repeat(self.scaling, times=len(self.pages)),
            )

        for index, img in enumerate(imgs):
            # convert to a displayable tk-image
            tkImg = ImageTk.PhotoImage(img)

            labelImg = self.blit_page(tkImg, index)

            # append label to pages to later display whether its selected
            self.page_label.append(labelImg)
        return None

    # def update_vision(self):
    #     current = int(
    #        self.canvas.yview()[1] * (len(self.page_label) // self.column + 1) * self.column
    #     )
    #     if self.current != current:
    #         self.update_pages(self.document)
    #         self.current = current

    def update_pages(self):
        """Recreate images and blit it on existing labels"""
        document = self.handler.get_values("document")
        self.get_properties()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            imgs = executor.map(
                self.convert_page,
                document,
                itertools.repeat(self.scaling, times=len(document)),
            )

        for index, img in enumerate(imgs):  # , start=self.current):
            # convert to a displayable tk-image
            tkImg = ImageTk.PhotoImage(img)

            self.page_label[index].config(image=tkImg)
            self.page_label[index].image = tkImg

    def convert_page(self, page, scaling):
        """Covert a given page object to a displayable Image and resize it"""
        pix = page.get_pixmap()

        # set the mode depending on alpha
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # rescale image to fit in the frame
        if self.column == 1:
            scale = (self.canvas_height - self.offset_horizontal) / img.size[1]
        else:
            scale = (
                (self.canvas_width - self.offset_horizontal) / self.column
            ) / img.size[0]

        scale *= scaling

        scaleImg = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

        return scaleImg

    def blit_page(self, page, index):
        """Blit given Image on label and returns it"""
        labelImg = tk.Label(
            master=self.viewPort,
            image=page,
            compound="top",
            padx=3,
        )
        labelImg.image = page
        labelImg.id = index

        # place label in frame
        if self.column == 1:
            labelImg.pack(pady=5, padx=7)
        else:
            labelImg.grid(
                row=index // self.column,
                column=index % self.column,
                pady=5,
                padx=5,
            )

        return labelImg

    def get_properties(self):
        """Function setting editor properties later used to scale the pages"""
        # get page viewer properties
        self.canvas.update()
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        # get width and height of the scrollbar to later calculate the offset
        # also subtract 10 for padding between pages
        if (
            self.yscrollbar.winfo_ismapped()
        ):  # test if a vertical scrollbar is displayed
            self.offset_horizontal = self.yscrollbar.winfo_width() + 10
        if (
            self.xscrollbar.winfo_ismapped()
        ):  # test if a horizontal scrollbar is displayed
            self.offset_vertical = self.xscrollbar.winfo_height() + 10

    def clear(self) -> None:
        """Removes all widget within the frame"""
        for widget in self.viewPort.winfo_children():
            widget.destroy()
        self.page_label.clear()


if __name__ == "__main__":
    from app import EventHandler

    handler = EventHandler()

    root = tk.Tk()
    root.title("test scrollbar frame")

    toolbarPanel = tk.PanedWindow(master=root, orient=tk.HORIZONTAL)
    toolbarPanel.pack(expand=True, fill="both")

    frame = ScrollFrame(parent=toolbarPanel, event_handler=handler)
    toolbarPanel.add(frame)

    label = tk.Label(master=toolbarPanel, text="This is a Label")
    toolbarPanel.add(label)

    for i in range(50):
        print(frame.viewPort.winfo_width())
        tk.Label(master=frame.viewPort, text=f"Label with number: {i}").pack()

    root.mainloop()
