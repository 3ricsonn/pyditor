import re
import tkinter as tk
from tkinter import messagebox

from PIL import Image

from widgets import PageViewer

__all__ = ["SidePageViewer", "SideSelectionViewer", "PagesEditor"]


class OneColumnPageViewer(PageViewer):
    def convert_page(self, page, scaling):
        """Covert a given page object to a displayable Image and resize it"""
        pix = page.get_pixmap()

        # set the mode depending on alpha
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # rescale image to fit in the frame
        # print(f"((({self.canvas_width} - {self.offset_horizontal}) / {self.column}) / {img.size[0]})")
        scale = ((self.canvas_width - self.offset_horizontal) / self.column) / img.size[
            0
        ]
        scale *= scaling

        scaleImg = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))

        return scaleImg


class SidePageViewer(OneColumnPageViewer):
    """Scrollable Frame to display and select a single page of a pdf document"""

    def _leave_frame(self, _event):
        super()._leave_frame(_event)
        self.clear_selection()

    def load_pages(self) -> None:
        """Displays all pages of the document vertically"""
        super().load_pages()

        for i, label in enumerate(self.page_label, 1):
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
        self.handler.call("jump-page", event.widget.id)


class SideSelectionViewer(OneColumnPageViewer):
    """View all selected pages to later past in main document"""

    def __init__(self, parent, *args, **kwargs):
        super(OneColumnPageViewer, self).__init__(parent, *args, **kwargs)

        self.handler.set_funcs("get-selection", self.get_selection)

        # == right-click popup menu ==
        self.popupMenu = tk.Menu(master=self.canvas, tearoff=False)
        self.popupMenu.add_command(label="Remove Page")
        self.popupMenu.add_separator()
        self.popupMenu.add_command(label="Clear", command=self.clear_all)

    def set_document(self):
        """Clears hole selection when a new document is opened"""
        self.clear_all()

    def _enter_frame(self, _event):
        """Bind popup-Menu when mouse enters component"""
        super()._enter_frame(_event)
        self.canvas.bind_all("<Button-3>", self.popup)

    def _leave_frame(self, _event):
        """Unbind popup-Menu when mouse leaves component"""
        super()._leave_frame(_event)
        self.canvas.unbind_all("<Button-3>")

    def popup(self, event):
        """Show popup menu"""
        self.popupMenu.tk_popup(event.x_root, event.y_root)

    def get_selection(self, selection):
        """Gets selection from page editor"""
        sorted(selection)
        for page_num in set(selection):
            self.pages.append(self.handler.get_values("document")[page_num])

        self.load_pages()

    def clear_all(self):
        """Clears all displayed pages"""
        for widget in self.viewPort.winfo_children():
            widget.destroy()

        self.pages.clear()


class PagesEditor(PageViewer):
    """Page editor combinable with a combobox for scaling"""

    def __init__(self, parent, *args, **kwargs):
        # arguments
        if "scale" in kwargs:
            if type(kwargs["scale"]) is tk.StringVar or re.match(
                "^[0-9]{1,3}%$", kwargs["scale"]
            ):
                self.scale = kwargs["scale"]
            else:
                ValueError(
                    "Argument scale must be ether a Stringvar or "
                    "a string indicating the percentage to scale the image"
                )
            kwargs.pop("scale")

        super().__init__(parent, *args, **kwargs)

        # selected pages
        self.handler.add_values("selection", [])
        # self.selection: list = []
        self.last_selected: int = 0

        # == right-click popup menu ==
        self.popupMenu = tk.Menu(master=self.canvas, tearoff=False)
        self.popupMenu.add_command(label="Copy", command=self.copy_selected)
        self.popupMenu.add_command(label="Cut", command=self.cut_selected)
        self.popupMenu.add_command(label="Past", command=self.past_selected)
        self.popupMenu.add_separator()
        self.popupMenu.add_command(label="Undo")
        self.popupMenu.add_command(label="Redo")

    def _enter_frame(self, _event):
        """Bind popup-Menu when mouse enters component"""
        super()._enter_frame(_event)
        self.canvas.bind_all("<Button-3>", self.popup)

    def _leave_frame(self, _event):
        """Unbind popup-Menu when mouse leaves component"""
        super()._leave_frame(_event)
        self.canvas.unbind_all("<Button-3>")

    def popup(self, event):
        """Show popup menu"""
        self.popupMenu.tk_popup(event.x_root, event.y_root)

    def copy_selected(self):
        """Sends selected pages to selection viewer without removing them"""
        # self.handler.print()
        self.handler.call("get-selection", value_hook="selection")

    def cut_selected(self):
        """Sends selected pages to selection viewer and removes them"""
        pass

    def past_selected(self):
        """Gets pages from selection viewer and pastes them into the document"""
        pass

    def load_pages(self) -> None:
        """Binds selection functionality to pages"""
        super().load_pages()

        for page in self.page_label:
            page.bind("<Button-1>", func=self.select_page)
            page.bind("<Control-Button-1>", func=self.select_pages_control)
            page.bind("<Shift-Button-1>", func=self.select_pages_shift)

    def select_page(self, event):
        """Selects page with a single right-click"""
        if event.widget.id in self.handler.get_values("selection"):
            self.clear_selection()
        else:
            self.clear_selection()
            event.widget.config(bg="blue")
            self.last_selected = event.widget.id
            self.handler.get_values("selection").append(event.widget.id)

    def select_pages_control(self, event):
        """Selects multiple pages by holding control"""
        if event.widget.id in self.handler.get_values("selection"):
            event.widget.config(bg="#cecfd0")
            self.handler.get_values("selection").remove(event.widget.id)
        else:
            event.widget.config(bg="blue")
            self.last_selected = event.widget.id

            self.handler.get_values("selection").append(event.widget.id)

    def select_pages_shift(self, event):
        """Selection a range of pages by holding shift and right-clicking start and end"""
        if self.last_selected < event.widget.id:
            start = self.last_selected
            end = event.widget.id
        else:
            start = event.widget.id
            end = self.last_selected

        for widget in self.viewPort.winfo_children()[start : end + 1]:
            widget.config(bg="blue")
            if widget.id != self.last_selected:  # ensures no duplicates
                self.handler.get_values("selection").append(widget.id)

    def clear_selection(self):
        """Removes all pages from selection"""
        for widget in self.viewPort.winfo_children():
            widget.config(bg="#cecfd0")

        self.handler.get_values("selection").clear()

    @property
    def scaling(self):
        """Gets the selected scaling and calculate the scaling factor"""
        scale = self.scale.get() if type(self.scale) is tk.StringVar else self.scale

        if not re.match("^[0-9]{1,3}", scale):
            messagebox.showerror(
                title="Invalid scaling",
                message="You entered an invalid scaling factor. Please make sure you entered a number.",
            )
            return 1

        return int(scale[:-1]) / 100

    def jump_to_page(self, page: int) -> None:
        """Jumps with scrollbar to given page"""
        if_overlap = 1 if len(self.page_label) % self.column != 0 else 0
        self.canvas.yview_moveto(
            str(
                (page // self.column)
                / (len(self.page_label) // self.column + if_overlap)
            )
        )
