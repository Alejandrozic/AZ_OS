"""
    The Arithmetic Logic Unit (ALU) module is responsible
    for all computations.

    Takes int() and returns int().
"""


def add(r1, r2):
    return r1 + r2


def sub(r1, r2):
    return r1 - r2


def multi(r1, r2):
    return r1 * r2


def div(r1, r2):
    return r1 // r2


def and_operator(r1, r2):
    return r1 & r2


def or_operator(r1, r2):
    return r1 | r2


def equals(r1, r2):
    return r1 == r2


def less_than(r1, r2):
    return r1 < r2


def greater_than(r1, r2):
    return r1 > r2


def is_branch_equal_to(breg, dreg):
    return breg == dreg


def is_branch_not_equal_to(breg, dreg):
    return breg != dreg


def is_branch_zero(breg):
    return breg == 0


def is_branch_not_zero(breg):
    return breg != 0


def is_branch_positive(breg):
    return breg > 0


def is_branch_negative(breg):
    return breg < 0
