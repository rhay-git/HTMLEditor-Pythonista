try:
    import ui
    import console
except ImportError:
    print "Using Dummy UI"
    import dummyUI as ui
    import dummyConsole as console
import urllib
import os


def exception_str(exception):
    return '{}: {}'.format(exception.__class__.__name__, exception)


def dummy_save(file_contents):
    # print "Saving file with contents %s" % file_contents
    pass


def list_themes():
    if "EditorView" in os.path.abspath("CodeMirror-5.3.0/theme"):
        path = os.path.abspath("CodeMirror-5.3.0/theme")
    else:
        path = os.path.abspath("EditorView/CodeMirror-5.3.0/theme")
    l = os.listdir(path)
    return [x.replace(".css", "") for x in l]


class WebViewDelegate(object):

    def __init__(self, save_func, console_view):
        self.save_func = save_func
        self.console_view = console_view
        self.webview = None
        self.load_callback = []

    def webview_should_start_load(self, webview, url, nav_type):
        self.webview = webview
        if url.startswith('ios'):
            url = urllib.unquote(url)
            url = url.replace("ios-", "")
            if url.startswith("log"):
                self.console_view.log(webview, url)
            elif url.startswith("error"):
                self.console_view.log(webview, url)
            elif url.startswith("warn"):
                self.console_view.log(webview, url)
            elif url.startswith("info"):
                self.console_view.log(webview, url)
            elif url.startswith("debug"):
                self.console_view.log(webview, url)
            elif url.startswith("save"):
                self.save(webview)
            elif url.startswith("alert"):
                self.alert(*url.replace("alert:", "").split(":"))
            return False
        print "Loading File: ", url
        return True

    def webview_did_start_load(self, webview):
        pass

    def webview_did_finish_load(self, webview):
        for callback in self.load_callback:
            callback()

    def webview_did_fail_load(self, webview, error_code, error_msg):
        print "Webview Error %r %s" % (error_code, error_msg)

    def add_load_callback(self, callback):
        self.load_callback.append(callback)

    def save(self, wv):
        if self.save_func:
            self.save_func(str(wv.eval_js('''editor.getValue();''')))

    def open(self, filename, contents):
        self._open(filename, contents)

    def _open(self, filename, contents):
        try:
            if self.webview:
                self.webview.eval_js("editor.setValue(%r)" % str(contents))
                mode = self.get_mode(filename)
                print "Loading: %s with mode %r" % (filename, mode)
                self.webview.eval_js(
                    "editor.setOption('mode', %r);" % str(mode))
                self.webview.eval_js(
                    "CodeMirror.autoLoadMode(editor, %r);" % str(mode))
                #self.webview.eval_js("loadMode(%r)" % str(mode))
            else:
                print "could not open file: %r" % filename
        except Exception as e:
            print exception_str(e)

    def get_mode(self, filename):
        '''return style name used by change_syntax, based on file extension.  '''
        syntaxes = {'css': 'css',
                    'html': 'htmlmixed',
                    'js': 'javascript',
                    'php': 'php',
                    'py': 'python',
                    'vb': 'vb',
                    'xml': 'xml',
                    'sql': 'sql',
                    'pas': 'pas',
                    'pl': 'perl',
                    'md': 'markdown'}
        try:
            ext = os.path.splitext(filename)[1][1:]
            syntax = syntaxes[ext]
        except KeyError as e:
            print exception_str(e)
            syntax = 'htmlmixed'
        return syntax

    @ui.in_background
    def alert(self, *args):
        console.alert(args[0], args[1], "ok")


class WebViewConsole(ui.View):

    def log(self, wv, msg):
        self["log_view"].text += "%s\n" % msg
        print "LOGGING MESSAGE ---> " + msg
        ui.delay(self.scroll, 0.0)

    def scroll(self):
        x, y = self["log_view"].content_offset
        width, height = self["log_view"].content_size
        self["log_view"].content_offset = (0, height - self["log_view"].height)
        self["log_view"].bounces = False


class WebViewInputDelegate(object):

    def __init__(self, webview):
        self.webview = webview

    def textfield_should_return(self, textfield):
        textfield.end_editing()
        self.webview.eval_js(textfield.text)
        textfield.text = ""
        return True


class WebView(ui.View):

    def log(self, wv, msg):
        print "LOGGING MESSAGE ---> " + msg

    def will_close(self):
        ui.cancel_delays()


def load_console(frame=(0, 0, 540, 575), load_addons=True):
    try:
        view = ui.load_view("EditorView/EditorViewConsole")
    except ValueError as e:
        print "Attempt 1 'EditorView/EditorViewConsole' failed " + exception_str(e)
        try:
            view = ui.load_view("EditorViewConsole")
        except ValueError as e:
            print "Attempt 2 'EditorViewConsole' failed " + exception_str(e)
            view = WebViewConsole()
    print "Setting Frame"
    view.frame = frame
    print "Done"
    return view


def load_editor_view(frame=None, load_addons=True):
    try:
        view = ui.load_view("EditorView/EditorView")
    except ValueError as e:
        print "Attempt 1 'EditorView/EditorView' failed " + exception_str(e)
        try:
            view = ui.load_view("EditorView")
        except ValueError as e:
            print "Attempt 2 'EditorView' failed " + exception_str(e)
            view = ui.WebView()
    if frame:
        view.frame = frame
    return view


def load_html_editor_view():
    if "EditorView" in os.path.abspath("index.html"):
        return os.path.abspath("index.html")
    else:
        return os.path.abspath("EditorView/index.html")


def load_html_preview_template():
    if "EditorView" in os.path.abspath("template.html"):
        return os.path.abspath("template.html")
    else:
        return os.path.abspath("EditorView/template.html")


def create_mode_btn(select_func):
    mode = ui.ButtonItem("mode")

    def change_mode(sender):
        v = ui.TableView()
        v.data_source = ui.ListDataSource(
            [{"title": x} for x in list_themes()])
        v.delegate = v.data_source

        def select_mode(sender):
            i = sender.items[sender.selected_row]
            if select_func:
                select_func(i)
            v.close()
        v.width = 200
        v.height = 500
        v.present(
            style="popover", hide_title_bar=True, popover_location=(300, 100))
        v.data_source.action = select_mode
    mode.action = change_mode

    return mode

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        use_console = bool(sys.argv[1])
    else:
        use_console = False
    if use_console:
        console_view = load_console()
        console_view["console_input"].delegate = WebViewInputDelegate(
            console_view["web_view"])
    else:
        console_view = load_editor_view()
    print list_themes()
    view = console_view["web_view"]
    view.delegate = WebViewDelegate(dummy_save, console_view)
    view.load_url(load_html_editor_view())

    def load():
        # os.path.abspath("CodeMirror-5.3.0/lib/codemirror.js")
        path = os.path.abspath("index.html")
        with open(path, "rb") as f:
            view.delegate.open(path, str(f.read()))
    view.delegate.add_load_callback(load)
    console_view.present("sheet")

    def select_func(i):
        view.eval_js("editor.setOption('theme', '%s')" % i["title"])
        color = view.eval_js(
            "window.getComputedStyle(document.getElementById('code'), null).backgroundColor")
        print "%r" % color
    btn = create_mode_btn(select_func)
    console_view.left_button_items = [btn]
