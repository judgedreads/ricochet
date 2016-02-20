from gi.repository import Gtk, GObject
import threading


def progress(func, *args, **kwargs):
    win = Gtk.Window(default_height=50, default_width=300)
    win.connect("delete-event", Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

    progress = Gtk.ProgressBar(show_text=True)
    progress.set_text('updating cache...')
    win.add(progress)

    def update_progress():
        progress.pulse()
        return True

    def target():
        func(*args, **kwargs)
        win.close()

    win.show_all()

    GObject.timeout_add(100, update_progress)
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    Gtk.main()
