# -*- coding: utf-8 -*-
"""orphan.enum -- enumerated types, with super-powers!
"""
import random
from . import palette


class Enum(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'members'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.members = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.members.append(cls)
            cls.index = len(cls.members) - 1
            setattr(cls.__class__, cls.__name__, cls)
            cls.key = cls.__name__

            if hasattr(cls, 'foregrounds'):
                cls.foreground_slugs = []
                for fg in cls.foregrounds:
                    cls.foreground_slugs.append(palette.entries.registerForeground(fg))
                if not hasattr(cls, 'foreground_slug'):
                    cls.foreground_slug = staticmethod(lambda x: random.choice(cls.foreground_slugs))
            elif hasattr(cls, 'foreground'):
                cls.foreground_slug = palette.entries.registerForeground(cls.foreground)

            if hasattr(cls, 'backgrounds'):
                cls.background_slugs = []
                for bg in cls.backgrounds:
                    cls.background_slugs.append(palette.entries.registerBackground(bg))
                if not hasattr(cls, 'background_slug'):
                    cls.background_slug = staticmethod(lambda x: random.choice(cls.background_slugs))
            elif hasattr(cls, 'background'):
                cls.background_slug = palette.entries.registerBackground(cls.background)

    def __iter__(cls):
        return iter(cls.members)

    def __len__(cls):
        return len(cls.members)

    def __getitem__(cls, idx):
        try:
            if isinstance(idx, int):
                return cls.members[idx]
            elif type(idx, basestring):
                try:
                    return getattr(cls, int)
                except AttributeError:
                    pass
        except KeyError:
            raise TypeError("'%s' does not support indexing." % cls.__name__)

        # Failing all that, raise our own KeyError.
        raise KeyError(idx)

    def __int__(cls):
        try:
            return cls.index
        except AttributeError:
            raise ValueError("'%s' does not support integer casting.")

    def __str__(cls):
        try:
            return cls.key
        except AttributeError:
            return super(Enum, cls).__str__()

    def __unicode__(cls):
        try:
            return unicode(cls.key)
        except AttributeError:
            return super(Enum, cls).__unicode__()
