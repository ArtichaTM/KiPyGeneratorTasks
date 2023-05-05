__all__ = ('Singleton',)


class Singleton:
    __slots__ = ()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            if hasattr(cls._instance, 'new'):
                getattr(cls._instance, 'new')()
        return cls._instance

    def new(self):
        """Called when singleton created. Once in all program"""
