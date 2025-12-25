import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Gio
from .window import ZenpadWindow

class ZenpadApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.zenpad.editor",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = ZenpadWindow(application=self)
        self.window.present()

def main():
    app = ZenpadApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
