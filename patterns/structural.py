from time import time


routes = {}


def route(url):
    def wrapper(cls):
        routes[url] = cls()
    return wrapper


class Debug:
    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        def timeit(method):
            def timed(*args, **kw):
                st = time()
                result = method(*args, **kw)
                et = time()
                res_time = et - st
                print(f'debug {self.name}: выполнялся {res_time:2.2f} ms')
                return result
            return timed
        return timeit(cls)
