import logic
import server

#######
#Message Pattern
#######
# '1][2][hello'
# string.split('][')
# message_index, message_command, message_data
#######
# Message Commands Key
#######
# -1 = invalid command
# 0 = join command
# 1 = move command
# 2 = broadcast command
# 3 = whisper command
# 4 = attack command
#Hello


class Game:
    def __init__(self):
        self.server = server.Server('localhost', 45456)
        self.logic = logic.Logic(self.server)


    def start(self):
        self.server.start()
        self.logic.start()

        
game = Game()
game.start()
