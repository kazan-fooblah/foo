__version__ = "1.0"

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from connection import Connection
from accelerometer import Accelerometer
from accelerometer_delegate import AccelerometerDelegate

from shapiro import env
import uuid

from kivy.properties import BooleanProperty
from kivy.utils import platform

import android
from jnius import autoclass, cast
from android.runnable import run_on_ui_thread

PythonActivity = autoclass('org.renpy.android.PythonActivity')
View = autoclass('android.view.View')
Params = autoclass('android.view.WindowManager$LayoutParams')


U = str(uuid.uuid4())


class UIContainer:

    def __init__(self):
        self._ui = None

    def configure_with(self, ui):
        self._ui = ui

    def draw(self, txt):
        if self._ui is not None:
            self._ui.update(txt)


uiContainer = UIContainer()

def node_main(e):
    global_presence = e.glob(env.LWWDict(), "global_presence")
    one = e.loc(env.LWWValue(), 'one')

    def set_presence(prev, sink):
        next_global_presence = prev.clone()
        new_one = env.LWWValue()
        new_one.set(1)
        next_global_presence.update(U, new_one)
        uiContainer.draw(next_global_presence.keys())
        return next_global_presence
    e.fold(global_presence, global_presence, set_presence)

    def set_one(one_value, sink):
        next_sink = sink.clone()
        next_sink.update(U, one_value)
        return next_sink
    e.fold(one, global_presence, set_one)

    next_one = one.clone()
    next_one.set(1)
    e.loc(next_one, 'one')

# def node_main(e):
#     global_presence = e.glob(env.LWWDict(), "global_presence")
#
#     def set_presence(prev, sink):
#         next_global_presence = prev.clone()
#         one = env.LWWValue()
#         one.set(1)
#         next_global_presence.update(U, one)
#         # UI < next_global_presence.keys()
#         uiContainer.draw(next_global_presence.keys())
#         return next_global_presence
#     e.fold(global_presence, global_presence, set_presence)

class UI(FloatLayout):

    def __init__(self, **kwargs):
        super(UI, self).__init__(**kwargs)
        self.lblAcce = Label(text="")
        self.add_widget(self.lblAcce)

    def update(self, txt):
        self.lblAcce.text = txt

class MainApp(App):

    connection = Connection()
    # acc = Accelerometer()
    # another_acc = Accelerometer()

    def on_stop(self):
        self.connection.stop.set()
        # self.acc.stop.set()
        # self.another_acc.stop.set()

    def build(self):
        self.bind(on_start=self.post_build_init)

        print "fooblah main build start"
        ui = UI()

        print "fooblah main build setflag"

        self.android_setflag()

        # return ui

        # self.another_acc.configure_with(delegate=ui)
        # self.another_acc.start()

        print "fooblah main build "

        uiContainer.configure_with(ui)

        print "fooblah main build handler.init"

        h = env.Handler(node_main)

        print "fooblah main build connection"

        self.connection.configure_with(delegate=None, func=h)
        self.connection.start()

        # acc_delegate = AccelerometerDelegate()
        # acc_delegate.configure_with(connection=self.connection)
        #
        # self.acc.configure_with(delegate=acc_delegate)
        # self.acc.start()

        return ui

    @run_on_ui_thread
    def android_setflag(self):
        PythonActivity.mActivity.getWindow().addFlags(Params.FLAG_KEEP_SCREEN_ON)

    def setflag(self, *args):
        self.android_setflag()

    def post_build_init(self, *args):
        android.map_key(android.KEYCODE_BACK, 1000)
        win = self._app_window
        win.bind(on_keyboard=self._key_handler)

    def _key_handler(self, *args):
        key = args[1]
        if key in (1000, 27):
            self.stop()
            return True


if __name__ == '__main__':
    MainApp().run()
