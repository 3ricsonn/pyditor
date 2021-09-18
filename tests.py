import time


def timer(function):
    def inner_function(*args, **kwargs):
        start = time.perf_counter()

        value = function(*args, **kwargs)

        print(f"{function.__name__} took {time.perf_counter() - start:.6f} seconds")

        return value

    return inner_function
