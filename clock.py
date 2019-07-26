#import numpy
import ctypes
import time



class Clock:
    def __init__(self, rate):
        self.tick_rate = rate

        #self.value = numpy.int64(0)
        self.value = ctypes.c_ulong(0)
        self.last_tick = time.time()

    def get_value(self):
        return self.value.value

    def tick(self):
        results = False
        current_time = time.time()
        if current_time - self.last_tick > self.tick_rate:
            results = True
            self.last_tick = current_time
            self.value.value += 1
        return results
