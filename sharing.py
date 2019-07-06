from threading import Lock


class SharedList:
    def __init__(self):
        self.lock = Lock()
        self.items = []

    def give(self, item):
        self.items.append(item)

    def can_get(self):
        return len(self.items) > 0

    def get(self):
        self.lock.acquire()
        items = self.items
        self.items = []
        self.lock.release()
        return items


class Message:
    def __init__(self, data, host):
        self.raw_data = data
        data = data.decode().split('][')

        self.index = data[0]
        self.command = data[1]
        self.value = data[2]

        self.host = host
        self.host_name = '%s:%s' % (host[0], host[1])

    def get_packet(self, index):
        packet = '%s][%s][%s' % (index, self.command, self.value)
        return packet.encode()

