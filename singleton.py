
class Singleton:
    __instances = {}

    def __new__(cls, *args):
        if args not in cls.__instances:
            cls.__instances[args] = object.__new__(cls)
            cls.__instances[args].__init__(*args)
        return cls.__instances[args]