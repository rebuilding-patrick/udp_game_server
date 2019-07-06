import time
import socket
import random
import sys
from threading import Thread, Lock


class Manager(Thread):
    def __init__(self, outputs):
        Thread.__init__(self)
        self.outputs = outputs

        self.lock = Lock()
        self.connections = {}

    def run(self):
        while True:
            try:
                if self.outputs.can_get():
                    output = self.outputs.get()
                    self.handle_output(output)
            except:
                print('Connection Error')

            time.sleep(0.1)

    def handle_output(self, output):
        for message in output:
            self.connections[message.host].send(message)

    def confirm(self, index, host):
        self.connections[host].last_msg = index

    def add(self, data, host):
        conn = Connection(host)
        self.connections[host] = conn
        return conn

    def get(self, host):
        return self.connections[host]

    def has(self, host):
        return host in self.connections

    def getall(self):
        return self.connections


class Connection:
    def __init__(self, host):
        self.host = host
        self.address = host[0]
        self.port = host[1]
        self.host_name = '%s:%s' % (host[0], host[1])

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.message_index = 0
        self.message_queue = []
        self.alive = 2
        self.last_msg = -1

        random.seed = self.host_name
        self.token = random.randint(0, sys.maxsize)

        self.handshake()

    def handshake(self):
        self.send_data(str(self.token).encode())

    def send_data(self, data):
        try:
            self.socket.sendto(data, self.host)
            print('Conn %s: sent %s' % (self.host_name, data.decode()))
        except:
            print('Conn %s: error sending %s' % (self.host_name, data.decode()))

    def send(self, message):
        packet = message.get_packet(self.message_index)
        self.message_index += 1
        self.send_data(packet)

