extends Node

#onready var game = get_node('../../Game')
onready var player_input = get_node('../Input')

signal msg_recv(message)


class Message:
	var raw_data
	var string
	var data 
	var index
	var command
	var value
	var values
	
	func _init(bytes):
		raw_data = bytes
		if bytes.size() > 0:
			string = bytes.get_string_from_ascii()
			data  = string.split('][')
			index = int(data[0])
			command = int(data[1])
			value = str(data[2])
			values  = {}
		else:
			string = ''
			data = ''
			index = -10
			command = -10
			value = -10
			values = {}
		
	func get_text():
		var text = '%s][%s][%s' % [index, command, value]
		return text


var socket = PacketPeerUDP.new()
var in_thread
var out_thread

var last_message_index = 0

var tick = 0
var last_tick = 0
var timer = 0
var tick_rate = 1 / 15.0

var input_channel = []
var output_channel = []

var username
var password
var ident_data
var address
var port

var message
var value
var text


func _ready():
	in_thread = Thread.new()
	out_thread = Thread.new()

func query_server(ip, port):
	socket.set_dest_address(ip, port)
	send_data(-1, -1, 'world_get')
	message = recv()
	return message

func join_server(username, password, ip, port):
	socket.set_dest_address(ip, port)
	ident_data = '%s:|:%s' % [username, password]
	send_data(0, 0, ident_data)
	
	in_thread.start(self, 'handle_input')
	
func handle_input(userdata):
	while true:
		message = recv()
		last_message_index = message.index
		emit_signal('msg_recv', message)
		OS.delay_msec(0.001)

var messages
func _process(delta):
	timer += delta
	if timer > last_tick + tick_rate:
		last_tick = timer
		tick += 1
		#print('_process tick %s' % tick)
		send_data(last_message_index, 3, player_input.get_input())
	
	#handle_input('data') #testing for thread
		
func send(message):
	text = message.get_text()
	socket.put_packet(text.to_ascii())
	#print('Server: Sent msg %s' % text)
	
	
func send_data(awk, command, text):
	text = '%s][%s][%s' % [awk, command, text]
	var packet = text.to_ascii()
	socket.put_packet(packet)
	#print('Server: Sent data %s' % text)
	
func recv():
	var bytes
	var message
	var stng
	var flag = true
	while flag: 
		if socket.get_available_packet_count():
			bytes = socket.get_packet()
			stng = bytes.get_string_from_ascii()
			flag = false
			message = Message.new(bytes)
	#print('Server: Recv %s - %s' % [message.index, message.value])
	return message

func _exit_tree():
	in_thread.wait_to_finish()
	out_thread.wait_to_finish()