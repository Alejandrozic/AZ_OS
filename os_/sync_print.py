from os_.synchronization import synchronized


@synchronized
def sync_print(*args):
    print(*args)
