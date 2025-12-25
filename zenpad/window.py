from gi.repository import Gtk, Pango, Gdk, Gio
import os
import json
from .editor import EditorTab
from .preferences import PreferencesDialog
from gi.repository import GtkSource

class ZenpadWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Zenpad")
        self.set_default_size(800, 600)
        self.set_default_size(800, 600)
        self.connect("delete-event", self.save_session)
        
        # Accelerator Group
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        
        # 0. Header Bar (For Window Controls Only - CSD)
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Zenpad"
        header.props.decoration_layout = ":minimize,maximize,close"
        self.set_titlebar(header)
        
        # Main Layout Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)

        # 1. Menu Bar
        menubar = self.create_menubar()
        main_box.pack_start(menubar, False, False, 0)
        
        # 2. Toolbar
        toolbar = self.create_toolbar()
        main_box.pack_start(toolbar, False, False, 0)

        # 3. Notebook (content)
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch-page", self.on_tab_switched)
        main_box.pack_start(self.notebook, True, True, 0)
        
        # 3.5 Search Bar (Footer)
        self.search_settings = GtkSource.SearchSettings()
        self.search_bar_revealer = Gtk.Revealer()
        self.search_bar_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.create_search_bar()
        main_box.pack_start(self.search_bar_revealer, False, False, 0)

        # 4. Status Bar
        self.statusbar = Gtk.Statusbar()
        main_box.pack_end(self.statusbar, False, True, 0)
        
        # Shortcuts
        self.create_actions()
        
        # Track current signal handler to disconnect later
        self.current_cursor_handler = None
        
        # Load Session or Add initial empty tab
        self.load_session()
        
        self.show_all()

    def create_menubar(self):
        menubar = Gtk.MenuBar()
        
        # File Menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        
        new_item = Gtk.ImageMenuItem(label="New")
        new_item.set_image(Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.MENU))
        new_item.set_always_show_image(True)
        new_item.connect("activate", self.on_new_tab)
        file_menu.append(new_item)

        new_window_item = Gtk.ImageMenuItem(label="New Window")
        new_window_item.set_image(Gtk.Image.new_from_icon_name("window-new", Gtk.IconSize.MENU))
        new_window_item.set_always_show_image(True)
        new_window_item.connect("activate", self.on_new_window)
        file_menu.append(new_window_item)
        
        # Open
        open_item = Gtk.ImageMenuItem(label="Open...")
        open_item.set_image(Gtk.Image.new_from_icon_name("document-open", Gtk.IconSize.MENU))
        open_item.set_always_show_image(True)
        open_item.connect("activate", self.on_open_file)
        file_menu.append(open_item)
        
        # Recent (Placeholder using Gtk.RecentChooserMenu if needed, but keeping simple for now)
        recent_item = Gtk.MenuItem(label="Open Recent")
        recent_menu = Gtk.RecentChooserMenu()
        recent_menu.connect("item-activated", self.on_open_recent)
        recent_item.set_submenu(recent_menu)
        file_menu.append(recent_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Save
        save_item = Gtk.ImageMenuItem(label="Save")
        save_item.set_image(Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.MENU))
        save_item.set_always_show_image(True)
        save_item.connect("activate", self.on_save_file)
        file_menu.append(save_item)
        
        save_as_item = Gtk.ImageMenuItem(label="Save As...")
        save_as_item.set_image(Gtk.Image.new_from_icon_name("document-save-as", Gtk.IconSize.MENU))
        save_as_item.set_always_show_image(True)
        save_as_item.connect("activate", self.on_save_as)
        file_menu.append(save_as_item)

        save_all_item = Gtk.ImageMenuItem(label="Save All")
        save_all_item.set_image(Gtk.Image.new_from_icon_name("document-save-all", Gtk.IconSize.MENU))
        save_all_item.set_always_show_image(True)
        save_all_item.connect("activate", self.on_save_all)
        file_menu.append(save_all_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Reload
        reload_item = Gtk.ImageMenuItem(label="Reload")
        reload_item.set_image(Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.MENU))
        reload_item.set_always_show_image(True)
        reload_item.connect("activate", self.on_reload)
        file_menu.append(reload_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())

        # Print
        print_item = Gtk.ImageMenuItem(label="Print...")
        print_item.set_image(Gtk.Image.new_from_icon_name("document-print", Gtk.IconSize.MENU))
        print_item.set_always_show_image(True)
        print_item.connect("activate", self.on_print)
        file_menu.append(print_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())

        # Detach Tab
        detach_item = Gtk.MenuItem(label="Detach Tab")
        detach_item.connect("activate", self.on_detach_tab)
        file_menu.append(detach_item)
        
        # Close Tab
        close_tab_item = Gtk.ImageMenuItem(label="Close Tab")
        close_tab_item.set_image(Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.MENU))
        close_tab_item.set_always_show_image(True)
        close_tab_item.connect("activate", self.on_close_current_tab)
        file_menu.append(close_tab_item)
        
        # Close Window
        close_win_item = Gtk.MenuItem(label="Close Window")
        close_win_item.connect("activate", lambda w: self.close())
        file_menu.append(close_win_item)
        
        quit_item = Gtk.ImageMenuItem(label="Quit")
        quit_item.set_image(Gtk.Image.new_from_icon_name("application-exit", Gtk.IconSize.MENU))
        quit_item.set_always_show_image(True)
        quit_item.connect("activate", lambda w: self.close()) # Quit app?
        file_menu.append(quit_item)
        
        menubar.append(file_item)
        
        # Edit Menu
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.set_submenu(edit_menu)

        # Undo/Redo
        undo_item = Gtk.ImageMenuItem(label="Undo")
        undo_item.set_image(Gtk.Image.new_from_icon_name("edit-undo", Gtk.IconSize.MENU))
        undo_item.set_always_show_image(True)
        undo_item.connect("activate", self.on_undo)
        undo_item.add_accelerator("activate", self.accel_group, Gdk.KEY_z, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(undo_item)

        redo_item = Gtk.ImageMenuItem(label="Redo")
        redo_item.set_image(Gtk.Image.new_from_icon_name("edit-redo", Gtk.IconSize.MENU))
        redo_item.set_always_show_image(True)
        redo_item.connect("activate", self.on_redo)
        redo_item.add_accelerator("activate", self.accel_group, Gdk.KEY_y, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(redo_item)

        edit_menu.append(Gtk.SeparatorMenuItem())

        # Cut/Copy/Paste
        cut_item = Gtk.ImageMenuItem(label="Cut")
        cut_item.set_image(Gtk.Image.new_from_icon_name("edit-cut", Gtk.IconSize.MENU))
        cut_item.set_always_show_image(True)
        cut_item.connect("activate", self.on_cut)
        cut_item.add_accelerator("activate", self.accel_group, Gdk.KEY_x, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(cut_item)

        copy_item = Gtk.ImageMenuItem(label="Copy")
        copy_item.set_image(Gtk.Image.new_from_icon_name("edit-copy", Gtk.IconSize.MENU))
        copy_item.set_always_show_image(True)
        copy_item.connect("activate", self.on_copy)
        copy_item.add_accelerator("activate", self.accel_group, Gdk.KEY_c, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(copy_item)
        
        paste_item = Gtk.ImageMenuItem(label="Paste")
        paste_item.set_image(Gtk.Image.new_from_icon_name("edit-paste", Gtk.IconSize.MENU))
        paste_item.set_always_show_image(True)
        paste_item.connect("activate", self.on_paste)
        paste_item.add_accelerator("activate", self.accel_group, Gdk.KEY_v, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(paste_item)

        # Delete Selection/Line
        del_item = Gtk.MenuItem(label="Delete Selection")
        del_item.connect("activate", self.on_delete_selection)
        del_item.add_accelerator("activate", self.accel_group, Gdk.KEY_Delete, 0, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(del_item)

        del_line_item = Gtk.MenuItem(label="Delete Line")
        del_line_item.connect("activate", self.on_delete_line)
        del_line_item.add_accelerator("activate", self.accel_group, Gdk.KEY_Delete, Gdk.ModifierType.SHIFT_MASK | Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(del_line_item)

        edit_menu.append(Gtk.SeparatorMenuItem())

        # Select All
        sel_all_item = Gtk.ImageMenuItem(label="Select All")
        sel_all_item.set_image(Gtk.Image.new_from_icon_name("edit-select-all", Gtk.IconSize.MENU))
        sel_all_item.set_always_show_image(True)
        sel_all_item.connect("activate", self.on_select_all)
        sel_all_item.add_accelerator("activate", self.accel_group, Gdk.KEY_a, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(sel_all_item)

        # Convert
        convert_item = Gtk.MenuItem(label="Convert")
        convert_menu = Gtk.Menu()
        convert_item.set_submenu(convert_menu)
        
        to_upper = Gtk.MenuItem(label="To Uppercase")
        to_upper.connect("activate", lambda w: self.on_change_case("upper"))
        convert_menu.append(to_upper)
        
        to_lower = Gtk.MenuItem(label="To Lowercase")
        to_lower.connect("activate", lambda w: self.on_change_case("lower"))
        convert_menu.append(to_lower)
        
        to_title = Gtk.MenuItem(label="To Title Case")
        to_title.connect("activate", lambda w: self.on_change_case("title"))
        convert_menu.append(to_title)

        edit_menu.append(convert_item)

        # Move
        move_item = Gtk.MenuItem(label="Move")
        move_menu = Gtk.Menu()
        move_item.set_submenu(move_menu)

        move_up = Gtk.MenuItem(label="Line Up")
        move_up.connect("activate", lambda w: self.on_move_line("up"))
        move_up.add_accelerator("activate", self.accel_group, Gdk.KEY_Up, Gdk.ModifierType.MOD1_MASK, Gtk.AccelFlags.VISIBLE) # Alt+Up
        move_menu.append(move_up)

        move_down = Gtk.MenuItem(label="Line Down")
        move_down.connect("activate", lambda w: self.on_move_line("down"))
        move_down.add_accelerator("activate", self.accel_group, Gdk.KEY_Down, Gdk.ModifierType.MOD1_MASK, Gtk.AccelFlags.VISIBLE) # Alt+Down
        move_menu.append(move_down)
        
        edit_menu.append(move_item)

        # Duplicate
        dup_item = Gtk.MenuItem(label="Duplicate Line / Selection")
        dup_item.connect("activate", self.on_duplicate)
        edit_menu.append(dup_item)

        # Indent
        indent_inc = Gtk.MenuItem(label="Increase Indent")
        indent_inc.connect("activate", lambda w: self.on_indent(True))
        indent_inc.add_accelerator("activate", self.accel_group, Gdk.KEY_i, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(indent_inc)

        indent_dec = Gtk.MenuItem(label="Decrease Indent")
        indent_dec.connect("activate", lambda w: self.on_indent(False))
        indent_dec.add_accelerator("activate", self.accel_group, Gdk.KEY_u, Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(indent_dec)

        edit_menu.append(Gtk.SeparatorMenuItem())
        
        pref_item = Gtk.ImageMenuItem(label="Preferences...")
        pref_item.set_image(Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.MENU))
        pref_item.set_always_show_image(True)
        pref_item.connect("activate", self.on_preferences_clicked)
        edit_menu.append(pref_item)
        
        menubar.append(edit_item)
        
        # Search Menu
        search_menu = Gtk.Menu()
        search_item = Gtk.MenuItem(label="Search")
        search_item.set_submenu(search_menu)
        
        find_item = Gtk.MenuItem(label="Find...")
        find_item.connect("activate", lambda w: self.on_find_clicked("find"))
        search_menu.append(find_item)

        replace_item = Gtk.MenuItem(label="Find & Replace...")
        replace_item.connect("activate", lambda w: self.on_find_clicked("replace"))
        search_menu.append(replace_item)
        
        menubar.append(search_item)
        
        # Help Menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)
        
        about_item = Gtk.ImageMenuItem(label="About")
        about_item.set_image(Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.MENU))
        about_item.set_always_show_image(True)
        about_item.connect("activate", self.on_about)
        help_menu.append(about_item)
        
        menubar.append(help_item)
        
        return menubar

    def create_toolbar(self):
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.ICONS)
        toolbar.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        
        # New
        new_btn = Gtk.ToolButton()
        new_btn.set_icon_name("document-new")
        new_btn.set_tooltip_text("New File")
        new_btn.connect("clicked", self.on_new_tab)
        toolbar.insert(new_btn, -1)
        
        # Open
        open_btn = Gtk.ToolButton()
        open_btn.set_icon_name("document-open")
        open_btn.set_tooltip_text("Open File")
        open_btn.connect("clicked", self.on_open_file)
        toolbar.insert(open_btn, -1)
        
        # Save
        save_btn = Gtk.ToolButton()
        save_btn.set_icon_name("document-save")
        save_btn.set_tooltip_text("Save File")
        save_btn.connect("clicked", self.on_save_file)
        toolbar.insert(save_btn, -1)
        
        toolbar.insert(Gtk.SeparatorToolItem(), -1)
        
        # Undo/Redo (Placeholder icons for visual parity)
        undo_btn = Gtk.ToolButton()
        undo_btn.set_icon_name("edit-undo")
        undo_btn.set_tooltip_text("Undo")
        toolbar.insert(undo_btn, -1)
        
        redo_btn = Gtk.ToolButton()
        redo_btn.set_icon_name("edit-redo")
        redo_btn.set_tooltip_text("Redo")
        toolbar.insert(redo_btn, -1)
        
        toolbar.insert(Gtk.SeparatorToolItem(), -1)
        
        # Cut/Copy/Paste
        cut_btn = Gtk.ToolButton()
        cut_btn.set_icon_name("edit-cut")
        cut_btn.set_tooltip_text("Cut")
        cut_btn.connect("clicked", self.on_cut)
        toolbar.insert(cut_btn, -1)
        
        copy_btn = Gtk.ToolButton()
        copy_btn.set_icon_name("edit-copy")
        copy_btn.set_tooltip_text("Copy")
        copy_btn.connect("clicked", self.on_copy)
        toolbar.insert(copy_btn, -1)
        
        paste_btn = Gtk.ToolButton()
        paste_btn.set_icon_name("edit-paste")
        paste_btn.set_tooltip_text("Paste")
        paste_btn.connect("clicked", self.on_paste)
        toolbar.insert(paste_btn, -1)
        
        toolbar.insert(Gtk.SeparatorToolItem(), -1)

        # Find
        find_btn = Gtk.ToolButton()
        find_btn.set_icon_name("edit-find")
        find_btn.set_tooltip_text("Find")
        find_btn.connect("clicked", lambda w: self.on_find_clicked("find"))
        toolbar.insert(find_btn, -1)
        
        return toolbar

    def create_search_bar(self):
        self.search_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.search_box.set_spacing(0)
        
        # Row 1: Find
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row1.set_spacing(5)
        row1.set_border_width(5)
        
        # Close Button
        close_btn = Gtk.Button.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.connect("clicked", lambda w: self.search_bar_revealer.set_reveal_child(False))
        row1.pack_start(close_btn, False, False, 0)
        
        # Search Entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_width_chars(30)
        self.search_entry.connect("search-changed", self.on_search_text_changed)
        self.search_entry.connect("activate", lambda w: self.on_search_next(w))
        row1.pack_start(self.search_entry, False, False, 0)
        
        # Match Count Label
        self.match_count_label = Gtk.Label()
        self.match_count_label.set_margin_start(5)
        self.match_count_label.set_margin_end(5)
        row1.pack_start(self.match_count_label, False, False, 0)
        
        # Navigation
        prev_btn = Gtk.Button.new_from_icon_name("go-up-symbolic", Gtk.IconSize.MENU)
        prev_btn.set_tooltip_text("Find Previous (Shift+F3)")
        prev_btn.connect("clicked", self.on_search_prev)
        row1.pack_start(prev_btn, False, False, 0)
        
        next_btn = Gtk.Button.new_from_icon_name("go-down-symbolic", Gtk.IconSize.MENU)
        next_btn.set_tooltip_text("Find Next (F3)")
        next_btn.connect("clicked", self.on_search_next)
        row1.pack_start(next_btn, False, False, 0)
        
        # Options
        self.match_case_check = Gtk.CheckButton(label="Match case")
        self.match_case_check.connect("toggled", self.on_search_settings_changed)
        row1.pack_start(self.match_case_check, False, False, 5)
        
        self.whole_word_check = Gtk.CheckButton(label="Match whole word")
        self.whole_word_check.connect("toggled", self.on_search_settings_changed)
        row1.pack_start(self.whole_word_check, False, False, 5)
        
        self.regex_check = Gtk.CheckButton(label="Regular expression")
        self.regex_check.connect("toggled", self.on_search_settings_changed)
        row1.pack_start(self.regex_check, False, False, 5)
        
        self.search_box.pack_start(row1, True, True, 0)
        
        # Row 2: Replace (Initially hidden or handled via mode)
        self.replace_revealer = Gtk.Revealer()
        self.replace_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row2.set_spacing(5)
        row2.set_border_width(5)
        
        # Spacer to align with entry
        # A simple label "Replace with:" or similar
        row2.pack_start(Gtk.Label(label="Replace with:"), False, False, 5)
        
        self.replace_entry = Gtk.Entry()
        self.replace_entry.set_width_chars(30)
        self.replace_entry.connect("activate", self.on_replace_one)
        row2.pack_start(self.replace_entry, False, False, 0)
        
        replace_btn = Gtk.Button(label="Replace")
        replace_btn.connect("clicked", self.on_replace_one)
        row2.pack_start(replace_btn, False, False, 0)
        
        replace_all_btn = Gtk.Button(label="Replace All")
        replace_all_btn.connect("clicked", self.on_replace_all)
        row2.pack_start(replace_all_btn, False, False, 0)
        
        self.replace_revealer.add(row2)
        self.search_box.pack_start(self.replace_revealer, False, False, 0)
        
        self.search_bar_revealer.add(self.search_box)
    
    def on_search_text_changed(self, entry):
        text = entry.get_text()
        self.search_settings.set_search_text(text)
        
    def on_search_settings_changed(self, widget):
        self.search_settings.set_case_sensitive(self.match_case_check.get_active())
        self.search_settings.set_at_word_boundaries(self.whole_word_check.get_active())
        self.search_settings.set_regex_enabled(self.regex_check.get_active())
        
    def on_search_next(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        editor = self.notebook.get_nth_page(page_num)
        
        if editor.search_context:
            buff = editor.buffer
            insert = buff.get_insert()
            iter_start = buff.get_iter_at_mark(insert)
            
            # Helper to unpack results safely
            def unpack_search_result(result):
                if len(result) == 4:
                    return result # success, start, end, wrapped
                elif len(result) == 3:
                    return result[0], result[1], result[2], False
                return False, None, None, False

            # Forward search
            try:
                ret = editor.search_context.forward2(iter_start)
            except AttributeError:
                ret = editor.search_context.forward(iter_start)
            
            success, match_start, match_end, wrapped = unpack_search_result(ret)

            if success:
                # Place cursor at END of match so next search finds next match
                buff.select_range(match_end, match_start)
                editor.view.scroll_to_iter(match_start, 0.0, True, 0.0, 0.5)
            else:
                # Wrap
                start = buff.get_start_iter()
                try:
                    ret = editor.search_context.forward2(start)
                except AttributeError:
                    ret = editor.search_context.forward(start)
                
                success, match_start, match_end, wrapped = unpack_search_result(ret)
                
                if success:
                    buff.select_range(match_end, match_start)
                    editor.view.scroll_to_iter(match_start, 0.0, True, 0.0, 0.5)

    def on_search_prev(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        editor = self.notebook.get_nth_page(page_num)
        
        if editor.search_context:
            buff = editor.buffer
            insert = buff.get_insert()
            iter_start = buff.get_iter_at_mark(insert)
            
            # Helper to unpack results safely
            def unpack_search_result(result):
                if len(result) == 4:
                    return result # success, start, end, wrapped
                elif len(result) == 3:
                    return result[0], result[1], result[2], False
                return False, None, None, False

            try:
                ret = editor.search_context.backward2(iter_start)
            except AttributeError:
                ret = editor.search_context.backward(iter_start)
                
            success, match_start, match_end, wrapped = unpack_search_result(ret)

            if success:
                # Place cursor at START of match so prev search finds prev match
                buff.select_range(match_start, match_end)
                editor.view.scroll_to_iter(match_start, 0.0, True, 0.0, 0.5)
            else:
                # Wrap to end
                end = buff.get_end_iter()
                try:
                    ret = editor.search_context.backward2(end)
                except AttributeError:
                    ret = editor.search_context.backward(end)
                
                success, match_start, match_end, wrapped = unpack_search_result(ret)

                if success:
                    buff.select_range(match_start, match_end)
                    editor.view.scroll_to_iter(match_start, 0.0, True, 0.0, 0.5)

    def on_cut(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            editor.buffer.cut_clipboard(clipboard, True)

    def on_copy(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            editor.buffer.copy_clipboard(clipboard)

    def on_paste(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            editor.buffer.paste_clipboard(clipboard, None, True)

    def on_undo(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            if editor.buffer.can_undo():
                editor.buffer.undo()

    def on_redo(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            if editor.buffer.can_redo():
                editor.buffer.redo()

    def on_delete_selection(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            editor.buffer.delete_selection(True, True)

    def on_delete_line(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            buff = editor.buffer
            insert = buff.get_insert()
            iter_curr = buff.get_iter_at_mark(insert)
            
            # Start of line
            iter_start = iter_curr.copy()
            iter_start.set_line_offset(0)
            
            # End of line (including newline)
            iter_end = iter_start.copy()
            if not iter_end.ends_line():
                 iter_end.forward_to_line_end()
            iter_end.forward_char() # include newline
            
            buff.delete(iter_start, iter_end)

    def on_select_all(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            start, end = editor.buffer.get_bounds()
            editor.buffer.select_range(start, end)

    def on_change_case(self, case_type):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            buff = editor.buffer
            bounds = buff.get_selection_bounds()
            if bounds and len(bounds) == 3 and bounds[0]:
                start, end = bounds[1], bounds[2]
                text = buff.get_text(start, end, True)
                
                new_text = text
                if case_type == "upper":
                    new_text = text.upper()
                elif case_type == "lower":
                    new_text = text.lower()
                elif case_type == "title":
                    new_text = text.title()
                
                if new_text != text:
                    buff.begin_user_action()
                    buff.delete(start, end)
                    buff.insert(start, new_text)
                    buff.end_user_action()

    def on_duplicate(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            buff = editor.buffer
            bounds = buff.get_selection_bounds()
            
            if bounds and len(bounds) == 3 and bounds[0]:
                # Duplicate Selection
                start, end = bounds[1], bounds[2]
                text = buff.get_text(start, end, True)
                buff.insert(end, text)
            else:
                # Duplicate Line
                insert = buff.get_insert()
                iter_curr = buff.get_iter_at_mark(insert)
                line = iter_curr.get_line()
                
                iter_start = buff.get_iter_at_line(line)
                iter_end = iter_start.copy()
                if not iter_end.ends_line():
                    iter_end.forward_to_line_end()
                iter_end.forward_char() # include newline if exists
                
                text = buff.get_text(iter_start, iter_end, True)
                # Ensure we have a newline if duplicating last line without one
                if not text.endswith('\n'):
                     text = "\n" + text
                     
                buff.insert(iter_end, text)

    def on_move_line(self, direction):
        # This is complex to implement robustly without native support.
        # Simple hack: delete line, insert at prev/next line.
        # Skipping for now to avoid messiness unless GtkSourceView has helper.
        pass 

    def on_indent(self, increase):
         # Simple Tab insertion/deletion
         page_num = self.notebook.get_current_page()
         if page_num != -1:
            editor = self.notebook.get_nth_page(page_num)
            buff = editor.buffer
            
            # For simplicity, operate on current line or selection
            # TODO: Full block indent support
            if increase:
                insert = buff.get_insert()
                iter_curr = buff.get_iter_at_mark(insert)
                line_start = iter_curr.copy()
                line_start.set_line_offset(0)
                buff.insert(line_start, "\t")
            else:
                # Check for tab at start
                insert = buff.get_insert()
                iter_curr = buff.get_iter_at_mark(insert)
                line_start = iter_curr.copy()
                line_start.set_line_offset(0)
                next_char = line_start.copy()
                next_char.forward_char()
                
                char = buff.get_text(line_start, next_char, False)
                if char == "\t" or char == " ":
                     buff.delete(line_start, next_char)

    def on_replace_one(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        editor = self.notebook.get_nth_page(page_num)
        
        if editor.search_context:
            buff = editor.buffer
            # Check if selection matches search
            bounds = buff.get_selection_bounds()
            if bounds and len(bounds) == 3 and bounds[0]:
                start, end = bounds[1], bounds[2]
                # Verify match
                # GtkSourceView 4: default replace uses the search text.
                # replace(match_start, match_end, replace_text, replace_length) -> bool
                try:
                    editor.search_context.replace(start, end, self.replace_entry.get_text(), -1)
                except Exception as e:
                    print(f"Replace error: {e}")
                
            self.on_search_next(None)

    def on_replace_all(self, widget):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        editor = self.notebook.get_nth_page(page_num)
        if editor.search_context:
            editor.search_context.replace_all(self.replace_entry.get_text(), -1)

    def on_find_clicked(self, mode="find"):
        # Toggle reveal
        reveal = self.search_bar_revealer.get_reveal_child()
        
        # If hidden, show
        if not reveal:
            self.search_bar_revealer.set_reveal_child(True)
            self.search_entry.grab_focus()
        else:
            # If already shown, just focus unless we want to close (usually Ctrl+F focuses)
            self.search_entry.grab_focus()
            
        if mode == "replace":
            self.replace_revealer.set_reveal_child(True)
        else:
            self.replace_revealer.set_reveal_child(False)

    def create_actions(self):
        # Action Map
        action_group = Gio.SimpleActionGroup()
        self.insert_action_group("win", action_group)

        # Actions
        actions = [
            ("new_tab", self.on_new_tab),
            ("new_window", self.on_new_window),
            ("open", self.on_open_file),
            ("save", self.on_save_file),
            ("save_as", self.on_save_as),
            ("save_all", self.on_save_all),
            ("reload", self.on_reload),
            ("print", self.on_print),
            ("detach_tab", self.on_detach_tab),
            ("find", lambda *args: self.on_find_clicked("find")),
            ("replace", lambda *args: self.on_find_clicked("replace")),
            ("close_tab", self.on_close_current_tab),
            ("close_window", lambda *args: self.close()),
            ("quit", lambda *args: self.get_application().quit())
        ]

        for name, callback in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            action_group.add_action(action)
        
        # Accelerators
        app = self.get_application()
        app.set_accels_for_action("win.new_tab", ["<Primary>n"])
        app.set_accels_for_action("win.new_window", ["<Primary><Shift>n"])
        app.set_accels_for_action("win.open", ["<Primary>o"])
        app.set_accels_for_action("win.save", ["<Primary>s"])
        app.set_accels_for_action("win.save_as", ["<Primary><Shift>s"])
        app.set_accels_for_action("win.reload", ["F5"])
        app.set_accels_for_action("win.print", ["<Primary>p"])
        app.set_accels_for_action("win.detach_tab", ["<Primary>d"])
        app.set_accels_for_action("win.find", ["<Primary>f"])
        app.set_accels_for_action("win.replace", ["<Primary>h"])
        # F3 for next
        # Actions for F3 need to be registered too? Or simple accelerator for find_next?
        # Let's add find_next/prev actions
        app.set_accels_for_action("win.close_tab", ["<Primary>w"])
        app.set_accels_for_action("win.close_window", ["<Primary><Shift>w"])
        app.set_accels_for_action("win.quit", ["<Primary>q"])

    def on_new_window(self, widget, param=None):
        app = self.get_application()
        win = ZenpadWindow(app)
        win.present()

    def on_open_recent(self, recent_chooser):
        item = recent_chooser.get_current_item()
        if item:
            uri = item.get_uri()
            # Convert file:// uri to path
            if uri.startswith("file://"):
                path = uri[7:]
                # decode %20 etc if needed, but keeping simple
                import urllib.parse
                path = urllib.parse.unquote(path)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.add_tab(content, os.path.basename(path), path)
                except Exception as e:
                    print(f"Error opening recent: {e}")

    def on_save_as(self, widget, param=None):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        editor = self.notebook.get_nth_page(page_num)
        self.save_file_as(editor)

    def on_save_all(self, widget, param=None):
        n = self.notebook.get_n_pages()
        for i in range(n):
            editor = self.notebook.get_nth_page(i)
            if editor.file_path:
                self.save_to_path(editor, editor.file_path)
            # Alternatively prompt for save as, but usually save all just saves known files

    def on_reload(self, widget, param=None):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        editor = self.notebook.get_nth_page(page_num)
        if editor.file_path and os.path.exists(editor.file_path):
            try:
                with open(editor.file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                editor.set_text(content)
            except Exception as e:
                print(f"Error reloading: {e}")

    def on_print(self, widget, param=None):
        # Basic print scaffolding
        op = Gtk.PrintOperation()
        # op.connect("draw-page", self.draw_page_cb) 
        # Printing is complex, implementing full draw logic is out of scope for "quick implementation"
        # Display error/info for now
        dlg = Gtk.MessageDialog(parent=self, modal=True, message_type=Gtk.MessageType.INFO,
                                buttons=Gtk.ButtonsType.OK, text="Printing")
        dlg.format_secondary_text("Printing is not fully configured in this environment.")
        dlg.run()
        dlg.destroy()

    def on_detach_tab(self, widget, param=None):
        page_num = self.notebook.get_current_page()
        if page_num == -1: return
        
        # Get content and path
        editor = self.notebook.get_nth_page(page_num)
        text = editor.get_text()
        path = editor.file_path
        title = os.path.basename(path) if path else "Untitled"
        
        # Remove from current
        self.close_tab(page_num)
        
        # Create new window with this tab
        app = self.get_application()
        win = ZenpadWindow(app)
        win.add_tab(text, title, path)
        # Remove the initial empty tab of new window if it exists
        if win.notebook.get_n_pages() > 1:
            win.notebook.remove_page(0)
        win.present()

    def on_new_tab(self, widget, param=None):
        self.add_tab()
        
    def on_close_current_tab(self, widget, param=None):
        page_num = self.notebook.get_current_page()
        if page_num != -1:
            self.close_tab(page_num)

    def close_tab(self, page_num):
        self.notebook.remove_page(page_num)
        # If no tabs left, close window? Or add empty?
        if self.notebook.get_n_pages() == 0:
            self.close()

    def add_tab(self, content=None, title="Untitled", path=None):
        editor = EditorTab(self.search_settings)
        if content is not None:
            editor.set_text(content)
        
        if path:
            editor.file_path = path
            editor.detect_language(path)
        else:
            editor.file_path = None
        
        # Tab Label with Close Button
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_spacing(5)
        label = Gtk.Label(label=title)
        box.pack_start(label, True, True, 0)
        
        close_btn = Gtk.Button.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        # We need to capture the editor widget or page num to close correctly
        # However, page num changes. Using the child widget 'editor' is safer.
        close_btn.connect("clicked", lambda btn: self.on_close_clicked(editor))
        box.pack_start(close_btn, False, False, 0)
        box.show_all()
        
        self.notebook.append_page(editor, box)
        self.notebook.show_all()
        
        # Connect signals
        editor.buffer.connect("modified-changed", lambda w: self.update_tab_label(editor))
        editor.buffer.connect("mark-set", lambda w, loc, mark: self.update_match_count(editor))
        # Search signals
        if editor.search_context:
             editor.search_context.connect("notify::occurrences-count", lambda w, p: self.update_match_count(editor))

        # Switch to the new tab
        self.notebook.set_current_page(-1)
        self.update_tab_label(editor)

    def update_tab_label(self, editor):
        page_num = self.notebook.page_num(editor)
        if page_num == -1: return
        
        tab_box = self.notebook.get_tab_label(editor)
        children = tab_box.get_children()
        if children:
             label = children[0]
             name = os.path.basename(editor.file_path) if editor.file_path else "Untitled"
             if editor.buffer.get_modified():
                 name = f"*{name}"
             label.set_text(name)

    def update_match_count(self, editor):
        # Only update if it's the current tab
        current_page = self.notebook.get_current_page()
        if current_page != -1 and self.notebook.get_nth_page(current_page) == editor:
            if editor.search_context:
                count = editor.search_context.get_occurrences_count()
                
                # Get current match index
                current = 0
                buff = editor.buffer
                bounds = buff.get_selection_bounds()
                if bounds and len(bounds) == 3 and bounds[0]:
                    start, end = bounds[1], bounds[2]
                    target_offset = start.get_offset()

                    try:
                        current = editor.search_context.get_occurrence_position(start, end)
                    except AttributeError:
                        # Fallback: Count manually by collecting offsets
                        # Robust but potentially slow for huge files
                        current = 0
                        iter_curr = editor.buffer.get_start_iter()
                        match_offsets = []
                        
                        while True:
                            try:
                                ret = editor.search_context.forward2(iter_curr)
                            except AttributeError:
                                ret = editor.search_context.forward(iter_curr)
                            
                            # unpack
                            if len(ret) == 4:
                                s, m_start, m_end, wrapped = ret
                            elif len(ret) == 3:
                                s, m_start, m_end = ret[0], ret[1], ret[2]
                            else:
                                break
                            
                            if not s:
                                break
                                
                            match_offsets.append(m_start.get_offset())
                            iter_curr = m_end
                        
                        # Find our place
                        if target_offset in match_offsets:
                            current = match_offsets.index(target_offset) + 1
                        else:
                             # Try approximate match (cursor inside match?)
                             # If selection is somehow different
                           pass


                if count == -1:
                    self.match_count_label.set_text("")
                elif current > 0:
                    self.match_count_label.set_text(f"{current} of {count} matches")
                else:
                    self.match_count_label.set_text(f"{count} matches")
            else:
                self.match_count_label.set_text("")

    def on_close_clicked(self, editor):
        page_num = self.notebook.page_num(editor)
        if page_num != -1:
            self.close_tab(page_num)

    def on_open_file(self, widget, param=None):
        dialog = Gtk.FileChooserDialog(
            title="Open File", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.add_tab(content, os.path.basename(file_path), file_path)
                
                # Add to Recent
                manager = Gtk.RecentManager.get_default()
                manager.add_item("file://" + file_path)
            except Exception as e:
                print(f"Error opening file: {e}")
        
        dialog.destroy()

    def on_save_file(self, widget, param=None):
        page_num = self.notebook.get_current_page()
        if page_num == -1:
            return
        
        editor = self.notebook.get_nth_page(page_num)
        if editor.file_path:
            self.save_to_path(editor, editor.file_path)
        else:
            self.save_file_as(editor)

    def save_file_as(self, editor):
        dialog = Gtk.FileChooserDialog(
            title="Save File", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )
        dialog.set_do_overwrite_confirmation(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            self.save_to_path(editor, file_path)
            
            # Add to Recent
            manager = Gtk.RecentManager.get_default()
            manager.add_item("file://" + file_path)
            
            # Update Tab Label
            page_num = self.notebook.get_current_page()
            
            # Label is now a Box, so we need to find the Label child
            tab_box = self.notebook.get_tab_label(editor)
            # Assuming first child is label (as packed)
            children = tab_box.get_children()
            if children:
                children[0].set_text(os.path.basename(file_path))
            
        dialog.destroy()

    def save_to_path(self, editor, path):
        try:
            content = editor.get_text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            editor.file_path = path
            editor.buffer.set_modified(False) # Mark as saved
            editor.detect_language(path)
            self.update_tab_label(editor)
        except Exception as e:
            print(f"Error saving file: {e}")

    def on_tab_switched(self, notebook, page, page_num):
        editor = self.notebook.get_nth_page(page_num)
        self.update_statusbar(editor)
        self.update_match_count(editor) # Update search count for this tab
        
        # Disconnect previous
        if getattr(self, "current_cursor_handler", None) and getattr(self, "current_buffer", None):
             try:
                 self.current_buffer.disconnect(self.current_cursor_handler)
             except:
                 pass

        self.current_buffer = editor.buffer
        self.current_cursor_handler = editor.buffer.connect("notify::cursor-position", lambda w, p: self.update_statusbar(editor))


    def update_statusbar(self, editor):
        line, col = editor.get_cursor_position()
        self.statusbar.push(0, f"Line {line}, Column {col}")

    def on_preferences_clicked(self, widget):
        dialog = PreferencesDialog(self)
        dialog.run()
        dialog.destroy()

    def apply_setting(self, key, value):
        # Iterate over all tabs and apply setting
        n_pages = self.notebook.get_n_pages()
        for i in range(n_pages):
            editor = self.notebook.get_nth_page(i)
            if key == "line_numbers":
                editor.view.set_show_line_numbers(value)
            elif key == "word_wrap":
                editor.view.set_wrap_mode(Gtk.WrapMode.WORD if value else Gtk.WrapMode.NONE)
            elif key == "theme":
                editor.set_scheme(value)
            elif key == "font":
                font_desc = Pango.FontDescription(value)
                editor.view.modify_font(font_desc)

        # Also store these settings to persistence if needed (not implemented yet)

    def save_session(self, widget, event):
        paths = []
        n_pages = self.notebook.get_n_pages()
        for i in range(n_pages):
            editor = self.notebook.get_nth_page(i)
            if editor.file_path:
                paths.append(editor.file_path)
        
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "zenpad")
        os.makedirs(config_dir, exist_ok=True)
        
        with open(os.path.join(config_dir, "session.json"), "w") as f:
            json.dump(paths, f)
            
        return False # Propagate Close

    def load_session(self):
        config_path = os.path.join(os.path.expanduser("~"), ".config", "zenpad", "session.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    paths = json.load(f)
                    for path in paths:
                        if os.path.exists(path):
                            with open(path, "r", encoding="utf-8") as f_content:
                                self.add_tab(f_content.read(), os.path.basename(path), path)
            except Exception as e:
                print(f"Error loading session: {e}")
                
        # If no tabs loaded (list empty or file not found), add default
        if self.notebook.get_n_pages() == 0:
            self.add_tab()

        if self.notebook.get_n_pages() == 0:
            self.add_tab()


    def on_about(self, widget, param=None):
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_modal(True)
        
        about.set_program_name("Zenpad")
        about.set_version("0.1.0")
        about.set_copyright("Copyright \u00A9 2025 - Zenpad Developers")
        about.set_comments("Zenpad is a simple text editor for the Linux desktop environment,\ndesigned as a Mousepad clone.")
        about.set_website("https://github.com/example/zenpad")
        about.set_website_label("Website")
        
        about.set_authors(["Zenpad Developer Team"])
        about.set_documenters(["Zenpad Documentation Team"])
        about.set_artists(["Zenpad Design Team"])
        
        about.set_license_type(Gtk.License.GPL_2_0)
        
        about.set_logo_icon_name("accessories-text-editor")
        
        about.run()
        about.destroy()
