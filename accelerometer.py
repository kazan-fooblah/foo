from plyer import accelerometer

class Accelerometer:

	FREQUENCY = 1.0 / 1

	def __init__(self):
		self._delegate = None

	def configure_with(self, delegate):
		self._delegate = delegate

	def start(self):
        try:
            accelerometer.enable()
            Clock.schedule_interval(self.update, FREQUENCY)

        except Exception as e:
            self._delegate.update("accelerometer.start: %s" % e)

	def update(self, dt):
		msg = Accelerometer.dt_representation(dt)
		self._delegate.update(msg)

	@classmethod
	def dt_representation(dt):
		return "X = %.2f\nY = %.2f\nZ = %2.f" % (accelerometer.acceleration[0], accelerometer.acceleration[1], accelerometer.acceleration[2])