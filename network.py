
from threading import Thread
import time
import socket


class Packet:
   def __init__(self, data, host):
      self.data = data
      self.host = host


class PacketPool:
   def __init__(self, size):
      self.size = size
      self.index = -1
      self.pool = []

      null_packet = Packet("null", ("0.0.0.0", 0))
      for i in range(size):
         self.pool.append(null_packet)

   def advance(self):
      self.index += 1
      if self.index >= self.size:
         self.index = 0
      return self.index

   def geti(self, index):
      return self.pool[index]

   def get(self):
      return self.pool[index]

   def set(self, index, packet):
      self.pool[index] = packet

   def add(self, packet):
      self.advance()
      self.pool[self.index] = packet


class Connection:
   def __init__(self, address, port):
      self.address = address
      self.port = port
      self.host_name = f"{address}:{port}"
      self.host = (address, port)
      self.history = PacketPool(200)
      self.last = 0
      self.warnings = 0

   def log(self, packet, time):
      self.history.add(packet)
      self.last = time

   def check(self, time):
      if time - self.last > 10:
         self.warnings += 1
      else:
         self.warnings = 0
      return self.warnings

#TODO I think the network should have some way to send guarenteed packets and then most packets are broadcast as is.
#Should the rebroadcast occur on the game or in the network? Both?
class Network:
   def __init__(self, address, port):    
      self.connections = {}
      self.connection = Connection(address, port)
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
   def bind(self):
      try:
         print(f"Network: Starting on {self.connection.host_name}")
         self.socket.bind((self.connection.address, self.connection.port))
      except:
         print("Network: Failed to start")

   def recv(self):
      try:
         data, host = self.socket.recvfrom(1024)
         #print(f"Network: recv {data} from {host}")
         packet = Packet(data, host)
         self.log(packet)
         return packet
      except:
         print("Network: err recv")

   def send(self, packet):
      #try:
      #print(f"Network: Sending {packet.data} to {host}")
      self.socket.sendto(packet.data, packet.host)
         #self.connection.log(packet, self.clock.time)
      #except:
      #   print("Network: err sending")

   def sendto(self, data, host):
      #try:
      #print(f"Network: Sending {data} to {host}")
      self.socket.sendto(data, host)
         #self.connection.log(packet, self.clock.time)
      #except:
      #   print("Network: err sending")
      
   def send_data(self, data):
      self.sendto(data, self.connection.host)

   def sendall(self, data):
      #try:
      #print(f"Sending all #{data}")
      for con in self.connections:
         self.sendto(data, con)
      #except:
      #   print("Network: err sendall")

   def log(self, packet):
      if packet.host in self.connections:
         #self.connections[packet.host].log(packet, self.clock.time.value)
         return
      else:
         self.connections[packet.host] = Connection(packet.host[0], packet.host[1])

   def check_connections(self):
      print("Server: Checking connections")
      dead = []
      time = 1 #self.clock.time.value
      for con in self.connections:
         warnings = con[1].check(time)
         if warnings > 2:
            print("Server: #{con.host} has timed out")
            dead.append(con[0])
         elif warnings > 0:
            print("Server: Timeout warning for #{con.host}")

      for host in dead:
         self.connections.delete(host)

