from fossa.utils import CachedSession, Session
import click


class Registrar(object):
    def __init__(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']

        if 'cache' in kwargs:
            self.session = CachedSession("{}-{}".format(self.__class__.__name__, self.name),
                                         cache=kwargs['cache'])
        else:
            self.session = Session(self.__class__.__name__ + self.name)

    def error(self, message):
        click.echo("{} {!s}: {}".format(click.style("ERR", fg="red"), self, message), err=True)

    def list(self):
        pass

    def __str__(self):
        if hasattr(self, "name"):
            return "{} ({})".format(self.__class__.__name__, self.name)
        else:
            return self.__class__.__name__
