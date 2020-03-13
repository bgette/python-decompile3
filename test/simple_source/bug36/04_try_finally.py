# From 3.6 _pyio.py
# Bug was in "return" not having "COME_FROM"
# and in 1st try/finally no END_FINALLY (which really
# hooks into the control-flow analysis).
# The 2nd try/finally has an END_FINALLY although still
# no "COME_FROM".

# RUNNABLE!
def getvalue():
    try:
        return 3
    finally:
        return 1

assert getvalue() == 1

def getvalue1():
    try:
        return 4
    finally:
        pass
    return 2

assert getvalue1() == 4

def getvalue1():
    try:
        return 4
    finally:
        pass
    return 2

assert getvalue1() == 4

# from 3.7.6 test_grammar.py
def g1():
    try:
        pass
    finally:
        return 1
    return 2

assert g1() == 1

# From Python 3.6 asynchat.py
# Bug is handling as why in the face of a return.
# decompyle3 shows removal of "why" after the return.
def handle_read(self):
    try:
        data = 5
    except ZeroDivisionError:
        return
    except OSError as why:
        return why

    return data

# From 3.6 contextlib
# Bug is indentation of "return exc"
# Also there are extra statements to remove exec,
# which we hide (unless doing fragments).
# Note: The indentation bug may be a result of using improper
# grammar.
def __exit__(self, type, value, traceback):
    try:
        value()
    except StopIteration as exc:
        return exc
    except RuntimeError as exc:
        return exc
    return
