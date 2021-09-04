import tkinter as tk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

from widgets import ScrollFrame


class MultiplePageViewer(ScrollFrame):
    """Scrollable Frame to display pages of a pdf document"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pages = []

    def load_pages(self, document: fitz.Document) -> None:
        """Displays all pages of the document vertically"""
        # clear viewPort frame
        self.clear()

        for i, page in enumerate(document, start=1):
            pix = page.get_pixmap()

            # set the mode depending on alpha
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

            # rescale image to fit in the frame
            scale = (self.viewPort.winfo_width() - 16) / img.size[0]
            if scale <= 0:
                raise ValueError("scale == {}".format(scale))

            scaleImg = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

            # convert to a displayable tk-image
            tkImg = ImageTk.PhotoImage(scaleImg)

            labelImg = tk.Label(
                master=self.viewPort,
                image=tkImg,
                compound="top",
                padx=3,
            )
            labelImg.image = tkImg
            labelImg.pack(pady=5, padx=5)

            # append label to pages to later display whether its selected
            self.pages.append(labelImg)

    def jump_to_page(self, page: int) -> None:
        """Jumps with scrollbar to given page"""
        self.canvas.yview_moveto(str(page/len(self.pages)))

    def clear(self) -> None:
        """Removes all widget within the frame"""
        for widget in self.viewPort.winfo_children():
            widget.destroy()


class SingleSelectablePV(MultiplePageViewer):
    """Scrollable Frame to display and select a single page of a pdf document"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # related page viewer to display selected page
        self.related: MultiplePageViewer = None

    def add_page_viewer_relation(self, widget: MultiplePageViewer):
        self.related = widget

    def load_pages(self, document: fitz.Document) -> None:
        super().load_pages(document)

        for i, label in enumerate(self.pages, 1):
            # add title to page
            label.config(text=f"Page {i}")

            # bind an event whenever a page is clicked to select it
            label.bind("<Button-1>", func=self.select_page)

    def clear_selection(self) -> None:
        """Remove selected pages from selection and reset page background"""
        for widget in self.viewPort.winfo_children():
            widget.config(bg="#cecfd0")

    def select_page(self, event: tk.Event) -> None:
        """Select page"""
        self.clear_selection()

        event.widget.config(bg="blue")
        
        # jump with main page viewer to selected page
        if self.related:
            self.related.jump_to_page(int(event.widget["text"].split(" ")[-1])-1)


class MultibleSelectablePV(MultiplePageViewer):
    """Scrollable Frame to display and select multiple pages of a pdf document"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selection = []

    def load_pages(self, document: fitz.Document) -> None:
        super().load_pages(document)

        for i, label in enumerate(self.pages, 1):
            # add title to page
            label.config(text=f"Page {i}")

            # bind an event whenever a page is clicked to select it
            label.bind("<Button-1>", func=self.select_page)
            label.bind("<Control-Button-1>", func=self.select_multiple_pages)

    def clear_selection(self) -> None:
        """Remove selected pages from selection and reset page background"""
        for widget in self.viewPort.winfo_children():
            widget.config(bg="#cecfd0")

        self.selection.clear()

    def select_page(self, event: tk.Event) -> None:
        """Select page"""
        self.clear_selection()

        event.widget.config(bg="blue")
        self.selection.append(event.widget["text"])

    def select_multiple_pages(self, event: tk.Event) -> None:
        """Add page to selection"""
        event.widget.config(bg="blue")
        self.selection.append(event.widget["text"])
