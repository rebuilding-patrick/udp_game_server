extends Node

onready var result = get_node('Panel/results')
onready var prompt = get_node("Panel/input")

var socket = PacketPeerUDP.new()
var ip = '127.0.0.1'
var con_port = 45456
var port = 45456

func _ready():
	socket.set_dest_address(ip, port)
	send('join')
	
	result.text = recv()
	
func send(text):
	text = '0][0][%s' % text
	var packet = text.to_ascii()
	socket.put_packet(packet)
	print('Sent %s' % text)
	
func recv():
	var bytes = socket.get_packet()
	return bytes.get_string_from_ascii()

func _on_Button_pressed():
	var text = prompt.text
	send(text)
	result.text = recv()