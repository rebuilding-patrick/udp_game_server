import socket
import time
import select
from clock import Clock
from message import MessagePool
from message import Message
from constants import *

from threading import Thread

class Connection:
    def __init__(self, host=None):
        if host:
            self.set_host(host[0], host[1])
        else:
            self.host = None
            self.address = None
            self.port = None
            self.host_name = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.message_pool = MessagePool(15 * 10)  # 15msg/sec, 10 second buffer (large for testing)  
        self.message_index = 0
        self.message_queue = []
        self.timeout_warnings = 0
        self.index = -1

    def set_host(self, address, port):
        self.address = address
        self.port = port
        self.host = address, port
        self.host_name = '%s:%s' % (address, port)

    def bind(self):
        self.socket.bind(self.host)

    def handshake(self):
        return

    def check_connection(self, tick):  # returns ticks since last message
        return tick - self.index

    def confirm(self, index):
        self.index = index
        self.timeout_warnings = 0

    def send(self, message):
        packet = message.get_packet()
        self.message_pool.get_copy(message)
        self._send_data(packet)

    def send_value(self, index, command, value):
        text = '%s/%s/%s' % (index, command, value)
        self.message_pool.get(index, command, value, self.host)
        self._send_data(text.encode())

    # Don't use this method directly as it bypasses logging
    # Use send or send_value instead
    def _send_data(self, data):
        try:
            self.socket.sendto(data, self.host)
            print('Conn %s: sent %s' % (self.host_name, data.decode()))
        except:
            print('Conn %s: error sending %s' % (self.host_name, data.decode()))

    def recv(self):
        data, host = self.socket.recvfrom(1024)
        message = self.handle_data(data, host)

        print('%s recv from %s' % (data, host))
        return message

    def handle_data(self, data, host):
        raw_data = data
        data = data.decode().split('/')
        index = int(data[0])
        command = int(data[1])
        value = data[2].split('|')
        i = 0
        for string in value:
            value[i] = string.split(':')
            i2 = 0
            for substring in value[i]:
                value[i][i2] = substring.split('#')
                i2 += 1
            i += 1

        message = self.message_pool.get(index, command, value, host)
        message.values['raw_data'] = raw_data

        return message


class Client(Thread):
    def __init__(self, game):
        Thread.__init__(self)

        self.game = game
        self.input_channel = game.input_channel
        self.output_channel = game.output_channel

        self.connection = Connection()

    def run(self):
        print('Client: Waiting for data')
        socket = (self.connection.socket,)
        while True:
            readable, writeable, exception = select.select(socket, socket, socket)
            
            if readable:
                message = self.connection.recv()
                self.handle_input(message)

            messages = self.output_channel.get('server')
            if messages and writeable:
                self.handle_output(messages)

            if exception:
                self.handle_exception()

            time.sleep(0.001)

    def set_host(self, address, port):
        self.connection.set_host(address, port)

    def handle_input(self, message):
        self.connection.confirm(message.index)
        self.input_channel.give(message, 'game')

    def handle_output(self, messages):
        for message in messages:
            self.connection.send(message)

    def handle_exception(self):
        print('Client socket error')

    def send(self, message):
        message.index = self.client.connection.index
        self.connection.send(message)

    def send_value(self, command, value):
        index = self.client.connection.index
        self.connection.send_value(index, command, value)

    def query_server(self):
        self.connection.send_value(-1, WORLD_INFO_COM, 'world_get')
        message = self.connection.recv()
        return message

    def login_server(self,username, password):
        value = '%s:%s' % (username, password)
        self.connection.send_value(-2, LOGIN_COM, value)
        message = self.connection.recv()
        return message

    def join_server(self, username, password):
        value = '%s:%s' % (username, password)
        self.connection.send_value(0, JOIN_COM, value)
        self.start()

    def message(self, command, value):
        message = connection.message_pool.get(-1, command, value, self.host)
        return message


class Server(Thread):
    def __init__(self, address, port, game):
        Thread.__init__(self)
        self.incoming = Connection((address, port))
        self.incoming.bind()

        game.server = self
        self.game = game
        self.input_channel = game.input_channel
        self.output_channel = game.output_channel

        self.outgoing = OutputManager(self)

    def run(self):
        print('Server: Waiting for data')
        self.outgoing.start()
        while True:
            #try:
            message = self.incoming.recv()
            self.handle_message(message)
            #except:
            #    print('Server: Input error')

            time.sleep(0.001)

    def handle_message(self, message):
        if self.outgoing.has(message.host):
            self.outgoing.confirm(message.host)  # Direct callback for ACK
            print('Server: %s recv from %s' % (message.value, message.host_name))
        else:
            self.outgoing.add(message.host)
            print('Server: New connection from %s:%s' % (message.value, message.host_name))

        self.input_channel.give(message, 'game')

    def send(self, message):
        self.outgoing.send(messsage)

    def send_value(self, command, value, host):
        self.outgoing.send_value(command, value, host)


class OutputManager(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.input_channel = server.input_channel
        self.output_channel = server.output_channel

        self.clock = Clock(PING_RATE)
        self.connections = {}

    def __getitem__(self, key):
        return self.connections[key]

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
        self.connections[host].confirm(self.clock.get_value())

    def check_connections(self):
        print('Server: Checking connections')
        healthy_connections = {}

        for host in self.connections:
            connection = self.connections[host]
            if connection.check_connection(self.clock.get_value()) < CONNECTION_WARN_RATE:
                healthy_connections[host] = connection
            else:
                connection.timeout_warnings += 1
                if connection.timeout_warnings < TIMEOUT_WARNINGS_TO_KILL:
                    print('Server: Timeout warning from %s:%s' % host)
                    healthy_connections[host] = connection
                else:
                    print('Server: Disconnect from %s:%s' % host)

        self.connections = healthy_connections

    def add(self, host):
        conn = Connection(host)
        self.connections[host] = conn
        return conn

    def get(self, host):
        return self.connections[host]

    def has(self, host):
        return host in self.connections

    def getall(self):
        return self.connections

    def get_message(self, tick, command, value, host):
        return self.connections[host].message_pool.get(tick, command, value, host)

    def send(self, message):
        message.index = self.clock.get_value()
        self.connections[message.host].send(message)

    def send_value(self, command, value, host):
        index = self.clock.get_value()
        self.connections[host].send_value(index, command, value)

