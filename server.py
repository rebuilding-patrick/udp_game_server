import socket
import time
import random
import sys
from threading import Thread
from sharing import Message

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

class Server(Thread):
    def __init__(self, address, port, input_channel, output_channel):
        Thread.__init__(self)
        self.address = address
        self.port = port
        self.host = (address, port)
        self.host_name = '%s:%s' % (address, port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.connections = ConnectionManager(output_channel)
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
            self.connections.confirm(message.index, host)  # Direct callback for ACK
            #print('Server: %s recv from %s' % (message.value, message.host_name))
        else:
            self.connections.add(data, host)
            #print('Server: Join from %s' % message.host_name)

        self.input_channel.give(message, 'logic')
        
    def get_message(self, data, host):
        raw_data = data
        data = data.decode().split('][')
        index = int(data[0])
        command_number = int(data[1])
        value = data[2]
        
        message = Message(index, command_number, value, host)
        message.raw_data = raw_data
        message.command_number = command_number

        if command_number == 0:
            message.command = 'join'
            value = value.split(':|:')
            print(data)
            print(value)
            message.username = value[0]
            message.password = value[1]

            print('Server: Join from %s' % message.host_name)

        elif command_number == 1:
            message.command = 'input'
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

            if inputs:
                print('Server: %s recv from %s at %s' % (inputs, message.host_name, message.index))

        elif command_number == 2:
            message.command = 'broadcast'

        elif command_number == 3:
            message.command = 'get_map'
            self.value = int(self.value)

        elif command_number == 4:
            message.command = 'move'
            value = self.value.split(':')
            message.x = int(value[0])
            message.y = int(value[1])

        elif command_number == 5:
            message.command = 'get_actors'

        elif command_number == 6:
            message.command = 'start_conflict'

        elif command_number == 7:
            message.command = 'join_conflict'

        elif command_number == 8:
            message.command = 'talk'

        elif command_number == 9:
            message.command = 'action'

        else:
            message.command = 'invalid'

        return message


class ConnectionManager(Thread):
    def __init__(self, output_channel):
        Thread.__init__(self)
        self.output_channel = output_channel

        self.connections = {}

    def run(self):
        while True:
            #try:
            for host in self.connections:
                if self.output_channel.has(host):
                    messages = self.output_channel.get(host)
                    for message in messages:
                        self.connections[host].send(message)
            #except:
            #    print('Connection Error')

            time.sleep(0.001)

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
        results = '%s][%s][%s' % (0, 0, self.token)
        self.send_data(results.encode())

    def send_data(self, data):
        try:
            self.socket.sendto(data, self.host)
            #print('Conn %s: sent %s' % (self.host_name, data.decode()))
        except:
            print('Conn %s: error sending %s' % (self.host_name, data.decode()))

    def send(self, message):
        packet = message.get_packet()
        self.message_index += 1
        self.send_data(packet)