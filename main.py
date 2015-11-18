__version__ = "1.0"
from kivy.app import App #for the main app
from kivy.uix.floatlayout import FloatLayout #the UI layout
from kivy.uix.label import Label #a label to show information
from plyer import accelerometer #object to read the accelerometer
from kivy.clock import Clock, mainthread #clock to schedule a method

import socket
import struct

# from kivy.lang import Builder
# from kivy.factory import Factory
# from kivy.animation import Animation
# from kivy.uix.gridlayout import GridLayout
# import threading
# import time

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 5007

class UI(FloatLayout):#the app ui
    def __init__(self, **kwargs):
        super(UI, self).__init__(**kwargs)
        self.lblAcce = Label(text="Accelerometer: ") #create a label at the center
        self.add_widget(self.lblAcce) #add the label at the screen

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                                         # to MCAST_GRP, not all groups on MCAST_PORT
            mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


            accelerometer.enable() # enable the accelerometer
            # if you want do disable it, just run: accelerometer.disable()
            Clock.schedule_interval(self.update, 1.0/24) # 24 calls per second

        except Exception as e:
            self.lblAcce.text = "Failed to start accelerometer %s" %e #error

    # @mainthread
    def update(self, dt):
        txt = ""
        try:
            txt = "Accelerometer:\nX = %.2f\nY = %.2f\nZ = %2.f \nRecievied: %s" % (
                accelerometer.acceleration[0],  # read the X value
                accelerometer.acceleration[1],  # Y
                accelerometer.acceleration[2])  # Z
        # str(self.sock.recv(10240))

        except Exception as e:
            txt = "Cannot read accelerometer! " % e #error
        self.lblAcce.text = txt  # add the correct text

    # def start_second_thread(self):
    #     threading.Thread(target=self.second_thread).start()

    # def second_tread(self):

class Accelerometer(App): #our app
    def build(self):
        ui = UI()# create the UI
        return ui #show it

if __name__ == '__main__':
    Accelerometer().run() #start our app
