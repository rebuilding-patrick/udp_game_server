import random, sys
from threading import RLock


class Client:
    def __init__(self, username, host):
        self.username = username
        self.host = host
        self.address = host[0]
        self.port = host[1]
        self.host_name = '%s:%s' % (host[0], host[1])

        seed = '%s:%s' % (username, self.host_name)
        random.seed(seed)
        self.token = random.randint(0, sys.maxsize)

class Manager:
    def __init__(self):
        self.lock = RLock()
        self.clients = {}

    def add(self, username, host):
        client = Client(username, host)
        self.clients[host] = client
        return client

    def get(self, host):
        return self.clients[host]

    def has(self, host):
        return host in self.clients

    def getall(self):
        return self.clients
