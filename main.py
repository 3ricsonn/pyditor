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

        self.PDFDocument: fitz.Document = fitz.Document()

    def open_file(self):
        """opens a filedialog to open the to editing pdf and convert it to a 'fitz.Document'"""
        pdf_file = askopenfilename(title="Choose your PDF you want to edit:", filetypes=[("PDF-Files", "*.pdf")])

        if pdf_file:
            self.PDFDocument = fitz.open(pdf_file)


if __name__ == "__main__":
    # create the window and do basic configuration
    rootWindow = tk.Tk()
    rootWindow.title("Pyditor - edit PDFs")
    rootWindow.geometry("400x400")

    # creating and packing the Main Application
    app = PyditorApplication(rootWindow)
    app.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
    modeMenu.add_command(label="Single Page")
    modeMenu.add_command(label="Multiple Pages")

    # run the windows mainloop
    try:
        rootWindow.mainloop()
    finally:
        app.PDFDocument.close()
