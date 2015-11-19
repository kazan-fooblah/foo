from shapiro import env
import time
import uuid
import threading

U = str(uuid.uuid4())


def acc(e):
    angles = e.glob(env.LWWDict(), 'angles')
    average_angle = e.glob(env.LWWValue(), 'average_angle')
    local_angle = e.loc(env.LWWValue(), 'local_angle')

    def update_my_angle(local_angle, angles):
        next_angles = angles.clone()
        next_angles.update(U, local_angle)
        return next_angles
    e.fold(local_angle, angles, update_my_angle, 'update_my_angle')

    def display(source, sink):
        print('++++++++++++++++++')
        return sink
    e.fold(angles, angles, display)

    def on_acc(next_value):
        next_local_angle = local_angle.clone()
        next_local_angle.set(next_value)
        e.loc(next_local_angle, 'local_angle')

    def update_acc():
        c = 0.0
        while True:
            c += 0.1
            time.sleep(0.2)
            on_acc(c)
    threading.Thread(target=update_acc).start()



# def main(e):
#     def inc_sleep(source, sink):
#         s = source.clone()
#         s.increment()
#         return s
#
#     global_sum = e.glob(env.GCounter(), 'global_sum')
#     e.fold(global_sum, global_sum, inc_sleep)


def real():
    e = env.Env()
    h = env.Handler(acc, env=e)
    h.attached()
    print("MAN: " + str(e.globals.payload))
    h(e.globals.payload)
    #next_e = e.clone()
    #global_sum = next_e.globals['global_sum'].clone()
    #global_sum.increment()
    #print(global_sum.value)
    #next_e.globals.update('global_sum', global_sum)
    #h(next_e.globals.payload)
    #h(next_e.globals.payload)
    #h(next_e.globals.payload)
    #print(next_e.globals['global_sum'].value)

if __name__ == "__main__":
    real()
