from threading import Thread
import time


class Logic(Thread):
    def __init__(self, channel):
        Thread.__init__(self)
        self.inputs = channel.inputs
        self.outputs = channel.outputs
        self.tick = 0

        self.messages = []

    def get_tick(self):
        return self.tick

    def run(self):
        while True:
            time.sleep(0.1)
            self.tick += 1

            try:
                if self.inputs.can_get():
                    self.messages = self.inputs.get()

                    for message in self.messages:
                        self.outputs.give(message)
            except:
                print('Logic error')