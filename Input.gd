extends Node

var input
var direction
var button

func get_input():
	direction = 0
	if Input.is_action_pressed('ui_up'):
		direction += 1
	if Input.is_action_pressed('ui_down'):
		direction += 2
	if Input.is_action_pressed('ui_left'):
		direction += 4
	if Input.is_action_pressed('ui_right'):
		direction += 8
	if Input.is_action_pressed('ui_shift'):
		direction += 16
	if Input.is_action_pressed('ui_control'):
		direction += 32
		
	button = 0
	if Input.is_action_pressed('ui_accept'):
		button += 1
	if Input.is_action_pressed('ui_select'):
		button += 2
	if Input.is_action_pressed('ui_r'):
		button += 4
	if Input.is_action_pressed('ui_f'):
		button += 8
	if Input.is_action_pressed('ui_q'):
		button += 16
	if Input.is_action_pressed('ui_e'):
		button += 32
	if Input.is_action_pressed('ui_z'):
		button += 64
	if Input.is_action_pressed('ui_tab'):
		button += 128
	if Input.is_action_pressed('ui_cancel'):
		button += 256
	
	input = '%s:%s' % [direction, button]
	return input
	
	
	