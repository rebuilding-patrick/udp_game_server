from threading import Lock


class SharedList:
    def __init__(self):
        self.lock = Lock()
        self.items = {}

    def give(self, message, address):
        if not self.has(address):
            self.items[address] = []
        self.items[address].append(message)

    def has(self, address):
        results = False
        if address in self.items:
            if len(self.items[address]) > 0:
                results = True
        return results

    def get(self, address):
        self.lock.acquire()
        items = self.items[address]
        self.items[address] = []
        self.lock.release()
        return items

    def get_message(self, index, command, value, host):
        return Message(index, command, value, host)

class Message:
    def __init__(self, index, command, value, host):
        self.index = index
        self.command = command
        self.value = value
        self.host = host
        self.host_name = '%s:%s' % (host[0], host[1])

    def get_packet(self):
        packet = '%s][%s][%s' % (self.index, self.command, self.value)
        return packet.encode()

