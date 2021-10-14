import sys
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import fitz  # PyMuPDF

from components import SidePageViewer, PagesEditor, SideSelectionViewer
from widgets import CollapsibleFrame

__all__ = ["PyditorApplication"]


class EventHandler:
    __functions = {}
    __values = {}

    def add_funcs(self, hook: str, *func):
        self.__functions[hook] = func

    def add_values(self, hook: str, *args, **kwargs):
        self.__values[hook] = args, kwargs

    def call(self, hook: str, *args, **kwargs):
        result = []
        # try:
        for func in self.__functions[hook]:
            if "value_hook" in kwargs:
                value_hook = kwargs.pop("value_hook")
                args += self.__values[value_hook][0]
                kwargs += self.__values[value_hook][1]
            result.append(func(*args, **kwargs))

            return result if len(result) > 1 else result[0]
        # except KeyError:
        #     raise ValueError("A function with this hook does not exists")

    def get_values(self, hook):
        if len(self.__values[hook][0]) == 0:
            if len(self.__values[hook][1]) == 0:
                return None
            else:
                return self.__values[hook][1]
        elif len(self.__values[hook][0]) == 1:
            if len(self.__values[hook][1]) == 0:
                return self.__values[hook][0][0]
        else:
            if len(self.__values[hook][1]) == 0:
                return self.__values[hook][0]
            else:
                return self.__values[hook]

    def print(self):
        print(self.__values)

    def check(self, hook: str):
        return hook in self.__values


class PyditorApplication(tk.Frame):
    """The Main Application Class bundling all the Components"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # handler for communication between components
        self.handler = EventHandler()

        # create placeholder document
        self.handler.add_values("document", fitz.Document())

        # == Attributes ==
        self.parent = parent
        self.sashpos = [(200, 1)]

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
        self.pageViewerFrame = CollapsibleFrame(parent=self.bodyPanel, event_handler=self.handler)
        self.sidebarTabs = ttk.Notebook(master=self.pageViewerFrame.frame)
        self.pageViewerTab = SidePageViewer(
            parent=self.sidebarTabs, event_handler=self.handler, direction="vertical"
        )
        self.selectionViewerTab = SideSelectionViewer(
            parent=self.sidebarTabs, event_handler=self.handler, direction="vertical"
        )

        # -- document editor --
        self.editorFrame = tk.Frame(master=self.bodyPanel, bg="green")
        self.pageEditor = PagesEditor(
            parent=self.editorFrame, event_handler=self.handler, column=2, scale=self.scaleVar, direction="both"
        )

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

    def __enter__(self):
        self.pack(fill="both", expand=True)
        self.load_components()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Function to clean up and end the application"""
        self.handler.get_values("document").close()

        # save application properties to later restore window how it was while closing
        # with open(".settings.json", "w") as f:
        #     pass

        if exc_type:
            raise exc_value
        else:
            sys.exit(0)

    def load_components(self) -> None:
        """Load the components for page-viewer"""
        # == toolbar ==
        toolbar = tk.Label(master=self.toolbarFrame, text="top_toolbar", bg="red")
        toolbar.pack(pady=10)

        # == page viewer ==
        # collapsible Frame as widget container
        self.bodyPanel.add(self.pageViewerFrame)

        # taps for ether displaying all pages for navigation or the selection
        self.sidebarTabs.pack(fill="both", expand=True)

        # Scrollable Frame to display pages of the document
        self.pageViewerTab.pack(fill="both", expand=True)
        self.sidebarTabs.add(self.pageViewerTab, text="All Pages")

        # Scrollable Frame to display all selected pages
        self.selectionViewerTab.pack(fill="both", expand=True)
        self.sidebarTabs.add(self.selectionViewerTab, text="Selection")

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

        # == Sashes ==
        self.bodyPanel.update()
        for i, pos in enumerate(self.sashpos):
            self.bodyPanel.sash_place(i, *pos)

        # == Bindings ==
        # -- page viewer --
        # bind functions when page viewer shows or hides
        self.handler.add_funcs(str(self.pageViewerFrame)+"-hide", self._hide)
        self.handler.add_values(str(self.pageViewerFrame)+"-hide", index=0, newpos=20)
        # self.pageViewerFrame.bind_hide_func(func=lambda: self._hide(index=0, newpos=20))
        self.handler.add_funcs(str(self.pageViewerFrame)+"-show", self._show)
        self.handler.add_values(str(self.pageViewerFrame)+"-show", index=0)
        # self.handler.print()
        # self.pageViewerFrame.bind_show_func(func=lambda: self._show(index=0))
        # self.pageViewerTab.add_page_viewer_relation(widget=self.pageEditor)

        self.handler.add_funcs("jump-page", self.pageEditor.jump_to_page)

        # bind functions updating pages when scale changed
        self.editorScalingSetting.bind("<<ComboboxSelected>>", self.update_editor)
        self.editorScalingSetting.bind("<Return>", self.update_editor)

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
        self.pageEditor.update_pages()

    def update_column_value(self, selection):
        """Function to change the number of columns the document is displayed"""
        self.scaleVar.set("100%")
        self.pageEditor.column = int(selection[0])
        self.pageEditor.canvas.yview_moveto(0.0)
        self.pageEditor.load_pages()

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
        self.handler.add_values("document", fitz.Document(doc))

        self.pageViewerTab.load_pages()
        self.pageEditor.load_pages()

        # rename title with according file path
        self.parent.title("Pyditor - editing: " + doc)

    def save_file(self):
        """Saves the edited pdf file using the metadata title as name"""

    def save_file_name(self):
        """Saves the edited pdf-file asking for a name"""
