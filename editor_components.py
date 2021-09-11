import tkinter as tk
import fitz  # PyMuPDF

from viewer_components import MultiplePageViewer

__all__ = ["MultiplePageEditor"]


class MultiplePageEditor(MultiplePageViewer):
    """Class to display all pages and edit their order"""
    def __init__(self, parent, column=1, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, column=column)

        self.selection = []

        # add right-click menu
        self.rightClickMenu = tk.Menu(master=parent, tearoff=0)
        self.rightClickMenu.add_command(label="Cut to selection")
        self.rightClickMenu.add_command(label="Copy to selection")
        self.rightClickMenu.add_command(label="Paste from selection")
        self.rightClickMenu.add_command(label="Delete")

    def load_pages(self, document: fitz.Document) -> None:
        """extend load methode to bind selection events to each page"""
        super().load_pages(document)

        for page in self.pages:
            # bind an event whenever a page is clicked to select it
            page.bind("<Button-1>", func=self.select_page)
            page.bind("<Control-Button-1>", func=self.select_multiple_pages)

            # bind an right-click event
            page.bind("<Button-3>", func=self.popup)

    def popup(self, event):
        """Function to appear a right-click menu"""
        try:
            self.rightClickMenu.tk_popup(x=event.x_root, y=event.y_root)
        finally:
            self.rightClickMenu.grab_release()

    def select_page(self, event: tk.Event) -> None:
        """Select page"""
        self.clear_selection()

        event.widget.config(bg="blue")
        self.selection.append(event.widget.id)

    def select_multiple_pages(self, event: tk.Event) -> None:
        """Add page to selection"""
        event.widget.config(bg="blue")
        self.selection.append(event.widget.id)

    def clear_selection(self) -> None:
        """Remove selected pages from selection and reset page background"""
        for widget in self.viewPort.winfo_children():
            widget.config(bg="#cecfd0")

        self.selection.clear()
