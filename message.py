class MessagePool:
    def __init__(self, size):
        self.size = size
        self.index = 0
        self.pool = []
        for i in range(size):
            self.pool.append(Message())


    def get(self, index=0, command=0, value=0, host=(0,0)):
        message = self.pool[self.index]
        message.update(index, command, value, host)
        self.index += 1
        self.index = self.index % self.size
        return message

    def get_copy(self, message):
        return self.get(message.index, message.command, message.value, message.host)

    

class Message:
    def __init__(self, index=0, command=0, value=0, host=(0, 0)):
        self.index = index
        self.command = command
        self.value = value
        self.values = {}
        self.host = host
        self.host_name = '%s#%s' % (host[0], host[1])

    def update(self, index=0, command=0, value=0, host=(0, 0)):
        self.__init__(index, command, value, host)

    def get_packet(self):
        packet = '%s/%s/%s' % (self.index, self.command, self.value)
        return packet.encode()

    def get_value(self, key):
        return self.values[key]
