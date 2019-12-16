
from threading import Thread
import time
import socket


class Message:
   def __init__(self, host, data, time, index, command, args):
      self.host = host #IPAddress:Host
      self.data = data #Stirng

      self.time = time #Int
      self.index = index #Int
      self.command = command #String
      self.args = args #Array of Strings


class MessagePool:
   def __init__(self, size):
      self.size = size
      self.index = -1
      self.pool = []

      null_ip = ("0.0.0.0", 0)
      null_msg = Message(null_ip, "null", -1, 0, "null", [])
      for i in range(size):
         self.pool.append(null_msg)

   def advance(self):
      self.index += 1
      if self.index >= self.size:
         self.index = 0
      return self.index

   def getat(self, index):
      return self.pool[index]

   def get(self):
      return self.pool[index]

   def set(self, index, message):
      self.pool[index] = message

   def add(self, message):
      self.advance()
      self.pool[self.index] = message


class Parser:
   def __init__(self, clock):
      self.clock = clock
      self.delimiter = b"/"
      host = ("127.0.0.1", 0)
      self.bad_message = Message(host, "bad message", 0, 0, "-999", [])

   def encode(self, command, data, index=0):
      return f"{data}/{command}/{index}/{self.clock.time}".encode()

   def decode(self, data, host):
      #try:
      args = data.split(self.delimiter)
      time = int(args.pop())
      index = int(args.pop())
      command = args.pop()

      return Message(host, data, time, index, command, args)
      #except:
      #   print(f"Network: Error parsing packet {data} from {host}")
      #   return self.bad_message


class Connection:
   def __init__(self, address, port):
      self.address = address
      self.port = port
      self.host_name = f"{address}:{port}"
      self.host = (address, port)
      self.history = MessagePool(200)
      self.last = 0
      self.warnings = 0

   def log(self, message):
      self.history.add(message)
      self.last = message.time

   def check(self, time):
      if time - self.last > 5:
         print(f"Warning {self.warnings}")
         self.warnings += 1
      else:
         self.warnings = 0
      return self.warnings

#TODO I think the network should have some way to send guarenteed messages and then most messages are broadcast as is.
#Should the rebroadcast occur on the game or in the network? Both?
class Network:
   def __init__(self, address, port, clock):    
      self.parser = Parser(clock)
      self.connections = {}
      self.connection = Connection(address, port)
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.resending = {}
      self.index = 0

   def bind(self):
      try:
         print(f"Network: Starting on {self.connection.host_name}")
         self.socket.bind((self.connection.address, self.connection.port))
      except:
         print("Network: Failed to start")

   def recv(self):
      #try:
      packet = self.socket.recvfrom(1024)
      message = self.parser.decode(packet[0], packet[1])
      if message.index > 0:
         if message.index in self.resending:
            del self.resending[message.index]

      return message
      #except:
      #   print("Network: err recv")

   def promise(self, command, data, host):
      self.index += 1
      self.resending[index] = (host, self.praser.encode(command, data, index))

   def resend(self):
      for packet in self.resending:
         self.sendto_data(packet[1], packet[0])

   def sendto_data(self, data, host):
      #try:
      #print(f"Network: Sending {message.data} to {host}")
      self.socket.sendto(data, host)
      #except:
      #   print("Network: err sending")

   def sendto(self, command, data, host):
      msg = self.parser.encode(command, data)
      self.sendto_data(msg, host)

   def send(self, command, data):
      msg = self.parser.encode(command, data)
      self.sendto_data(msg, self.connection.host)

   def send_data(self, data):
      self.sendto_data(data, self.connection.host)

   def sendall_data(self, data):
      for con in self.connections:
         self.send_data(data, con)

   def sendall(self, command, data):
      msg = self.parser.encode(command, data)
      self.sendall_data(msg)

