# ------------- #
# -- Options -- #
# -- 1, 2, 4 -- #
# ------------- #

CPU_COUNT = 4

# ---------------- #
# -- Scheduling
# -- FIFO
# -- SJF
# -- Priority
# ---------------- #

SCHEDULING_TYPE = 'SJF'

# --------------- #
# -- PAGE SIZE -- #
# --------------- #

PAGE_SIZE = 4

# ---------------- #
# -- PCB States -- #
# ---------------- #

NEW_STATE = 'NEW_STATE'
READY_STATE = 'READY_STATE'
WAITING_STATE = 'WAITING_STATE'
RUNNING_STATE = 'RUNNING_STATE'
ENDED_STATE = 'ENDED_STATE'

# ------------------------------------------ #
# -- Tie some value to the EMPTY constant -- #
# ------------------------------------------ #

EMPTY = None

# ---------------------------- #
# -- Initialize DUMP object -- #
# ---------------------------- #

from os_.output import Output

CORE_DUMPS = Output()

# ----------------------------- #
# -- Initialize Stats object -- #
# ----------------------------- #

from os_.statistics import Statistics

statistics = Statistics()
