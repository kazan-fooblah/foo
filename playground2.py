from shapiro import env
import time
import socket
import uuid
import threading
from connection import Connection
import httplib, urllib

U = str(uuid.uuid4())
UI_HOST = 'localhost'
UI_PORT = 3000
UI_ENDPOINT = '/endpoint'

print("I am U: " + U)

def post(data):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    body = '{"foo": "blah"}'
    conn = httplib.HTTPConnection(UI_HOST, UI_PORT)
    conn.request("POST", UI_ENDPOINT, body, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print(data)
    conn.close()


def angle_main(e):
    angles = e.glob(env.LWWDict(), 'angles')
    initial_average = env.LWWValue()
    initial_average.set(0)
    average_angle = e.glob(initial_average, 'average_angle')
    current_angle = e.loc(env.LWWValue(), 'current_angle')

    def add_current_to_angles(current, all):
        next_all = all.clone()
        next_all.update(U, current)
        return next_all
    e.fold(current_angle, angles, add_current_to_angles)

    zero_angle = current_angle.q()
    zero_angle.set(1)
    e.loc(zero_angle, 'current_angle')

    def calculate_average_angle(all_angles, snk):
        count = len(all_angles.value)
        s = sum(all_angles.value.itervalues())
        avg_angle = snk.clone()
        avg_angle.set(float(s) / float(count))
        return avg_angle
    e.fold(angles, average_angle, calculate_average_angle)


def node_main(e):
    global_presence = e.glob(env.LWWDict(), u"global_presence")
    one = e.loc(env.LWWValue(), u'one')

    def set_presence(prev, sink):
        next_global_presence = prev.clone()
        one = env.LWWValue()
        one.set(1)
        next_global_presence.update(U, one)
        return next_global_presence
    e.fold(global_presence, global_presence, set_presence)

    def set_one(one_value, sink):
        next_sink = sink.clone()
        next_sink.update(U, one_value)
        return next_sink
    e.fold(one, global_presence, set_one)

    next_one = one.clone()
    next_one.set(1)
    e.loc(next_one, u'one')


def real():
    connection = Connection()
    h = env.Handler(node_main)
    connection.configure_with(delegate=None, func=h)
    connection.start()

if __name__ == "__main__":
    real()
