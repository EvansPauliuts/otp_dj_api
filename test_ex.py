class BaseClass:
    @staticmethod
    def static_method(a):
        print(a)

    @classmethod
    def class_method(cls, *args, **kwargs):
        print(cls, args, kwargs)

    def method(self):
        print(self)


BaseClass().method()
BaseClass().class_method(1, 2, 3, a=1, b=2, c=3)
BaseClass().static_method('1')

BaseClass().method()
BaseClass.class_method(1, 2, 3, a=1, b=2, c=3)
BaseClass.static_method('1')

# a = BaseClass()
# a.static_method('2')
# a.class_method()
# a.method()
#
# b = BaseClass()
# BaseClass.class_method(b)
# BaseClass.method(b)
# BaseClass.static_method(b)
