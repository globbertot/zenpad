import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SearchDialog(Gtk.Dialog):
    def __init__(self, parent, apply_fn, mode="replace"):
        title = "Find" if mode == "find" else "Find & Replace"
        super().__init__(title=title, transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
        )
        self.apply_fn = apply_fn
        self.mode = mode
        
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_border_width(20)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        box.add(grid)
        
        # Find
        grid.attach(Gtk.Label(label="Find:"), 0, 0, 1, 1)
        self.find_entry = Gtk.Entry()
        grid.attach(self.find_entry, 1, 0, 1, 1)
        
        self.find_entry = Gtk.Entry()
        grid.attach(self.find_entry, 1, 0, 1, 1)
        
        # Replace
        if self.mode == "replace":
            grid.attach(Gtk.Label(label="Replace:"), 0, 1, 1, 1)
            self.replace_entry = Gtk.Entry()
            grid.attach(self.replace_entry, 1, 1, 1, 1)
        
        # Buttons
        btn_box = Gtk.Box(spacing=5)
        
        find_btn = Gtk.Button(label="Find Next")
        find_btn.connect("clicked", self.on_find)
        btn_box.pack_start(find_btn, True, True, 0)
        
        if self.mode == "replace":
            replace_btn = Gtk.Button(label="Replace")
            replace_btn.connect("clicked", self.on_replace)
            btn_box.pack_start(replace_btn, True, True, 0)

            replace_all_btn = Gtk.Button(label="Replace All")
            replace_all_btn.connect("clicked", self.on_replace_all)
            btn_box.pack_start(replace_all_btn, True, True, 0)
        
        grid.attach(btn_box, 0, 2, 2, 1)
        
        self.show_all()

    def on_find(self, widget):
        text = self.find_entry.get_text()
        if text:
            self.apply_fn("find", text, None)

    def on_replace(self, widget):
        find_text = self.find_entry.get_text()
        replace_text = self.replace_entry.get_text()
        if find_text:
            self.apply_fn("replace", find_text, replace_text)

    def on_replace_all(self, widget):
        find_text = self.find_entry.get_text()
        replace_text = self.replace_entry.get_text()
        if find_text:
            self.apply_fn("replace_all", find_text, replace_text)
