__version__ = "1.0"

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from kivy.clock import Clock, mainthread

from connection import Connection
from accelerometer import Accelerometer
from accelerometer_delegate import AccelerometerDelegate

class UI(FloatLayout):

    def __init__(self, **kwargs):
        super(UI, self).__init__(**kwargs)
        self.lblAcce = Label(text="")
        self.add_widget(self.lblAcce)

    def update(self, txt):
        self.lblAcce.text = txt

class Accelerometer(App):

    connection = Connection()

    def on_stop(self):
        self.connection.stop.set()

    def build(self):
        ui = UI()

        self.connection.configure_with(delegate=ui)
        self.connection.start()

        acc_delegate = AccelerometerDelegate()
        acc_delegate.configure_with(connection=connection)

        acc = Accelerometer()
        acc.configure_with(delegate=acc_delegate)
        acc.start()

        return ui

if __name__ == '__main__':
    Accelerometer().run()
