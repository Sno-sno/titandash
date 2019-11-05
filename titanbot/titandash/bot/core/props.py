"""
props.py

A Props object may be used to improve the way the Bot and BotInstance interacts
together. Ensure that the properties specified exist on both the Bot and BotInstance.
"""
from titandash.bot.core.constants import PROPERTIES


PROP_KEYS = {p for p in PROPERTIES}


class Props(object):
    """
    Property Container used by a Bot instance to encapsulate our properties that are present in both
    the Bot class, as well as the BotInstance associated with a session.
    """
    def __init__(self, instance, props):
        self.instance = instance
        self.props = props

    def __getattribute__(self, item):
        if item in PROP_KEYS:
            return getattr(self.instance, item)
        return super(Props, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key in PROP_KEYS:
            # Externally setting the instance value as well, this ensures our
            # sockets are still firing properly when values change.
            setattr(self.instance, key, value)
            self.instance.save()
        super(Props, self).__setattr__(key, value)
