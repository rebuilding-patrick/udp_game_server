
import time
import socket

JOIN_B = b"3"
AWK_B = b"2"
RELIABLE_B = b"1"
UNRELIABLE_B = b"0"
ERR_B = B"4"

JOIN_S = "3"
AWK_S = "2"
RELIABLE_S = "1"
UNRELIABLE_S = "0"
ERR_S = "4"

JOIN_I = 3
AWK_I = 2
RELIABLE_I = 1
UNRELIABLE_I = 0
ERR_I = 4

class Message:
   def __init__(self, index, command, args, host, data):
      self.index = index #: Int
      self.command = command #: Byte of Int
      self.args = args #: Array of Strings

      self.host = host #: IPAddress:Host
      self.data = data #: Stirng


class Parser:
   def __init__(self):
      self.delimiter = b"/"
      host = ("127.0.0.1", 0)
      self.bad_message = Message(0, b"-1", [], host, "-999")

   def encode(self, data, command, index):
      return f"{data}/{command}/{index}".encode()

   def decode(self, data, host):
      #try:
      args = data.split(self.delimiter)
      index = int(args.pop())
      command = args.pop()
      return Message(index, command, args, host, data)
      #except:
      #   print(f"Network: Error parsing packet {data} from {host}")
      #   return self.bad_message


class Connection:
   def __init__(self, address, port):
      self.address = address
      self.port = port
      self.host_name = f"{address}:{port}"
      self.host = (address, port)

      self.last = 0
      self.warnings = 0

      self.index = 0
      self.delimiter = b"|"
      self.resending = {}
      self.confirming = []
      self.awk_buffer = b""

      self.message_buffer = [b"", b"", b"", b"", b""]
      self.buffer_max = 4
      self.buffer_len = -1
      self.buffer_size = 0

   def buffer(self, data, command):
      self.index += 1
      parsed_data = f"{data}/{command}/{self.index}".encode()
      if command == RELIABLE_S or command == RELIABLE_I or command == JOIN_S or command == JOIN_I:
         self.resending[self.index] = parsed_data

      self.buffer_data(parsed_data)

   def buffer_data(self, data):
      size = len(data)
      if self.buffer_size + size > 768:
         self.buffer_size = 0
         self.buffer_len += 1
      else:
         if self.buffer_len < 0:
            self.buffer_len = 0

         if self.buffer_size > 0:
            self.message_buffer[self.buffer_len] += self.delimiter
            size += 1
         
      self.message_buffer[self.buffer_len] += data
      self.buffer_size += size

   def flush(self):
      i = 0
      while i <= self.buffer_max:
         self.message_buffer[i] = b""
         i += 1
      
      self.buffer_len = -1
      self.buffer_size = 0

   def confirm(self, index):
      if index in self.resending:
         self.confirming.append(index)

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


class Network:
   def __init__(self, address, port):    
      self.parser = Parser()
      self.connections = {}
      self.connection = Connection(address, port)
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.delimiter = b"|"

   def bind(self):
      try:
         print(f"Network: Starting on {self.connection.host_name}")
         self.socket.bind((self.connection.address, self.connection.port))
      except:
         print("Network: Failed to start")

   def handle_new_connection(self, data, host):
      self.connections[host] = Connection(data, host, None)


   def recv(self):
      #try:
      data, host = self.socket.recvfrom(1024) #TODO pool for this
      values = data.split(self.delimiter)
      #print(f"Network: recv {data} from {host}")
      messages = []
      for value in values:
         message = self.parser.decode(value, host)
         if message.command == AWK_B:  
            self.connection.confirm(message.index)

         elif message.command == RELIABLE_B:
            #TODO this should fill an awk_buffer
            self.send_data(f"awk/1/{AWK_S}/{message.index}".encode(), host)
            messages.append(message)

         elif message.command == UNRELIABLE_B:
            messages.append(message)

         elif message.command == JOIN_B:
            self.connection.confirm(message.index)
         
         else:
            print("bad message command {message.command}")

      return messages

   def buffer(self, data, host, command):
      self.connections[host].buffer(data, command)

   def flush(self):
      for connection in self.connections:
         connection.flush()

   def send_all(self):
      for conneciton in self.connections:
         self.send(connection)

   def send(self, connection):
      i = 0
      while i <= connection.buffer_len:
         self.send_data(connection.message_buffer[i], connection.host)
         connection.message_buffer[i] = b""
         i += 1
      connection.buffer_len = -1
      connection.buffer_size = 0

   def send_data(self, data, host):
      #try:
      #print(f"Network: Sending {data} to {host}")
      self.socket.sendto(data, host)
      #except:
      #   print("Network: err sending")

   def resend_all(self):
      for connection in self.connections:
         self.resend(connection)

   def resend(self, connection):
      if connection.confirming:
         for index in connection.confirming:
            if index in connection.resending:
               del connection.resending[index]
            else:
               print(f"Network: Resend error deleting {index} from connection.resending (but in connection.confirming)")
               #TODO figure this out
         connection.confirming = []

      for index in connection.resending:
         self.send_data(connection.resending[index], connection.host)

