import tkinter as tk
from tkinter.filedialog import askopenfilename
import fitz  # PyMuPDF

from viewer_components import MultiplePageViewer, SingleSelectablePV


class PyditorApplication(tk.Frame):
    """The Main Application Class bundling all the Components"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # == divide window in panels ==
        # -- create toolbar panel--
        self.toolbarPanel = tk.PanedWindow(master=self, orient=tk.VERTICAL)
        self.toolbarPanel.pack(expand=True, fill="both")

        # -- create toolbar frame
        self.toolbarFrame = tk.Frame(master=self.toolbarPanel, bg="red")
        self.toolbarPanel.add(self.toolbarFrame)

        # -- create page-viewer panel --
        self.pageViewerPanel = tk.PanedWindow(master=self, orient=tk.HORIZONTAL)
        self.toolbarPanel.add(self.pageViewerPanel)

        # == components definitions ==
        # -- pdf-page-viewer --
        # scrollable Frame to display all pages of a document
        self.leftPageViewer: SingleSelectablePV = None
        # scrollable Frame to display the document each page at a time
        self.mainPageViewer: MultiplePageViewer = None

        # -- pdf-page-editor --

        # create placeholder document
        self.PDFDocument: fitz.Document = fitz.Document()

    def load_components_view(self) -> None:
        """Load the components for page-viewer"""
        self.clear_frame()

        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        self.leftPageViewer = SingleSelectablePV(parent=self.pageViewerPanel)
        self.pageViewerPanel.add(self.leftPageViewer)

        self.mainPageViewer = MultiplePageViewer(parent=self.pageViewerPanel)
        self.pageViewerPanel.add(self.mainPageViewer)

        # add main page viewer to left page viewer to jump to selected page
        self.leftPageViewer.add_page_viewer_relation(self.mainPageViewer)

        self.pageViewerPanel.update()
        self.pageViewerPanel.sash_place(0, 180, 1)

        # display already loaded document
        if self.PDFDocument:
            self.leftPageViewer.update()
            self.leftPageViewer.load_pages(self.PDFDocument)
            self.mainPageViewer.load_pages(self.PDFDocument)

    def load_components_edit(self) -> None:
        """Load the components for page-editor"""
        self.clear_frame()

        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        left = tk.Label(
            master=self.pageViewerPanel, text="selected_page_view", bg="green"
        )
        self.pageViewerPanel.add(left)

        editor = tk.Label(
            master=self.pageViewerPanel, text="page_arrangement_editor", bg="blue"
        )
        self.pageViewerPanel.add(editor)

        self.pageViewerPanel.update()
        self.pageViewerPanel.sash_place(0, 180, 1)

    def clear_frame(self):
        """Removes all widget within the frame"""
        for widget in self.pageViewerPanel.winfo_children():
            widget.destroy()

    def open_file(self):
        """Opens a filedialog and convert selected pdf-file to a 'fitz.Document'"""
        pdf_file = askopenfilename(
            title="Choose your PDF you want to edit:",
            filetypes=[("PDF-Files", "*.pdf")],
        )

        if pdf_file:
            self.PDFDocument = fitz.Document(pdf_file)

            # rename title with according file path
            self.parent.title("Pyditor - editing: " + pdf_file)

            # display file in page viewer
            self.leftPageViewer.clear()
            self.leftPageViewer.load_pages(self.PDFDocument)
            self.mainPageViewer.load_pages(self.PDFDocument)

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
    rootWindow.geometry("1200x1300")

    # creating and packing the Main Application
    app = PyditorApplication(rootWindow)
    app.pack(fill="both", expand=True)
    app.load_components_view()

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

    # editor mode menu
    modeMenu = tk.Menu(master=rootWindow)
    mainMenu.add_cascade(label="Mode", menu=modeMenu)
    modeMenu.add_command(label="Single Page view", command=app.load_components_view)
    modeMenu.add_command(label="Multiple Pages edit", command=app.load_components_edit)

    # debugging
    debug = tk.Menu(master=rootWindow)
    mainMenu.add_cascade(label="debug", menu=debug)
    debug.add_command(label="sash", command=print_sash_pos)

    # run the windows mainloop
    try:
        rootWindow.mainloop()
    finally:
        app.PDFDocument.close()
