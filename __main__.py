#!/bin/python3
# -*- coding: utf-8 -*-
#
# Pyditor – An editor to inspected and rearrange pages of pdf-files
# Copyright (C) 2021  3ricsonn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import getopt
import os
import sys
import tkinter as tk

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
try:
    opts, _ = getopt.getopt(sys.argv[1:], shortopts="f:", longopts=["version", "copyright"])
except getopt.GetoptError:
    print(
        """
    Invalid argument(s)
    For usage information run: pyditor -h | --help
    For version information run: pyditor --version
    """
    )
    sys.exit()

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print(
            """
            Usage: pyditor [OPTIONS] -f file-path

            Options:
                General Options
                    -h, --help          Shows this help text and exit
                    --version           Print program version and exit
                File editing
                    -f                  Start the editor with the given document
            """
        )
        sys.exit()

    elif opt == "-f":
        file_path = os.path.join(DIRNAME, arg.strip())
    elif opt == "--version":
        print(f"Current version: {__version__}, status: {__status__}")
        sys.exit()
    elif opt == "--copyright":
        print("""
        pyditor  Copyright (C) 2021  3ricsonn
        This program comes with ABSOLUTELY NO WARRANTY.
        This is free software, and you are welcome to redistribute it
        under certain conditions; for details please refer to LICENSE.
        """)
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
