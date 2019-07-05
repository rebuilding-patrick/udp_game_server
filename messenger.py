import sys, time
from threading import Thread, RLock

class Message:
    def __init__(self, data, host):
        self.raw_data = data
        self.timestamp = data[0]
        self.command = data[1]
        self.value = data[2]

        self.host = host
        self.host_name = '%s:%s' % (host[0], host[1])

class Postman(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = RLock()
        
        self.inbox = []
        self.outbox = []
        self.timestamp = 0

    def give_message(self, message):
        self.inbox.append(message)

    def give_data(self, data, host):
        message = Message(data, host)
        self.give_message(message)

    def give_state(self, state, host):
        self.outbox.append((state, host))

    def get_inbox(self):
        inbox = self.inbox
        self.inbox = []
        return inbox

    def get_outbox(self):
        outbox = self.outbox
        self.outbox = []
        return outbox

    def get_time(self):
        return self.timestamp

    def run(self):
        print('Postman: Keeping time')
        while True:
            self.timestamp += 1

            if self.timestamp % 10 == 0:
                print('Postman: Tick %s' % self.timestamp)

            if self.timestamp > sys.maxsize:
                self.timestamp = 0

            time.sleep(1)