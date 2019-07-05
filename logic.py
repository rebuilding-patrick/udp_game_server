from threading import Thread
import time

class Logic(Thread):
    def __init__(self, postman):
        Thread.__init__(self)
        self.postman = postman

        self.state = 0

        self.messages = []

    def get_state(self):
        return self.state

    def run(self):
        while True:
            self.state += 1
            time.sleep(1)

            self.postman.lock.acquire()
            self.messages = self.postman.get_inbox()
            if self.messages:
                print('Logic: Messages recv')

            for message in self.messages:
                state = '%s %s' % (self.state, message.value)
                self.postman.give_state(state, message.host)
                print('Logic: %s outgoing to %s' %(state, message.host))
            self.postman.lock.release()