import tkinter as tk
import getopt
import sys
import os

from app import PyditorApplication

# Owned
__author__ = "3ricsonn"
__copyright__ = "Copyright 2021, 3ricsonn"
__credits__ = ["3ricsonn"]
__license__ = "GPLv3"
__version__ = "0.0.2"
__maintainer__ = "3ricsonn"
__email__ = "3ricsonn@protonmail.com"
__status__ = "DEV"

# CONSTANTS
DIRNAME: str = os.path.dirname(__file__)
file_path: str = ""


def print_sash_pos():
    """Print position of sashes for debugging"""
    print(f"1.: {app.bodyPanel.sash_coord(0)}")
    print(f"2.: {app.bodyPanel.sash_coord(1)}")


# handling command line commands
opts, _ = getopt.getopt(sys.argv[1:], shortopts="f:", longopts=["version"])
for opt, arg in opts:
    if opt == "-h" or opt == "--help":
        print("""
            Usage: pyditor [OPTIONS] -f file-path

            Options:
                General Options
                    -h, --help          Shows this help text and exit
                    --version           Print program version and exit
                File editing
                    -f                  Start the editor with the given document
            """)
        sys.exit()

    if opt == "-f":
        file_path = os.path.join(DIRNAME, arg.strip())
    elif opt == "--version":
        print(f"Current version: {__version__}, status: {__status__}")
        sys.exit()

# create the window and do basic configuration
rootWindow = tk.Tk()
rootWindow.title("Pyditor - edit PDFs")
rootWindow.geometry("1350x1300")

# creating and packing the Main Application
app = PyditorApplication(rootWindow)
app.pack(fill="both", expand=True)
app.load_components()

# open file via commandline
if file_path != "":
    app.set_document(doc=file_path)

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
    app.exit()
