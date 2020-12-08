from os_.driver import OSDriver


def create_os(program_file: str) -> OSDriver:
    return OSDriver(program_file)
