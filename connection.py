import socket
import struct
import threading
import uuid
import json

from kivy.clock import Clock, mainthread

MCAST_GRP = '224.0.0.1'
MCAST_PORT = 5670

class Connection:

    stop = threading.Event()
    sock = None

    def __init__(self):
        self._delegate = None
        self._uuid = uuid.uuid4()

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
        try:
            m = {
                "uuid": self._uuid,
                "payload": message
            }
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.sendto(json.dumps(m), (MCAST_GRP, MCAST_PORT))
            sock.close()
        except:
            self._delegate.update("connection.send: %s" % e)

    @mainthread
    def recieved(self, txt):
        try:
            self._delegate.update(txt)
        except Exception as e:
            self._delegate.update("connection.recieved: %s" % e)

    def start_second_thread(self):
        try:
            threading.Thread(target=self.second_thread).start()
        except Exception as e:
            self._delegate.update("connection.start_second_thread: %s" % e)

    def second_thread(self):
        try:
            while True:
                if self.stop.is_set():
                    break
                msg = str(self.sock.recv(4096))
                self.recieved(msg)
        except Exception as e:
            self._delegate.update("connection.second_thread: %s" % e)
        finally:
            self.sock.close()
