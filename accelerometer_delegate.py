class AccelerometerDelegate:

    def __init__(self):
        self._connection = None

    def configure_with(self, connection):
        self._connection = connection

    def update(self, msg):
        self._connection.send(msg)
