import tkinter as tk
import platform


# ************************
# Scrollable Frame Class
# ************************
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
