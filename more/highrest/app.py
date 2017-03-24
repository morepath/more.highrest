import morepath
from dectate import directive
from . import action


class App(morepath.App):
    collection = directive(action.CollectionAction)
