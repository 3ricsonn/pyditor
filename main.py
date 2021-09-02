import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import fitz

from widgets import ScrollFrame


class MultiplePageViewer(ScrollFrame):
    """Scrollable Frame  to display and select pages of an pdf document"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.pages = []
        self.selection = []

    def load_pages(self, document: fitz.Document) -> None:
        """Displays all pages of the document verticaly"""
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
                raise ValueError("scale == {}".formate(scale))

            scaleImg = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

            # convert to a displayable tk-image
            tkImg = ImageTk.PhotoImage(scaleImg)

            labelImg = tk.Label(
                master=self.viewPort,
                text=f"Page {i}",
                image=tkImg,
                compound="top",
                padx=3,
            )
            labelImg.image = tkImg
            labelImg.pack(pady=5, padx=5)

            # bind an event whenever a page is clicked to select it
            labelImg.bind("<Button-1>", func=self.add_page_to_selection)
            labelImg.bind("<Control-Button-1>", func=self.select_multiple_pages)

            # append label to pages to later display whether its selected
            self.pages.append(labelImg)

    def clear(self) -> None:
        """Removes all widget within the frame"""
        for widget in self.viewPort.winfo_children():
            widget.destroy()

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

        # -- create page-view-bar panel --
        self.pageViewerPanel = tk.PanedWindow(master=self, orient=tk.HORIZONTAL)
        self.toolbarPanel.add(self.pageViewerPanel)

        # == components definitions ==
        # -- pdf-page-viewer --
        self.leftPageViewer: MultiplePageViewer = (
            None  # scrollable Frame displaying the pages of document
        )

        # -- pdf-page-editor --

        # create placeholder document
        self.PDFDocument: fitz.Document = fitz.Document()

    def load_components_view(self) -> None:
        self.clear_frame()

        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        self.leftPageViewer = MultiplePageViewer(parent=self.pageViewbarPanel)
        self.pageViewbarPanel.add(self.leftPageViewer)

        editor = tk.Label(
            master=self.pageViewbarPanel, text="single_page_editor", bg="blue"
        )
        self.pageViewbarPanel.add(editor)

        self.pageViewbarPanel.update()
        self.pageViewbarPanel.sash_place(0, 180, 1)

        # display already loaded document
        if self.PDFDocument:
            self.leftPageView.load_pages(self.PDFDocument)

    def load_components_edit(self):
        self.clear_frame()

        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        left = tk.Label(
            master=self.pageViewbarPanel, text="selected_page_view", bg="green"
        )
        self.pageViewbarPanel.add(left)

        editor = tk.Label(
            master=self.pageViewbarPanel, text="page_arrangement_editor", bg="blue"
        )
        self.pageViewbarPanel.add(editor)

        self.pageViewbarPanel.update()
        self.pageViewbarPanel.sash_place(0, 180, 1)

    def clear_frame(self):
        for widget in self.pageViewbarPanel.winfo_children():
            widget.destroy()

    def open_file(self):
        """Opens a filedialog to select a pdf-file and convert it to a 'fitz.Document'"""
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

    def save_file(self):
        """Saves the edited pdf file using the metadata title as name"""

    def save_file_name(self):
        """Saves the edited pdf-file asking for a name"""


def print_sash_pos():
    print(f"1.: {app.toolbarPanel.sash_coord(0)}")
    print(f"2.: {app.toolbarPanel.sash_coord(1)}")


if __name__ == "__main__":
    # create the window and do basic configuration
    rootWindow = tk.Tk()
    rootWindow.title("Pyditor - edit PDFs")  # TODO: more meaningful name
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
