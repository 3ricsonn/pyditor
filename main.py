import tkinter as tk
from tkinter.filedialog import askopenfilename
import fitz


class PageViewer(tk.Frame):
    pass


class PyditorApplication(tk.Frame):
    """The Main Application Class bundling all the Components"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # == divide window in panels ==
        self.toolbarPanel = tk.PanedWindow(master=self, orient=tk.HORIZONTAL)
        self.toolbarPanel.pack(expand=True, fill="both")
        self.sash1_x = 180
        self.sash2_x = 1050

        self.PDFDocument: fitz.Document = fitz.Document()

    def load_components_view(self):
        self.clear_frame()

        left = tk.Label(master=self.toolbarPanel, text="left_page_viewer", bg="red")
        self.toolbarPanel.add(left)

        editor = tk.Label(master=self.toolbarPanel, text="single_page_editor", bg="blue")
        self.toolbarPanel.add(editor)

        right = tk.Label(master=self.toolbarPanel, text="tools?", bg="green")
        self.toolbarPanel.add(right)

        self.toolbarPanel.update()
        self.toolbarPanel.sash_place(0, 180, 1)
        self.toolbarPanel.sash_place(1, 1050, 1)

    def load_components_edit(self):
        self.clear_frame()

        left = tk.Label(master=self.toolbarPanel, text="left_page_viewer", bg="red")
        self.toolbarPanel.add(left)

        editor = tk.Label(master=self.toolbarPanel, text="page_arrangement_editor", bg="blue")
        self.toolbarPanel.add(editor)

        right = tk.Label(master=self.toolbarPanel, text="tools?", bg="green")
        self.toolbarPanel.add(right)

        self.toolbarPanel.update()
        self.toolbarPanel.sash_place(0, 180, 1)
        self.toolbarPanel.sash_place(1, 1050, 1)

    def clear_frame(self):
        for widget in self.toolbarPanel.winfo_children():
            widget.destroy()

    def open_file(self):
        """opens a filedialog to open the to editing pdf and convert it to a 'fitz.Document'"""
        pdf_file = askopenfilename(title="Choose your PDF you want to edit:", filetypes=[("PDF-Files", "*.pdf")])

        if pdf_file:
            self.PDFDocument = fitz.open(pdf_file)

            self.parent.title("Pyditor - editing: " + pdf_file)


def print_sash_pos():
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
    printSash = debug.add_command(label="sash", command=print_sash_pos)

    # run the windows mainloop
    try:
        rootWindow.mainloop()
    finally:
        app.PDFDocument.close()