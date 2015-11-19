from shapiro import env
import time


def main(e):
    def inc_sleep(source):
        s = source.clone()
        s.increment()
        return s

    global_sum = e.glob(env.GCounter(), 'global_sum')
    print("APP: Got initial global sum: " + str(global_sum.value))
    e.fold(global_sum, global_sum, inc_sleep)


def real():
    e = env.Env()
    h = env.Handler(main, env=e)
    h.attached()
    print("MAN: " + str(e.globals.payload))
    h(e.globals.payload)
    next_e = e.clone()
    global_sum = next_e.globals['global_sum'].clone()
    global_sum.increment()
    print(global_sum.value)
    next_e.globals.update('global_sum', global_sum)
    h(next_e.globals.payload)
    h(next_e.globals.payload)
    h(next_e.globals.payload)
    print(next_e.globals['global_sum'].value)

if __name__ == "__main__":
    real()
