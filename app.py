import sys
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import fitz  # PyMuPDF

from components import SidePageViewer, PagesEditor
from widgets import CollapsibleFrame


class PyditorApplication(tk.Frame):
    """The Main Application Class bundling all the Components"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # == Attributes ==
        self.parent = parent
        self.sashpos = [(190, 1), (1150, 1)]

        # == Variables ==
        # variables for the column settings
        column_nums = ["1 site per row", "2 sites per row", "3 sites per row"]
        start = tk.StringVar()
        start.set(column_nums[1])

        # variables for the scaling settings
        states = [f"{i}%" for i in range(50, 110, 10)] + ["125%", "150%", "200%"]
        self.scaleVar = tk.StringVar()

        # == divide window in panels ==
        # -- create toolbar panel--
        self.toolbarPanel = tk.PanedWindow(master=self, orient=tk.VERTICAL)
        self.toolbarPanel.pack(expand=True, fill="both")

        # -- create toolbar frame
        self.toolbarFrame = tk.Frame(master=self.toolbarPanel, bg="red")
        self.toolbarPanel.add(self.toolbarFrame)

        # -- create application body --
        self.bodyPanel = tk.PanedWindow(master=self.toolbarPanel, orient=tk.HORIZONTAL)
        self.toolbarPanel.add(self.bodyPanel)

        # == components definitions ==
        # -- page viewer --
        self.pageViewerFrame = CollapsibleFrame(parent=self.bodyPanel)
        self.pageViewer = SidePageViewer(parent=self.pageViewerFrame.frame, direction="vertical")

        # -- document editor --
        self.editorFrame = tk.Frame(master=self.bodyPanel, bg="green")
        self.pageEditor = PagesEditor(parent=self.editorFrame, column=2, scale=self.scaleVar, direction="both")

        # frame to store setting widgets
        self.editorSettingsFrame = tk.Frame(master=self.editorFrame, bg="blue")
        self.editorColumnSetting = ttk.OptionMenu(
            self.editorSettingsFrame,
            start,
            column_nums[1],
            *column_nums,
            command=self.update_column_value,
        )

        self.editorScalingSetting = ttk.Combobox(
            master=self.editorSettingsFrame, textvariable=self.scaleVar, values=states
        )

        # -- selection viewer --
        self.selectionViewerFrame = CollapsibleFrame(
            parent=self.bodyPanel, state="hide", char=(">", "<"), align="right"
        )

        # create placeholder document
        self.PDFDocument: fitz.Document = fitz.Document()

    def load_components(self) -> None:
        """Load the components for page-viewer"""
        # == toolbar ==
        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        # == page viewer ==
        # collapsible Frame as widget container
        self.bodyPanel.add(self.pageViewerFrame)

        # Scrollable Frame to display pages of the document
        self.pageViewer.pack(fill="y", expand=True)

        # == main document editor ==
        # Frame as widget container
        self.bodyPanel.add(self.editorFrame)

        # Scrollable Frame to display and edit pages of the document
        self.pageEditor.pack(fill="both", expand=True)

        # frame to store setting widgets
        self.editorSettingsFrame.pack(fill="both")

        # - options -
        # option menu to change the number of columns the document is displayed
        self.editorColumnSetting.config(width=12)
        self.editorColumnSetting.grid(column=0, row=0, padx=5, pady=2)

        # options menu to change the scaling factor
        self.editorScalingSetting.grid(row=0, column=1, padx=5)
        self.editorScalingSetting.current(5)

        # == selection viewer ==
        # collapsible Frame as widget container
        self.bodyPanel.add(self.selectionViewerFrame)

        # == Sashes ==
        self.bodyPanel.update()
        for i, pos in enumerate(self.sashpos):
            self.bodyPanel.sash_place(i, *pos)

        # == Bindings ==
        # -- page viewer --
        # bind functions when page viewer shows or hides
        self.pageViewerFrame.bind_hide_func(func=lambda: self._hide(index=0, newpos=20))
        self.pageViewerFrame.bind_show_func(func=lambda: self._show(index=0))
        self.pageViewer.add_page_viewer_relation(widget=self.pageEditor)

        # bind functions updating pages when scale changed
        self.editorScalingSetting.bind("<<ComboboxSelected>>", self.update_editor)
        self.editorScalingSetting.bind("<Return>", self.update_editor)

        # -- selection viewer --
        # bind functions when selection viewer shows or hides
        self.selectionViewerFrame.bind_hide_func(
            func=lambda: self._hide(index=1, newpos=1330)
        )
        self.selectionViewerFrame.bind_show_func(func=lambda: self._show(index=1))

        # load document content if opened
        if self.PDFDocument:
            self.pageViewer.load_pages(document=self.PDFDocument)
            self.pageEditor.load_pages(document=self.PDFDocument)

    def _hide(self, index: int, newpos: int):
        """Function called when collapsible frame hides to relocate sash on newpos"""
        self.sashpos[index] = self.bodyPanel.sash_coord(index)
        self.bodyPanel.sash_place(index, newpos, 1)
        self.update_editor()

    def _show(self, index: int):
        """Function called when collapsible frame shows to relocate sash"""
        self.bodyPanel.sash_place(index, *self.sashpos[index])
        self.update_editor()

    def update_editor(self, *_):
        """Updates the dimensions of the editor after sash been relocated"""
        self.bodyPanel.update()
        self.pageEditor.update_pages(self.PDFDocument)

    def update_column_value(self, selection):
        """Function to change the number of columns the document is displayed"""
        self.scaleVar.set("100%")
        self.pageEditor.column = int(selection[0])
        self.pageEditor.canvas.yview_moveto(0.0)
        self.pageEditor.load_pages(self.PDFDocument)

    def open_file(self):
        """Opens a filedialog and convert selected pdf-file to a 'fitz.Document'"""
        pdf_file = askopenfilename(
            title="Choose your PDF you want to edit:",
            filetypes=[("PDF-Files", "*.pdf")],
        )

        if pdf_file:
            self.set_document(pdf_file)

    def set_document(self, doc: str) -> None:
        """Create document from path and load pages onto the viewer-frames"""
        self.PDFDocument = fitz.Document(doc)

        self.pageViewer.load_pages(document=self.PDFDocument)
        self.pageEditor.load_pages(document=self.PDFDocument)

        # rename title with according file path
        self.parent.title("Pyditor - editing: " + doc)

    def save_file(self):
        """Saves the edited pdf file using the metadata title as name"""

    def save_file_name(self):
        """Saves the edited pdf-file asking for a name"""

    def exit(self):
        """Function to clean up and end the application"""
        self.PDFDocument.close()
        sys.exit(1)
