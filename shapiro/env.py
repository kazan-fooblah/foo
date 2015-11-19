# -*- coding: utf-8 -*-

from crdt.base import StateCRDT
from time import time
import uuid


def to_typestring(element):
    if isinstance(element, LWWDict):
        return 'lwwdict'
    elif isinstance(element, GCounter):
        return 'gcounter'
    else:
        raise StandardError("SHP: TOS: Hey, I do not know what to do with element of class " + str(element.__class__))


def from_typestring(typestring):
    if typestring == 'gcounter':
        return GCounter
    elif typestring == 'lwwdict':
        return LWWDict
    else:
        raise StandardError("SHP: SOT: Hey, I do not know what to do with typestring " + str(typestring))


class GCounter(StateCRDT):
    def __init__(self, client_id=None):
        super(StateCRDT, self).__init__()
        self._payload = {}
        self.client_id = client_id or str(uuid.uuid4())

    #
    # State-based CRDT API
    #
    def get_payload(self):
        return self._payload

    def set_payload(self, newp):
        self._payload = newp

    payload = property(get_payload, set_payload)

    def clone(self):
        new = super(GCounter, self).clone()

        print("CLONECLONE: " + str(new.payload))
        # Copy the client id
        new.client_id = self.client_id
        return new

    @property
    def value(self):
        return sum(self._payload.itervalues())

    def compare(self, other):
        """
        (∀i ∈ [0, n − 1] : X.P [i] ≤ Y.P [i])
        """
        return all(self._payload.get(key, 0) <= other.payload.get(key, 0)
                   for key in other.payload)

    @classmethod
    def merge(cls, X, Y):
        """
        let ∀i ∈ [0,n − 1] : Z.P[i] = max(X.P[i],Y.P[i])
        """
        keys = set(X.payload.iterkeys()) | set(Y.payload.iterkeys())
        gen = {}
        for k in keys:
            value = max(X.payload.get(k, 0), Y.payload.get(k, 0))
            gen[k] = value
        return cls.from_payload(gen)

    #
    # GCounter API
    #
    def increment(self):
        print("++++++++++++++++++++++++++++++")
        print(self.client_id)
        print(self._payload)
        c = self._payload.get(self.client_id, 0)
        self._payload[self.client_id] = c + 1

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)


class LWWValue(StateCRDT):
    def __init__(self):
        super(StateCRDT, self).__init__()
        self.A = None
        self.v = None

    def set(self, v):
        self.A = time()
        self.v = v

    @classmethod
    def merge(cls, X, Y):
        new = cls()
        if X.A > Y.A:
            new.A = X.A
            new.v = X.v
        else:
            new.A = Y.A
            new.v = Y.v
        return new

    @property
    def value(self):
        return self.v

    def get_payload(self):
        return {
            'A': self.A,
            'v': self.v
        }

    def set_payload(self, payload):
        self.A = payload['A']
        self.v = payload['v']

    payload = property(get_payload, set_payload)


class LWWDict(StateCRDT):
    def __init__(self):
        super(StateCRDT, self).__init__()
        self.A = {}
        self.R = {}
        self.pairs = {} # Contains CRTD as well

    @property
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
        return self.value.keys()

    def __contains__(self, key):
        return key in self.value.keys()

    def __getitem__(self, key):
        return self.value[key]

    def get_payload(self):
        pairs = {}
        print("****************************")
        for k, v in self.pairs.iteritems():
            print("For " + str(k) + " got " + str(v.payload))
            pairs[k] = v.payload
        types = {k: to_typestring(v) for k, v in self.pairs.iteritems()}
        return {
            'A': self.A,
            'R': self.R,
            'pairs': pairs,
            'types': types
        }

    def set_payload(self, payload):
        self.A = payload['A']
        self.R = payload['R']
        types = payload['types']
        self.pairs = {}
        for k, v in payload['pairs'].iteritems():
            self.pairs[k] = from_typestring(types[k])().from_payload(v)

    payload = property(get_payload, set_payload)

    @classmethod
    def merge(cls, X, Y):
        additions, pairs, types = cls._merge_additions(X, Y)
        print('LWW: ADD: ' + str(additions))
        print('LWW: PAR: ' + str(pairs))
        print('LWW: TYP: ' + str(types))
        removals = cls._merge_removals(X, Y)
        print('LWW: REM: ' + str(removals))
        payload = {
            'A': additions,
            'R': removals,
            'pairs': {k: v.payload for k, v in pairs.iteritems()},
            'types': types
        }
        print("LWW: MRG: " + str(payload))
        return cls.from_payload(payload)

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
    def _merge_additions(cls, X, Y):
        additions = {}
        pairs = {}
        types = {}
        keys = set(X.A) | set(Y.A)
        print("MMMMMMMMMMMMMMMM")
        for key in keys:
            x_timestamp = X.A.get(key, 0)
            y_timestamp = Y.A.get(key, 0)
            if x_timestamp >= y_timestamp:
                value = X.pairs[key]
                print("X value: " + str(value) + " of class " + str(value.__class__))
                pairs[key] = value
                types[key] = to_typestring(value)
                additions[key] = x_timestamp
            else:
                value = Y.pairs[key]
                print("Y value: " + str(value) + " of class " + str(value.__class__))
                pairs[key] = value
                types[key] = to_typestring(value)
                additions[key] = y_timestamp
        print("LWW: MRG: After merge: " + str(additions) + ", " + str(pairs) + ", " + str(types))
        return additions, pairs, types

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

    def sink(self, func, sink):
        pass

    def q(self):
        return self.env.locals[self.name]

    def __getattr__(self, item):
        return getattr(self.q(), item)


