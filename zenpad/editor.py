import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, GtkSource, Pango

class EditorTab(Gtk.ScrolledWindow):
    def __init__(self, search_settings=None):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.buffer = GtkSource.Buffer()
        self.view = GtkSource.View.new_with_buffer(self.buffer)
        
        self.file_path = None
        
        # Search Context
        self.search_context = None
        if search_settings:
            self.search_context = GtkSource.SearchContext.new(self.buffer, search_settings)
            self.search_context.set_highlight(True)
        
        # Default Settings
        self.view.set_show_line_numbers(True)
        self.view.set_auto_indent(True)
        self.view.set_highlight_current_line(True)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # Load Default Theme
        self.set_scheme("tango")

        # Font (Default Monospace)
        font_desc = Pango.FontDescription("Monospace 12")
        self.view.modify_font(font_desc)
        
        self.add(self.view)
        self.show_all()

    def get_text(self):
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        return self.buffer.get_text(start_iter, end_iter, True)

    def set_text(self, text):
        self.buffer.set_text(text)

    def set_scheme(self, scheme_id):
        manager = GtkSource.StyleSchemeManager.get_default()
        scheme = manager.get_scheme(scheme_id)
        if scheme:
            self.buffer.set_style_scheme(scheme)

    def get_cursor_position(self):
        insert = self.buffer.get_insert()
        iter = self.buffer.get_iter_at_mark(insert)
        line = iter.get_line() + 1
        col = iter.get_line_offset() + 1
        return line, col

    def detect_language(self, filename):
        manager = GtkSource.LanguageManager.get_default()
        language = manager.guess_language(filename, None)
        if language:
            self.buffer.set_language(language)
