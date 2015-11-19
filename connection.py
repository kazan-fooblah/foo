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
        self._callable = None

    def configure_with(self, delegate, func):
        self._delegate = delegate
        self._callable = func

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MCAST_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        h.attached()

        self.start_second_thread()

    def send(self, message):
        try:
            m = {
                "uuid": str(self._uuid),
                "payload": message
            }
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            sock.sendto(json.dumps(m), (MCAST_GRP, MCAST_PORT))
            sock.close()
        except Exception as e:
            self._delegate.update("connection.send: %s" % e)

    @mainthread
    def recieved(self, txt):
        try:
            if self._delegate is not None:
                self._delegate.update(txt)
            if self._callable is not None:
                self._callable(json.loads(txt))
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
                try:
                    message = json.loads(msg)
                    if "uuid" in message and message["uuid"] != str(self._uuid):
                        self.recieved(message["payload"])
                except:
                    pass
        except Exception as e:
            self._delegate.update("connection.second_thread: %s" % e)
        finally:
            self.sock.close()
