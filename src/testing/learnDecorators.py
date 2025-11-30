def acde(func):
    def wrapper(*args, **kwargs):
        print('doing this')
        for i in range(5):
            func(*args, **kwargs)
        print('doing that')
    return wrapper

@acde
def a(i):
    print('woowowow', i)

@acde
def b(i):
    print('aaaaaaabbbb', i)


a()