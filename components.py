import tkinter as tk
from widgets import PageViewer
import fitz  # PyMuPDF

__all__ = [
    "SingleSelectablePV"
]


class SingleSelectablePV(PageViewer):
    """Scrollable Frame to display and select a single page of a pdf document"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # related page viewer to display selected page
        self._related: PageViewer = None

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
            self._related.jump_to_page(int(event.widget["text"].split(" ")[-1]) - 1)
