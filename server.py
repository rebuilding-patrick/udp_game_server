import socket
import connection
import sharing
from threading import Thread


class Server(Thread):
    def __init__(self, address, port):
        Thread.__init__(self)
        self.address = address
        self.port = port
        self.host = (address, port)
        self.host_name = '%s:%s' % (address, port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.inputs = sharing.SharedList()
        self.outputs = sharing.SharedList()
        self.connections = connection.Manager(self.outputs)
        self.connections.start()

    def run(self):
        self.socket.bind(self.host)
        while True:
            print('Server: Waiting for data')

            try:
                data, host = self.socket.recvfrom(1024)
                self.handle_input(data, host)
            except Error:
                print('Server: Input error')

    def handle_input(self, data, host):
        if self.connections.has(host):
            self.on_client_message(data, host)
        else:
            self.on_client_join(data, host)

    def on_client_join(self, data, host):
        try:
            self.connections.add(data, host)
            print('Server: Join from %s:%s' % (host[0], host[1]))
        except Error:
            print('Server: Bad join')

    def on_client_message(self, data, host):
        try:
            message = sharing.Message(data, host)
            self.inputs.give(message)
            self.connections.confirm(message.index, host)  # Direct callback for ACK
            print('Server: %s recv from %s' % (message.value, message.host_name))
        except Error:
            print('Server: Bad message')