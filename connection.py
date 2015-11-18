import socket
import struct
import threading

from kivy.clock import Clock, mainthread

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 5670

class Connection:

    stop = threading.Event()
    sock = None

    def __init__(self):
        self._delegate = None

    def configure_with(self, delegate):
        self._delegate = delegate

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MCAST_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.start_second_thread()

    def send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        sock.close()

    @mainthread
    def update2(self, txt):
        self._delegate.update_from_socket(txt)

    def start_second_thread(self):
        try:
            threading.Thread(target=self.second_thread).start()
        except Exception as e:
            self._delegate.update_from_socket("start_second_thread: %s" % e)

    def second_thread(self):
        while True:
            if self.stop.is_set():
                self.sock.close()
                return
            msg = str(self.sock.recv(255))
            self.update2(msg)
