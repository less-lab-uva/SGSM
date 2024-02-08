import pickle
import os
import warnings

from functools import lru_cache


class Node:
    def __init__(self, name, base_class=None, attr=None):
        self.name = name
        self.base_class = base_class
        self.attr = {} if attr is None else attr

    def __repr__(self):
        return str(self.name)  # name should always be a string anyway, but just to be safe


class SGUnickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == '__main__' and name == 'Node':
            return Node
        if module == 'carla_sgg.sgg_abstractor' and name == 'Node':
            return Node
        return super().find_class(module, name)


class IgnoreWaypointPickler(pickle.Pickler):
    def reducer_override(self, obj):
        """Custom reducer for MyClass."""
        if getattr(obj, "__name__", None) == "Waypoint":
            return None
        else:
            # For any other object, fallback to usual reduction
            return NotImplemented

    def persistent_id(self, obj):
        # print(type(obj))
        if str(type(obj)) == "<class 'carla.libcarla.Waypoint'>":
            return 'please_ignore_me'
        else:
            return None  # default behavior


@lru_cache(maxsize=int(os.getenv('SG_CACHE_SIZE', default='128')))
def load_sg(sg_file):
    with open(sg_file, 'rb') as f:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sg = SGUnickler(f).load()
    return sg
