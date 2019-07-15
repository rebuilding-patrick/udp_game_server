import socket
import time

from threading import Thread
from sharing import Message, Clock

up = 1 << 0
down = 1 << 1
left = 1 << 2
right = 1 << 3
shift = 1 << 4
ctrl = 1 << 5

accept = 1 << 0
select = 1 << 1
r = 1 << 2
f = 1 << 3
q = 1 << 4
e = 1 << 5
z = 1 << 6
tab = 1 << 7
esc = 1 << 8

PING_RATE = 100
CONNECTION_WARN_RATE = 50
TIMEOUT_WARNINGS_TO_KILL = 3

GET_WORLD_COMMAND = -1
JOIN_COMMAND = 0
UPDATE_PLAYER_COMMAND = 1
UPDATE_PLAYERS_COMMAND = 2
PLAYER_INPUT_COMMAND = 3
GET_ACTORS_COMMAND = 4
GET_ACTOR_COMMAND = 5
MESSAGE_COMMAND = 6


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

        message = Message(index, command, value, host)
        message.raw_data = raw_data

        if command == PLAYER_INPUT_COMMAND:
            value = value.split(':')
            directions = int(value[0])
            buttons = int(value[1])
            inputs = {}

            if directions & up:
                inputs['up'] = True
            if directions & down:
                inputs['down'] = True
            if directions & left:
                inputs['left'] = True
            if directions & right:
                inputs['right'] = True
            if directions & shift:
                inputs['shift'] = True
            if directions & ctrl:
                inputs['ctrl'] = True

            if buttons & accept:
                inputs['accept'] = True
            if buttons & select:
                inputs['select'] = True
            if buttons & r:
                inputs['r'] = True
            if buttons & f:
                inputs['f'] = True
            if buttons & q:
                inputs['q'] = True
            if buttons & e:
                inputs['e'] = True
            if buttons & z:
                inputs['z'] = True
            if buttons & tab:
                inputs['tab'] = True
            if buttons & esc:
                inputs['esc'] = True

            message.inputs = inputs

            #if inputs:
            #    print('Server: %s recv from %s at %s' % (inputs, message.host_name, message.index))

        elif command == GET_ACTORS_COMMAND:
            pass

        elif command == GET_ACTOR_COMMAND:
            pass

        elif command == MESSAGE_COMMAND:
            pass

        elif command == JOIN_COMMAND:
            value = value.split(':|:')
            message.username = value[0]
            message.password = value[1]

            print('Server: Join from %s at %s' % (message.username, message.host_name))

        elif command == GET_WORLD_COMMAND:

            print('Server: World request from %s' % message.host_name)

        return message


class ConnectionManager(Thread):
    def __init__(self, server):
        Thread.__init__(self)
        self.input_channel = server.input_channel
        self.output_channel = server.output_channel
        self.host = server.host

        self.clock = Clock(1/15.0)
        self.connections = {}


    def run(self):
        while True:
            #try:
            if self.clock.tick():
                message = Message(self.clock.value, UPDATE_PLAYERS_COMMAND, 'new_turn', self.host)
                self.input_channel.give(message, 'game')

                if self.clock.value % PING_RATE == 0:
                    self.check_connections()

            connections = self.connections
            for host in connections:
                    if self.output_channel.has(host):
                        messages = self.output_channel.get(host)
                        for message in messages:
                            connections[host].send(message, self.clock.value)

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

    def send(self, message, tick):
        packet = message.get_packet(tick)
        self.send_data(packet)

    def send_data(self, data):
        try:
            self.socket.sendto(data, self.host)
            #print('Conn %s: sent %s' % (self.host_name, data.decode()))
        except:
            print('Conn %s: error sending %s' % (self.host_name, data.decode()))
