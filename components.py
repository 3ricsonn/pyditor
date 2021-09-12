import tkinter as tk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

from widgets import ScrollFrame

__all__ = [
    "PageViewer",
]


class PageViewer(ScrollFrame):
    """Scrollable Frame to display pages of a pdf document"""

    def __init__(self, parent, column=1, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pages = []
        self.column = column

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
            scale = ((self.viewPort.winfo_width() - 16) / self.column) / img.size[0]

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
            labelImg.id = i

            # place label in frame
            if self.column == 1:
                labelImg.grid(column=0, row=i - 1, pady=5, padx=5)
            else:
                labelImg.grid(
                    row=(i - 1) // self.column,
                    column=(i - 1) % self.column,
                    pady=5,
                    padx=5,
                )

            # append label to pages to later display whether its selected
            self.pages.append(labelImg)

    def jump_to_page(self, page: int) -> None:
        """Jumps with scrollbar to given page"""
        self.canvas.yview_moveto(str(page / len(self.pages)))

    def clear(self) -> None:
        """Removes all widget within the frame"""
        for widget in self.viewPort.winfo_children():
            widget.destroy()

        self.pages.clear()
