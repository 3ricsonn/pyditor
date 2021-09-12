import tkinter as tk
from tkinter.filedialog import askopenfilename
import fitz  # PyMuPDF

from widgets import CollapsibleFrame
from components import PageViewer


class PyditorApplication(tk.Frame):
    """The Main Application Class bundling all the Components"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # == Attributes ==
        self.parent = parent
        self.sashpos = [(190, 1), (1150, 1)]

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
        self.pageViewerFrame: CollapsibleFrame = None
        self.pageViewer: PageViewer = None

        # -- document editor --
        self.editorFrame: tk.Frame = None
        self.pageEditor: PageViewer = None

        # -- selection viewer --
        self.selectionViewerFrame: CollapsibleFrame = None

        # create placeholder document
        self.PDFDocument: fitz.Document = fitz.Document()

    def load_components(self) -> None:
        """Load the components for page-viewer"""

        # == toolbar ==
        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        # == page viewer ==
        # collapsible Frame as widget container
        self.pageViewerFrame = CollapsibleFrame(parent=self.bodyPanel)
        self.pageViewerFrame.func_hide = lambda: self._hide(index=0, newpos=20)
        self.pageViewerFrame.func_show = lambda: self._show(index=0)
        self.bodyPanel.add(self.pageViewerFrame)

        # Scrollable Frame to display pages of the document
        self.pageViewer = PageViewer(parent=self.pageViewerFrame.frame)
        self.pageViewer.pack(fill="both", expand=True)

        # == main document editor ==
        # Frame as widget container
        self.editorFrame = tk.Frame(master=self.bodyPanel, bg="green")
        self.bodyPanel.add(self.editorFrame)

        # Scrollable Frame to display and edit pages of the document
        self.pageEditor = PageViewer(parent=self.editorFrame, column=2)
        self.pageEditor.pack(fill="both", expand=True)

        # == selection viewer ==
        # collapsible Frame as widget container
        self.selectionViewerFrame = CollapsibleFrame(parent=self.bodyPanel, char=(">", "<"), align="right")
        self.selectionViewerFrame.func_hide = lambda: self._hide(index=1, newpos=1330)
        self.selectionViewerFrame.func_show = lambda: self._show(index=1)
        self.bodyPanel.add(self.selectionViewerFrame)

        # set sashes
        self.bodyPanel.update()
        for i, pos in enumerate(self.sashpos):
            self.bodyPanel.sash_place(i, *pos)

        # load document content if opened
        if self.PDFDocument:
            self.pageViewer.load_pages(document=self.PDFDocument)

    def _hide(self, index: int, newpos: int):
        """Function called when collapsible frame hides to relocate sash on newpos"""
        self.sashpos[index] = self.bodyPanel.sash_coord(index)
        self.bodyPanel.sash_place(index, newpos, 1)

    def _show(self, index: int):
        """Function called when collapsible frame shows to relocate sash"""
        self.bodyPanel.sash_place(index, *self.sashpos[index])

    def open_file(self):
        """Opens a filedialog and convert selected pdf-file to a 'fitz.Document'"""
        pdf_file = askopenfilename(
            title="Choose your PDF you want to edit:",
            filetypes=[("PDF-Files", "*.pdf")],
        )

        if pdf_file:
            self.PDFDocument = fitz.Document(pdf_file)

            self.pageViewer.load_pages(document=self.PDFDocument)

            # rename title with according file path
            self.parent.title("Pyditor - editing: " + pdf_file)

    def save_file(self):
        """Saves the edited pdf file using the metadata title as name"""

    def save_file_name(self):
        """Saves the edited pdf-file asking for a name"""


def print_sash_pos():
    """Print position of sashes for debugging"""
    print(f"1.: {app.toolbarPanel.sash_coord(0)}")
    print(f"2.: {app.toolbarPanel.sash_coord(1)}")


if __name__ == "__main__":
    # create the window and do basic configuration
    rootWindow = tk.Tk()
    rootWindow.title("Pyditor - edit PDFs")
    rootWindow.geometry("1350x1300")

    # creating and packing the Main Application
    app = PyditorApplication(rootWindow)
    app.pack(fill="both", expand=True)
    app.load_components()

    # == creating menus ==
    # the main menu
    mainMenu = tk.Menu(master=rootWindow)
    rootWindow.config(menu=mainMenu)

    # creating menu taps
    # file-menu
    fileMenu = tk.Menu(master=mainMenu)
    mainMenu.add_cascade(label="File", menu=fileMenu)
    fileMenu.add_command(label="Open", command=app.open_file)
    fileMenu.add_command(label="Save", command=app.save_file)
    fileMenu.add_command(label="Save as...", command=app.save_file_name)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", command=rootWindow.quit)

    # debugging
    debug = tk.Menu(master=rootWindow)
    mainMenu.add_cascade(label="debug", menu=debug)
    debug.add_command(label="sash", command=print_sash_pos)

    # run the windows mainloop
    try:
        rootWindow.mainloop()
    finally:
        app.PDFDocument.close()
