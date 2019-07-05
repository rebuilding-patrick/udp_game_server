import client, messenger, server, logic


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


class Game:
    def __init__(self):
        self.postman = messenger.Postman()
        self.clients = client.Manager()

        self.logic = logic.Logic(self.postman)
        self.input_server = server.Input_Server('localhost', 45456, self.clients, self.postman)
        self.output_server = server.Output_Server('localhost', 45466, self.clients, self.postman)

    def start(self):
        self.postman.start()
        self.logic.start()
        self.input_server.start()
        self.output_server.start()

        
game = Game()
game.start()
