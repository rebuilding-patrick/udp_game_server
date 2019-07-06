import socket

class Client:
    def __init__(self, index):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.index = index


    def create_message(self, message_index, command, data):
        return '%s][%s][%s' % (message_index, command, data)

    def decode_data(self, data):
        return str(data).split('][')
        
        
    def connect(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (ip, port)
        print('Connected to %s' % str(self.address))

    def send(self, message):
        self.socket.sendto(message.encode(), self.address)
        print('Sent %s' % str(message))

    def recv(self):
        raw_data, server = self.socket.recvfrom(1024)

        print('Recv %s from %s' % (raw_data.decode(), server))





        
joins = 0
msgs = 0
clients = []
for i in range(10):
    client = Client(i)
    clients.append(client)
    client.connect('localhost', 45456)
    message = client.create_message(0, 0, 'User%s' % i)
    client.send(message)
    client.recv()
    joins += 1

for client in clients:
    greeting = 'Yo it\'s %s' % client.index
    message = client.create_message(0, 2, greeting)
    client.send(message)
    client.recv()
    msgs += 1

print('Joins %s' % joins)
print('Messages %s' % msgs)

while clients:
    for client in clients:
        client.recv()
        msgs += 1
    print('Messages %s' % msgs)
