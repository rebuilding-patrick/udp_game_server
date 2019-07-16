from threading import Lock
import time
import numpy

GET_WORLD_COMMAND = -1
JOIN_COMMAND = 0
UPDATE_PLAYER_COMMAND = 1
UPDATE_PLAYERS_COMMAND = 2
PLAYER_INPUT_COMMAND = 3
ACTOR_INPUT_COMMAND = 4
GET_ACTORS_COMMAND = 5
GET_ACTOR_COMMAND = 6
MESSAGE_COMMAND = 7
ADD_ACTOR_COMMAND = 8

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

up_key = 1 << 0
down_key = 1 << 1
left_key = 1 << 2
right_key = 1 << 3
shift_key = 1 << 4
ctrl_key = 1 << 5

accept_key = 1 << 0
select_key = 1 << 1
r_key = 1 << 2
f_key = 1 << 3
q_key = 1 << 4
e_key = 1 << 5
z_key = 1 << 6
tab_key = 1 << 7
esc_key = 1 << 8

class Clock:
    def __init__(self, rate):
        self.tick_rate = rate

        self.value = numpy.int64(0)
        self.last_tick = time.time()

    def tick(self):
        results = False
        current_time = time.time()
        if current_time - self.last_tick > self.tick_rate:
            results = True
            self.last_tick = current_time
            self.value += 1
        return results


class SharedList:
    def __init__(self):
        self.lock = Lock()
        self.items = {}

    def give(self, message, address):
        if not self.has(address):
            self.items[address] = []
        self.items[address].append(message)

    def has(self, address):
        results = False
        if address in self.items:
            if len(self.items[address]) > 0:
                results = True
        return results

    def get(self, address):
        self.lock.acquire()
        if address in self.items:
            items = self.items[address]
        else:
            items = []
        self.items[address] = []
        self.lock.release()
        return items

    def get_message(self, index, command, value, host):
        return Message(index, command, value, host)


class MessagePool:
    def __init__(self, size):
        self.size = size
        self.index = 0
        self.pool = []
        for i in range(size):
            self.pool.append(Message(0, 0, 0, (0, 0)))

    def get(self, index, command, value, host):
        message = self.pool[self.index]
        message.update(index, command, value, host)
        self.index += 1
        self.index = self.index % self.size
        return message


class Message:
    def __init__(self, index, command, value, host):
        self.index = index
        self.command = command
        self.value = value
        self.values = {}
        self.host = host
        self.host_name = '%s:%s' % (host[0], host[1])

    def update(self, index, command, value, host):
        self.__init__(index, command, value, host)

    def get_packet(self):
        packet = '%s][%s][%s' % (self.index, self.command, self.value)
        return packet.encode()

