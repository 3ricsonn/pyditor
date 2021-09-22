import platform
import tkinter as tk
import concurrent.futures
import itertools
import fitz  # PyMuPDF
from PIL import Image, ImageTk

from tests import timer

__all__ = ["ScrollFrame", "CollapsibleFrame", "PageViewer"]


# ************************ #
#  Scrollable Frame Class  #
# ************************ #
# (origin: https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01)
class ScrollFrame(tk.Frame):
    """A Scrollable Frame Class"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.viewPort = tk.Frame(
            self.canvas, background="#ffffff"
        )  # place a frame on the canvas, this frame will hold the child widgets
        self.vsb = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )  # place a scrollbar on self
        self.canvas.configure(
            yscrollcommand=self.vsb.set
        )  # attach scrollbar action to scroll of canvas

        # pack scrollbar to right of self
        self.vsb.pack(side="right", fill="y")
        # pack canvas to left of self and expand to fil
        self.canvas.pack(side="left", fill="both", expand=True)
        # add view port frame to canvas
        self.canvas_window = self.canvas.create_window(
            (4, 4), window=self.viewPort, anchor="nw", tags="self.viewPort"
        )

        self.viewPort.bind(
            "<Configure>", self.on_frame_configure
        )  # bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind(
            "<Configure>", self.on_canvas_configure
        )  # bind an event whenever the size of the canvas frame changes.

        self.viewPort.bind(
            "<Enter>", self.on_enter
        )  # bind wheel events when the cursor enters the control
        self.viewPort.bind(
            "<Leave>", self.on_leave
        )  # unbind wheel events when the cursor leaves the control

        # perform an initial stretch on render,
        # otherwise the scroll region has a tiny border until the first resize
        self.on_frame_configure(None)

    def on_frame_configure(self, _unused):
        """Reset the scroll region to encompass the inner frame"""
        # whenever the size of the frame changes, alter the scroll region respectively.
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Reset the canvas window to encompass inner frame when required"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def on_mouse_wheel(self, event):
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

    def on_enter(self, _unused):
        """Bind wheel events when the cursor enters the control"""
        if platform.system() == "Linux":
            self.canvas.bind_all("<Button-4>", self.on_mouse_wheel)
            self.canvas.bind_all("<Button-5>", self.on_mouse_wheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_leave(self, _unused):
        """Unbind wheel events when the cursor leaves the control"""
        if platform.system() == "Linux":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")


# *********************** #
# Collapsable Frame Class #
# *********************** #
class CollapsibleFrame(tk.Frame):
    """A Collapsible Frame Class"""

    def __init__(
            self, parent, state="show", char=("<", ">"), align="left", *args, **kwargs
    ):
        super().__init__(master=parent, *args, **kwargs)

        # == store attributes ==
        # stores the state the frame starts in
        if state in ("show", "hide"):
            self.state = state
        else:
            raise ValueError("Attribute state must be ether show or hide")

        # stores the characters shown on the button
        self.char: tuple = char

        # stores the order of frame and button
        if align == "left":
            self.align = ("left", "right")
        elif align == "right":
            self.align = ("right", "left")
        else:
            raise ValueError("Attribute align must be ether left or right")

        # function called when frame hides
        self._func_hide = lambda: None
        # function called when frame shows
        self._func_show = lambda: None

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

    def bind_hide_func(self, func) -> None:
        """Bind a function when frame hides and calls it"""
        self._func_hide = func
        if self.state == "hide":
            self._func_hide()

    def bind_show_func(self, func) -> None:
        """Bind a function when frame hides and calls it"""
        self._func_show = func
        if self.state == "show":
            self._func_show()

    def _hide(self) -> None:
        """Hide content expects the button"""
        self._func_hide()
        self.frame.pack_forget()
        self._hideButton.config(text=self.char[1], command=self._show)

    def _show(self) -> None:
        """Reshow content"""
        self._func_show()
        self.frame.pack(fill="both", side=self.align[0], expand=True)
        self._hideButton.config(text=self.char[0], command=self._hide)


# ************************ #
#  Scrollable Frame Class  #
# ************************ #
class PageViewer(ScrollFrame):
    """Scrollable Frame to display pages of a pdf document"""

    def __init__(self, parent, column=1, scale="100%", *args, **kwargs):
        self.pages = []
        self.column = column
        self.frame_width = 0
        self.scale = scale

        super().__init__(parent, *args, **kwargs)

    # @timer
    def load_pages(self, document: fitz.Document) -> None:
        """Displays all pages of the document vertically"""
        if len(document) == 0:
            return None

        # clear viewPort frame
        self.clear()
        self.frame_width = self.viewPort.winfo_width()

        scale = self.get_scaling()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            imgs = executor.map(self.convert_page, document, itertools.repeat(scale, times=len(document)))

        for index, img in enumerate(imgs):
            # convert to a displayable tk-image
            tkImg = ImageTk.PhotoImage(img)

            labelImg = self.blit_page(tkImg, index)

            # append label to pages to later display whether its selected
            self.pages.append(labelImg)

        return None

    def blit_page(self, page, index):
        """Blit given Image on label and returns it"""
        labelImg = tk.Label(
            master=self.viewPort,
            image=page,
            compound="top",
            padx=3,
        )
        labelImg.image = page

        # place label in frame
        if self.column == 1:
            labelImg.grid(column=0, row=index, pady=5, padx=5)
        else:
            labelImg.grid(
                row=index // self.column,
                column=index % self.column,
                pady=5,
                padx=5,
            )

        return labelImg

    def get_scaling(self):
        scale = self.scale.get() if type(self.scale) == tk.StringVar else self.scale
        print(int(scale[:-1]) / 100)
        return int(scale[:-1]) / 100

    # def update_vision(self):
    #     current = int(
    #        self.canvas.yview()[1] * (len(self.pages) // self.column + 1) * self.column
    #     )
    #     if self.current != current:
    #         self.load_pages(self.document)
    #         self.current = current

    def update_pages(self, document: fitz.Document):
        """Recreate images and blit it on existing labels"""
        self.frame_width = self.viewPort.winfo_width()

        scale = self.get_scaling()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            imgs = executor.map(self.convert_page, document, itertools.repeat(scale, times=len(document)))

        for index, img in enumerate(imgs):  # , start=self.current):
            # convert to a displayable tk-image
            tkImg = ImageTk.PhotoImage(img)

            self.pages[index].config(image=tkImg)
            self.pages[index].image = tkImg

    def convert_page(self, page, scaling: int):
        """Covert a given page object to a displayable Image and resize it"""
        pix = page.get_pixmap()

        # set the mode depending on alpha
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # rescale image to fit in the frame
        scale = (((self.frame_width - 16) / self.column) / img.size[0]) * scaling

        scaleImg = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

        return scaleImg

    def jump_to_page(self, page: int) -> None:
        """Jumps with scrollbar to given page"""
        overlap = 1 if self.column >= 2 else 0
        self.canvas.yview_moveto(
            str((page // self.column) / (len(self.pages) // self.column + overlap))
        )

    def clear(self) -> None:
        """Removes all widget within the frame"""
        for widget in self.viewPort.winfo_children():
            widget.destroy()
        self.pages.clear()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("test scrollbar frame")

    toolbarPanel = tk.PanedWindow(master=root, orient=tk.HORIZONTAL)
    toolbarPanel.pack(expand=True, fill="both")

    frame = ScrollFrame(parent=toolbarPanel)
    toolbarPanel.add(frame)

    label = tk.Label(master=toolbarPanel, text="This is a Label")
    toolbarPanel.add(label)

    for i in range(50):
        print(frame.viewPort.winfo_width())
        tk.Label(master=frame.viewPort, text=f"Label with number: {i}").pack()

    root.mainloop()
