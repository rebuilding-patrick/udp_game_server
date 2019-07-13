extends Node

signal message_recv(message)

onready var player_input = get_node('../Input')

class Message:
	var raw_data
	var string
	var data 
	var index
	var command
	var value
	
	func _init(bytes):
		raw_data = bytes
		string = bytes.get_string_from_ascii()
		data  = string.split('][')
		index = int(data[0])
		command = int(data[1])
		value = str(data[2])
		
	func get_text():
		var text = '%s][%s][%s' % [index, command, value]
		return text


		
var socket = PacketPeerUDP.new()
var in_thread
var out_thread

var last_message_index = 0

var last_tick = 0
var timer = 0
var tick_rate = 1 / 10.0

var input_channel = []
var output_channel = []

func _ready():
	in_thread = Thread.new()
	out_thread = Thread.new()

var ident_data
func start_connection(username, password, ip, port):
	socket.set_dest_address(ip, port)
	ident_data = '%s:|:%s' % [username, password]
	send_data(0, 0, ident_data)
	recv()
	
	in_thread.start(self, 'handle_input')
	
	
func handle_input(userdata):
	var message
	while true:
		message = recv()
		last_message_index = message.index
		emit_signal("message_recv", message)
		
var messages
func _process(delta):
	timer += delta
	if timer > last_tick + tick_rate:
		last_tick = timer
		
		send_data(last_message_index, 1, player_input.get_input())

func send(message):
	var text = message.get_text()
	socket.put_packet(text.to_ascii())
	print('Server: Sent msg %s' % text)
	
	
func send_data(awk, command, text):
	text = '%s][%s][%s' % [awk, command, text]
	var packet = text.to_ascii()
	socket.put_packet(packet)
	print('Server: Sent data %s' % text)
	
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
	print('Server: Recv %s - %s' % [message.index, message.value])
	return message