class Global(object):
    def __init__(self, name, env):
        self.name = name
        self.env = env

    def q(self):
        return self.env.globals[self.name]

    def __getattr__(self, item):
        return getattr(self.q(), item)

    def fold(self, func, sink):
        pass


def fake_broadcast(x):
    print("ENV: FAK: Broadcasting: " + str(x))


class Env(object):
    def __init__(self, broadcast=fake_broadcast):
        self.globals = LWWDict()
        self.locals = {}
        self.global_interesting = {}
        self.local_interesting = {}
        self.broadcast = broadcast

    def glob(self, dt, name):
        if name in self.globals:
            value = self.globals[name]
            print("ENV: GLB: Got new value " + str(value) + " for " + name)
            new_value = value.merge(value, dt)
            print("ENV: GLB: Really new value " + str(value) + " for " + name)
            self.globals.update(name, new_value)
        else:
            self.globals.add(name, dt)
        # Publish
        return Global(name, self)

    def loc(self, dt, name):
        self.locals[name] = dt
        return Local(name, self)

    def fold(self, source, sink, func):
        print("ENV: Make fold of " + str(source.name) + " into " + str(sink.name))

        def and_set_local(value, sink_name):
            print("ENV: Setting local " + str(value) + " to " + str(sink_name))
            self.locals[sink_name] = value
            return value

        def and_set_and_broadcast(value, sink_name):
            self.globals.update(sink_name, value)
            print("New value for global " + str(sink_name) + ": " + str(value) + ", " + str(value.__class__))
            self.broadcast(self.globals.payload)
            return value

        if isinstance(source, Local):
            if isinstance(sink, Local):
                self.local_interesting[source.name] = lambda src: and_set_local(func(src), sink.name)
            elif isinstance(sink, Global):
                self.local_interesting[source.name] = lambda src: and_set_and_broadcast(func(src), sink.name)
        elif isinstance(source, Global):
            if isinstance(sink, Local):
                self.global_interesting[source.name] = lambda src: and_set_local(func(src), sink.name)
            elif isinstance(sink, Global):
                self.global_interesting[source.name] = lambda src: and_set_and_broadcast(func(src), sink.name)

    def clone(self):
        new = self.__class__()
        new.globals = self.globals.clone()
        new.locals = self.locals.copy()
        new.global_interesting = self.global_interesting.copy()
        new.local_interesting = self.local_interesting.copy()
        new.broadcast = self.broadcast
        return new


class Handler(object):
    def __init__(self, func, broadcast=fake_broadcast, env=Env()):
        self.env = env
        self.broadcast = broadcast
        self.func = func
        self.__initiated = False

    def attached(self):
        self.func(self.env)
        print("HAN: Just been attached")
        self.__initiated = True

    def __call__(self, global_state_payload):
        if not self.__initiated:
            raise StandardError("Hey, you must call attached after you attached me!")
        print("HAN: Got new global state payload: " + str(global_state_payload))
        new_global = LWWDict.from_payload(global_state_payload)
        current_global = self.env.globals
        next_global = LWWDict.merge(current_global, new_global)
        self.env.globals = next_global
        interests = set(self.env.global_interesting.keys()) & set(self.env.globals.keys())
        for interest in interests:
            handler = self.env.global_interesting.get(interest)
            if hasattr(handler, '__call__'):
                handler(self.env.globals[interest])
