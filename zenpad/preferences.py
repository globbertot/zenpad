import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, GtkSource, Pango

class PreferencesDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Preferences", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE
        )
        self.parent = parent
        
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_border_width(20)
        
        # Grid for settings
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(10)
        box.add(grid)
        
        # Line Numbers Toggle
        self.line_numbers_check = Gtk.CheckButton(label="Show Line Numbers")
        self.line_numbers_check.set_active(True) # Default
        self.line_numbers_check.connect("toggled", self.on_setting_changed, "line_numbers")
        grid.attach(self.line_numbers_check, 0, 0, 2, 1)

        # Word Wrap Toggle
        self.word_wrap_check = Gtk.CheckButton(label="Word Wrap")
        self.word_wrap_check.set_active(True) # Default
        self.word_wrap_check.connect("toggled", self.on_setting_changed, "word_wrap")
        grid.attach(self.word_wrap_check, 0, 1, 2, 1)

        # Theme Selection
        label_theme = Gtk.Label(label="Theme:")
        label_theme.set_halign(Gtk.Align.START)
        grid.attach(label_theme, 0, 2, 1, 1)
        
        self.theme_combo = Gtk.ComboBoxText()
        self.populate_themes()
        self.theme_combo.connect("changed", self.on_setting_changed, "theme")
        grid.attach(self.theme_combo, 1, 2, 1, 1)

        # Font Selection
        label_font = Gtk.Label(label="Font:")
        label_font.set_halign(Gtk.Align.START)
        grid.attach(label_font, 0, 3, 1, 1)
        
        self.font_button = Gtk.FontButton()
        self.font_button.set_font("Monospace 12")
        self.font_button.connect("font-set", self.on_setting_changed, "font")
        grid.attach(self.font_button, 1, 3, 1, 1)
        
        self.show_all()

    def populate_themes(self):
        manager = GtkSource.StyleSchemeManager.get_default()
        ids = manager.get_scheme_ids()
        for i, scheme_id in enumerate(ids):
            self.theme_combo.append(scheme_id, scheme_id)
            if scheme_id == "classic":
                self.theme_combo.set_active(i)

    def on_setting_changed(self, widget, setting_key):
        # Notify parent window to apply settings
        value = None
        if setting_key == "line_numbers":
            value = self.line_numbers_check.get_active()
        elif setting_key == "word_wrap":
            value = self.word_wrap_check.get_active()
        elif setting_key == "theme":
            value = self.theme_combo.get_active_id()
        elif setting_key == "font":
            value = self.font_button.get_font_name()
            
        self.parent.apply_setting(setting_key, value)
