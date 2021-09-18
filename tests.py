import time


def timer(function):
    """Wrapper function to measure executing time"""
    def inner_function(*args, **kwargs):
        """Function to measure the executing time"""
        start = time.perf_counter()

        value = function(*args, **kwargs)

        print(f"{function.__name__} took {time.perf_counter() - start:.6f} seconds")

        return value

    return inner_function
