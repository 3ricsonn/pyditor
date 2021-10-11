import re
import tkinter as tk

import fitz  # PyMuPDF
from PIL import Image

from widgets import PageViewer

__all__ = ["SidePageViewer", "PagesEditor"]


class SidePageViewer(PageViewer):
    """Scrollable Frame to display and select a single page of a pdf document"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # related page viewer to display selected page
        self._related: PagesEditor = None

    def add_page_viewer_relation(self, widget: PageViewer):
        """Add page viewer to be able to jump to a selected page"""
        self._related = widget

    def load_pages(self, document: fitz.Document) -> None:
        """Displays all pages of the document vertically"""
        super().load_pages(document)

        for i, label in enumerate(self.pages, 1):
            # add title to page
            label.config(text=f"Page {i}")

            # bind an event whenever a page is clicked to select it
            label.bind("<Button-1>", func=self.select_page)

    def convert_page(self, page, scaling):
        """Covert a given page object to a displayable Image and resize it"""
        pix = page.get_pixmap()

        # set the mode depending on alpha
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # rescale image to fit in the frame
        scale = (((self.frame_width - 16) / self.column) / img.size[0]) * scaling

        scaleImg = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

        return scaleImg

    def clear_selection(self) -> None:
        """Remove selected pages from selection and reset page background"""
        for widget in self.viewPort.winfo_children():
            widget.config(bg="#cecfd0")

    def select_page(self, event: tk.Event) -> None:
        """Select page"""
        self.clear_selection()

        event.widget.config(bg="blue")

        # jump with added page viewer to selected page
        if self._related:
            self._related.jump_to_page(event.widget.id - 1)


class PagesEditor(PageViewer):
    def __init__(self, parent, *args, **kwargs):
        if "scale" in kwargs:
            if type(kwargs["scale"]) == tk.StringVar or re.match("^[0-9]{1,3}%$", kwargs["scale"]):
                self.scale = kwargs["scale"]
            else:
                ValueError(
                    "Argument scale must be ether a Stringvar or "
                    "a string indicating the percentage to scale the image"
                )
            kwargs.pop("scale")

        super().__init__(parent, *args, **kwargs)

    @property
    def scaling(self):
        """Gets the selected scaling and calculate the scaling factor"""
        scale = self.scale.get() if type(self.scale) is tk.StringVar else self.scale
        return int(scale[:-1]) / 100

    def jump_to_page(self, page: int) -> None:  # TODO: jumps not everytime to correct page
        """Jumps with scrollbar to given page"""
        overlap = 1 if self.column >= 2 else 0
        self.canvas.yview_moveto(
            str((page // self.column) / (len(self.pages) // self.column + overlap))
        )
