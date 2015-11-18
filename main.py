__version__ = "1.0"

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from plyer import accelerometer
from kivy.clock import Clock, mainthread

import socket
import struct
import threading

from connection import Connection


class UI(FloatLayout):

    def __init__(self, **kwargs):
        super(UI, self).__init__(**kwargs)
        self.lblAcce = Label(text="Accelerometer: ")
        self.add_widget(self.lblAcce)

        try:
            accelerometer.enable()
            Clock.schedule_interval(self.update, 1.0/24)

        except Exception as e:
            self.lblAcce.text = "Failed to start accelerometer %s" %e

    def update(self, dt):
        txt = ""
        try:
            txt = "Accelerometer:\nX = %.2f\nY = %.2f\nZ = %2.f" % (accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2])
        except Exception as e:
            txt = "Cannot read accelerometer! " % e 
            self.lblAcce.text = txt

    def update_from_socket(self, txt):
        self.lblAcce.text = "Recieved: " + txt

class Accelerometer(App):

    connection = Connection()

    def on_stop(self):
        self.connection.stop.set()

    def build(self):
        ui = UI()

        connection.configure_with(delegate=ui)
        connection.start()

        return ui

if __name__ == '__main__':
    Accelerometer().run()
