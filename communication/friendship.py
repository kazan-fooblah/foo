from pyre import Pyre
from pyre import zhelper
import zmq
import uuid
import json
import math

from binascii import crc32

class Gateway:

    def __init__(self):
        self._chat_pipe = None
        self._delegate = None

    def configure_with(self, delegate):
        self._delegate = delegate

    def start(self):
        ctx = zmq.Context()
        self._chat_pipe = zhelper.zthread_fork(ctx, self._connect)

    def send(self, payload, peer_uuid=None):
        message = {
            "payload": payload.encode('utf-8')
        }
        if type(peer_uuid) == uuid.UUID:
            payload["peer"] = peer_uuid

        self._chat_pipe.send(json.dumps(message).encode('utf-8'))

    def _connect(self, context, pipe):
        node = Pyre("fooblah")
        node.join("fooblah")
        node.start()

        poller = zmq.Poller()
        poller.register(pipe, zmq.POLLIN)
        poller.register(node.inbox, zmq.POLLIN)

        while True:
            items = dict(poller.poll())

            if pipe in items and items[pipe] == zmq.POLLIN:
                message = pipe.recv()

                print "message: %s of %s" % (message, type(message))

                if message.decode('utf-8') == '$$STOP':
                    break

                try:
                    data = json.load(message)

                    if "peer" in data:
                        node.whisper(uuid.UUID(data["peer"]), data["message"])
                    else:
                        node.shout("fooblah", data["message"])

                except AttributeError:
                    pass

            if node.inbox in items and items[node.inbox] == zmq.POLLIN:
                cmds = node.recv()
                msg_type = cmds.pop(0).decode('utf-8')

                peer_uuid_bytes = cmds.pop(0)
                peer_uuid = uuid.UUID(bytes=peer_uuid_bytes)

                print("NODE_MSG TYPE: %s" % msg_type)
                print("NODE_MSG PEER: %s" % peer_uuid)

                if msg_type == "SHOUT":
                    group_name = cmds.pop(0)
                    print("NODE_MSG GROUP: {0}".format(group_name))

                elif msg_type == "ENTER":
                    try:
                        headers = json.loads(cmds.pop(0))
                        print("NODE_MSG HEADERS: {0}".format(headers))
                    except AttributeError:
                        pass

                elif msg_type == 'JOIN':
                    self._delegate.join_recieved(peer_uuid)

                elif msg_type == 'EXIT':
                    self._delegate.exit_recieved(peer_uuid)

                print("NODE_MSG CONT: {0}".format(cmds))

        node.stop()

    def stop(self):
        self.send("$$STOP".encode('utf-8'))

    def __exit__(self, exc_type, exc_value, traceback):
        print "THAT'S ALL FOLKS"
        self.stop()


class Friendship:

    def __init__(self):
        self._gateway = Gateway()
        self._gateway.configure_with(delegate=self)
        self._gateway.start()

        self._delegate = None
        self._friends = set()

    def configure_with(self, delegate):
        self._delegate = delegate

    def join_recieved(self, friend_id):
        crc = crc32(friend_id)
        if abs(crc) < pow(2, 31):
            self._gateway.send(json.dumps({"handshake": }))
        # self._friends.add(friend_id)


    def exit_recieved(self, friend_id):
        try:
            self._friends.remove(friend_id)
        except KeyError:
            pass

    def message_recieved(self, friend_id, payload):
        if friend_id in self._friends:
            if self._delegate is not None:
                self._delegate.message(payload)

    def die(self):
        self._gateway.stop()
