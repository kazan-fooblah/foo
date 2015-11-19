import threading
import time
import math

from plyer import accelerometer
from kivy.clock import Clock, mainthread

FREQUENCY = 1.0 / 24

class Accelerometer:

    stop = threading.Event()

    def __init__(self):
        self._delegate = None

    def configure_with(self, delegate):
        self._delegate = delegate

    def start(self):
        try:
            accelerometer.enable()
            self.start_second_thread()
        except Exception as e:
            self._delegate.update("accelerometer.start: %s" % e)

    @mainthread
    def update(self, msg):
        self._delegate.update(msg)

    def start_second_thread(self):
        try:
            threading.Thread(target=self.second_thread, name="Little Sparrow").start()
        except Exception as e:
            self._delegate.update("accelerometer.start_second_thread: %s" % e)

    def second_thread(self):
        try:
            while True:
                if self.stop.is_set():
                    break
                msg = Accelerometer.accelerometer_representation()
                self.update(msg)
                time.sleep(1.0 / 24)
        except Exception as e:
            self.update("accelerometer.second_thread: %s" % e)

    @staticmethod
    def accelerometer_representation():
        x = float(accelerometer.acceleration[0] or 0)
        y = float(accelerometer.acceleration[1] or 0)
        z = float(accelerometer.acceleration[2] or 0)
        # return math.arcsin(z / (pow(pow(z, 2) + pow(y, 2) + pow(x, 2)), 0.5))
        return math.atan(y / x)

