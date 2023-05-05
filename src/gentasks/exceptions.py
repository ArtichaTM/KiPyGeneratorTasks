class GeneratorUnexpectedShutdown(Exception):
    __slots__ = ()
    __module__ = 'builtins'

    def __repr__(self) -> str:
        return type(self).__qualname__
