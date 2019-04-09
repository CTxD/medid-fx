class Base():
    def __init__(self):
        print(self.__class__.__name__)


class Sub(Base):
    def __init__(self):
        super().__init__()


sub = Sub()