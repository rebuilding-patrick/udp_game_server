import socket, time
from threading import Thread



class Server(Thread):
    def __init__(self, address, port, clients, postman):
        Thread.__init__(self)

        self.address = address
        self.port = port
        self.host = (address, port)
        self.host_name = '%s:%s' % (address, port)

        self.clients = clients
        self.postman = postman

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def encode_data(self, command, data):
        data = '%s][%s][%s' % (self.postman.get_time(), command, data)
        return data.encode()

    def send_data(self, command, data, host):
        self.socket.sendto(self.encode_data(command, data), host)
        print('Sent %s to %s:%s' % (data, host[0], host[1]))

    def parse_data(self, data):
        return data.decode().split('][')

class Input_Server(Server):
    def __init__(self, address, port, clients, postman):
        Server.__init__(self, address, port, clients, postman)


    def run(self):
        self.socket.bind(self.host)
        while True:
            print('Server: Waiting for data')
            data, host = self.socket.recvfrom(1024)
            self.handle_input(data, host)

    def handle_input(self, data, host):
        data = self.parse_data(data)

        if self.clients.has(host):
            self.on_client_message(data, host)
        else:
            self.on_client_join(data, host)

    def on_client_join(self, data, host):
        client = self.clients.add(data, host)

        print('Server: Join from %s:%s' % (host[0], host[1]))

        self.send_data(0, client.token, host)  # handshake

    def on_client_message(self, data, host):
        self.postman.lock.acquire()
        self.postman.give_data(data, host)
        self.postman.lock.release()


class Output_Server(Server):
    def __init__(self, address, port, clients, postman):
        Server.__init__(self, address, port, clients, postman)

    def run(self):
        while True:
            self.postman.lock.acquire()
            outbox = self.postman.get_outbox()
            self.postman.lock.release()
            self.handle_output(outbox)
            time.sleep(0.5)

    def handle_output(self, outbox):
        for data, host in outbox:
            for host in self.clients.getall():
                self.send_data(0, data, host)
