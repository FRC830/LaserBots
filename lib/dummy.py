""" Dummy replacements for unavailable libraries, used for testing """

class gpio(object):
    OUT = None
    BOARD = None
    @staticmethod
    def setmode(*args): pass
    @staticmethod
    def setup(*args): pass
    class PWM(object):
        def __init__(*args): pass
        def start(*args): pass
