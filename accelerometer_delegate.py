from shapiro import env

class AccelerometerDelegate:

    def __init__(self):
        self._handler = None

    def configure_with(self, handler):
        self._handler = handler

    def update(self, msg):
        v = env.LWWValue()
        v.set(float(msg))
        self._handler.env.loc(v, u'current_angle')
