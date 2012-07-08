# -*- coding: utf-8 -*-
"""orphan.switchboard -- Burbank? I need something.
"""
from collections import defaultdict, MutableMapping


class Switchboard(MutableMapping):
    """A collection of signals.

    Switchboards are registered by name. All Switchboards with the
    same name have the same contents.
    """
    _name_dict = defaultdict(dict)  # For a twist on the Borg idiom

    def __init__(self, name='default', **kwargs):
        self.name = name
        self.dict = Switchboard._name_dict[name]

        super(Switchboard, self).__init__(**kwargs)

    def __contains__(self, key):
        return self.dict.__contains__(key)

    def __len__(self):
        return self.dict.__len__()

    def __iter__(self):
        return self.dict.__iter__()

    def __getitem__(self, key):
        return self.dict.__getitem__(key)

    def __setitem__(self, key, value):
        return self.dict.__setitem__(key, value)

    def __delitem__(self, key):
        return self.dict.__delitem__(key)
