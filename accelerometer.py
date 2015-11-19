import threading
import time

from plyer import accelerometer
from kivy.clock import Clock, mainthread

FREQUENCY = 1.0 / 24

class Accelerometer:

    stop = None

    def __init__(self):
        self._delegate = None

    def configure_with(self, delegate):
        self._delegate = delegate

    def start(self):
        try:
            accelerometer.enable()
            # Clock.schedule_interval(self.update, 1.0 / 24)
            # self._delegate.update("accelerometer.start_second_thread: %s")
            # raise
            self.start_second_thread()
        except Exception as e:
            self._delegate.update("accelerometer.start: %s" % e)

    @mainthread
    def update(self, msg):
        self._delegate.update(msg)

    def start_second_thread(self):
        try:
            threading.Thread(target=self.second_thread).start()
            names = map(lambda x: x.name, threading.enumerate())
            self._delegate.update("\n".join(names))
        except Exception as e:
            self._delegate.update("accelerometer.start_second_thread: %s" % e)

    def second_thread(self):
        try:
            while True:
                if self.stop.is_set():
                    break
                msg = Accelerometer.accelerometer_representation()
                self.update(msg)
                time.sleep(FREQUENCY)
        except Exception as e:
            self._delegate.update_from_socket("accelerometer.second_thread: %s" % e)

    @staticmethod
    def accelerometer_representation():
        return "X = %.2f\nY = %.2f\nZ = %2.f" % (accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2])
