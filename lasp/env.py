from crdt.base import StateCRDT
from time import time


class LWWDict(StateCRDT):
    def __init__(self):
        super(StateCRDT, self).__init__()
        self.A = {}
        self.R = {}
        self.pairs = {} # Contains CRTD as well

    def value(self):
        result = {}
        for (k, ts) in self.A.iteritems():
            if ts >= self.R.get(k, 0):
                result[k] = self.pairs[k]
        return result

    def add(self, key, value):
        self.A[key] = (time(),)
        self.pairs[key] = value

    def discard(self, key):
        if key in self.A:
            self.R[key] = (time(),)
            del self.pairs[key]

    def update(self, key, new_value):
        self.discard(key)
        self.add(key, new_value)

    def keys(self):
        return self.value().keys()

    def __contains__(self, key):
        return key in self.value().keys()

    def __getitem__(self, key):
        return self.value()[key]

    def get_payload(self):
        return {
            'A': self.A,
            'R': self.R,
            'pairs': self.pairs
        }

    def set_payload(self, payload):
        self.A = payload['A']
        self.R = payload['R']
        self.pairs = payload['pairs']

    payload = property(get_payload, set_payload)

    def compare(self, other):
        a_e = set([(k, ts) for k, ts in self.A.iteritems()])
        a_t = set([(k, ts) for k, ts in self.R.iteritems()])
        b_e = set([(k, ts) for k, ts in other.A.iteritems()])
        b_t = set([(k, ts) for k, ts in other.R.iteritems()])
        a = a_e.union(a_t)
        b = b_e.union(b_t)
        left = a.issubset(b)
        right = a_t.issubset(b_t)
        return left and right


    @classmethod
    def merge(cls, X, Y):
        additions, pairs = cls._merge_additions(X, Y)
        print(additions)
        print(pairs)
        removals = cls._merge_removals(X, Y)
        print(removals)
        payload = {
            'A': additions,
            'R': removals,
            'pairs': pairs
        }
        print(payload)
        return cls.from_payload(payload)

    @classmethod
    def _merge_additions(cls, X, Y):
        additions = {}
        pairs = {}
        keys = set(X.A) | set(Y.A)
        for key in keys:
            x_timestamp = X.A.get(key, 0)
            y_timestamp = Y.A.get(key, 0)
            if x_timestamp >= y_timestamp:
                pairs[key] = X.pairs[key]
                additions[key] = x_timestamp
            else:
                pairs[key] = Y.pairs[key]
                additions[key] = y_timestamp
        return additions, pairs

    @classmethod
    def _merge_removals(cls, X, Y):
        result = {}
        keys = set(X.R) | set(Y.R)
        for k in keys:
            result[k] = max(X.R.get(k, 0), Y.R.get(k, 0))
        return result


class Local(object):
    def __init__(self, name, env):
        self.name = name
        self.env = env

    def fold(self, func, sink):
        pass

    def value(self):
        return self.env.locals[self.name]


class Global(object):
    def __init__(self, name, env):
        self.name = name
        self.env = env

    def value(self):
        return self.env.globals[self.name]

    def fold(self, func, sink):
        pass


class Env(object):
    def __init__(self):
        self.globals = LWWDict()
        self.locals = {}
        self.interesting = {}

    def glob(self, dt, name):
        if name in self.globals:
            value = self.globals[name]
            new_value = value.merge(value)
            self.globals.update(name, new_value)
        else:
            self.globals.add(name, dt)
        # Publish
        return Global(name, self)

    def loc(self, dt, name):
        self.locals[name] = dt
        return Local(name, self)


class Handler(object):
    def __init__(self, publish, env=Env()):
        self.env = env
        self.publish = publish

    def handle(self, global_state_payload):
        new_global = LWWDict.from_payload(global_state_payload)
        current_global = self.env.globals
        next_global = LWWDict.merge(current_global, new_global)
        self.env.globals = next_global
        interests = set(self.env.interesting.keys()) & set(self.env.globals.keys())
        for interest in interests:
            handler = self.env.interesting.get(interest)
            if hasattr(handler, '__call__'):
                handler(self.env.globals[interest])

