import functools
class Test():

    def my(self, a):
        print(a)

    aa = functools.partial(my, a=10)


if __name__ == "__main__":
    t = Test()
    t.aa(t)
