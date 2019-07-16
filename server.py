import socket
from sharing import *
from threading import Thread


PING_RATE = 10
CONNECTION_WARN_RATE = 50
TIMEOUT_WARNINGS_TO_KILL = 3


class Server(Thread):
    def __init__(self, address, port, game):
        Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.address = address
        self.port = port
        self.host = (address, port)
        self.host_name = '%s:%s' % (address, port)

        self.game = game
        self.input_channel = game.input_channel
        self.output_channel = game.output_channel
        self.message_pool = MessagePool(15*8*3)  # 15msg a second in, 8 clients, 3 second buffer

        self.connections = ConnectionManager(self)
        self.connections.start()

    def run(self):
        self.socket.bind(self.host)
        print('Server: Waiting for data')

        while True:
            #print('Server: Waiting for data')

            #try:
            data, host = self.socket.recvfrom(1024)
            self.handle_input(data, host)
            #except:
            #    print('Server: Input error')

            time.sleep(0.001)

    def handle_input(self, data, host):
        message = self.get_message(data, host)
        if self.connections.has(host):
            self.connections.confirm(host)  # Direct callback for ACK
            #print('Server: %s recv from %s' % (message.value, message.host_name))
        else:
            self.connections.add(data, host)
            print('Server: New connection from %s' % message.host_name)

        self.input_channel.give(message, 'game')

    def get_message(self, data, host):
        raw_data = data
        data = data.decode().split('][')
        index = int(data[0])
        command = int(data[1])
        value = data[2]

        message = self.message_pool.get(index, command, value, host)
        message.values['raw_data'] = raw_data

        return message


class ConnectionManager(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.input_channel = server.input_channel
        self.output_channel = server.output_channel
        self.host = server.host

        self.message_pool = MessagePool(15 * 8 * 3)  # 15msg/sec, 8 clients, 3 second buffer
        self.clock = Clock(PING_RATE)
        self.connections = {}


    def run(self):
        while True:
            #try:
            if self.clock.tick():
                self.check_connections()

            connections = self.connections
            for host in connections:
                messages = self.output_channel.get(host)
                for message in messages:
                    connections[host].send(message)

            #except:
            #    print('Connection Error')

            time.sleep(0.001)

    def confirm(self, host):
        self.connections[host].last_msg = self.clock.value
        self.connections[host].timeout_warnings = 0

    def check_connections(self):
        print('Server: Checking connections')
        healthy_connections = {}

        for host in self.connections:
            connection = self.connections[host]
            if connection.check_connection(self.clock.value) < CONNECTION_WARN_RATE:
                healthy_connections[host] = connection
            else:
                connection.timeout_warnings += 1
                if connection.timeout_warnings < TIMEOUT_WARNINGS_TO_KILL:
                    print('Server: Timeout warning from %s:%s' % host)
                    healthy_connections[host] = connection
                else:
                    print('Server: Disconnect from %s:%s' % host)

        self.connections = healthy_connections

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
        self.timeout_warnings = 0
        self.last_msg = -1

        self.handshake()

    def check_connection(self, tick):  # returns ticks since last message
        return tick - self.last_msg


    def handshake(self):
        return

    def send(self, message):
        packet = message.get_packet()
        self.send_data(packet)

    def send_data(self, data):
        try:
            self.socket.sendto(data, self.host)
            #print('Conn %s: sent %s' % (self.host_name, data.decode()))
        except:
            print('Conn %s: error sending %s' % (self.host_name, data.decode()))
