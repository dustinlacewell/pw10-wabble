
import collections

class CollisionDispatcher(object):

    def __init__(self):
        self._funcs = collections.defaultdict(self._factory) # {(type1, type2): func12, (type3, type4): func34}

    def add(self, type1, type2, func):
        if __debug__:
            if self._funcs.has_key((type1, type2)):
                print "key already registered for collision func:", (type1, type2)
        self._funcs[(type1, type2)] = func

    def collide(self, obj1, obj2):
        return self._funcs[(obj1.__class__, obj2.__class__)](obj1, obj2)

    def get_func(self, obj1, obj2):
        return self._funcs[(obj1.__class__, obj2.__class__)]

    def _factory(self):
        return self._default_func

    def _default_func(self, a, b):
        if __debug__:
            print "missing coll functions for objects", a.__class__, b.__class__
        return False