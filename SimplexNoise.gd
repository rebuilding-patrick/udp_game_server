extends Node

var STRETCH_CONSTANT_2D = -0.211324865405187    # (1/Math.sqrt(2+1)-1)/2
var SQUISH_CONSTANT_2D = 0.366025403784439      # (Math.sqrt(2+1)-1)/2
var NORM_CONSTANT_2D = 47
var DEFAULT_SEED = 0

var GRADIENTS_2D = [5, 2, 2, 5, -5, 2, -2, 5, 5, -2, 2, -5, -5, -2, -2, -5]	

var noise_seed
var perm
var _perm
var perm_grad_index_3D
var _perm_grad_index_3D
var source

var i1
var i2
var index
var r
var g
var g1
var g2

var stretch_offset
var squish_offset
var xs
var ys
var xsb
var ysb
var xb
var yb
var xins
var yins
var in_sum
var dx0
var dy0
var value
var dx1
var dy1
var attn1
var extrapolate
var dx2
var dy2
var attn2
var attn0
var attn_ext
var dx_ext
var dy_ext
var zins
var xsv_ext
var ysv_ext

var c_max = 4294967296

func overflow(x):
	return x


func _init(noise_seed=DEFAULT_SEED):
	perm = []
	for i in range(0, 256):
		perm.append(0)
	_perm = perm
	
	source = []
	for i in range(0, 256):
		source.append(i)
		
	noise_seed = overflow(noise_seed * 6364136223846793005 + 1442695040888963407)
	noise_seed = overflow(noise_seed * 6364136223846793005 + 1442695040888963407)
	noise_seed = overflow(noise_seed * 6364136223846793005 + 1442695040888963407)
	for i in range(255, -1, -1):
		noise_seed = overflow(noise_seed * 6364136223846793005 + 1442695040888963407)
		r = int((noise_seed + 31) % (i + 1))
		if r < 0:
			r += i + 1
		perm[i] = source[r]
		source[r] = source[i]
		
func extrapolate(xsb, ysb, dx, dy):
	perm = self._perm
	i1 = fmod(xsb, 256.0)
	i2 = fmod((i1 + ysb), 256.0)
	
	index = fmod(perm[i2], 16) - fmod(perm[i2], 2)
	
	g1 = GRADIENTS_2D[index]
	g2 = GRADIENTS_2D[index + 1]
	return g1 * dx + g2 * dy
	
func set_seed(value):
	_init(value)

func noise2d(x, y):
	stretch_offset = (x + y) * STRETCH_CONSTANT_2D
	xs = x + stretch_offset
	ys = y + stretch_offset
	
	xsb = floor(xs)
	ysb = floor(ys)
	
	squish_offset = (xsb + ysb) * SQUISH_CONSTANT_2D
	xb = xsb + squish_offset
	yb = ysb + squish_offset
	
	xins = xs - xsb
	yins = ys - ysb

	in_sum = xins + yins
	
	dx0 = x - xb
	dy0 = y - yb
	
	value = 0
	
	dx1 = dx0 - 1 - SQUISH_CONSTANT_2D
	dy1 = dy0 - 0 - SQUISH_CONSTANT_2D
	attn1 = 2 - dx1 * dx1 - dy1 * dy1
	if attn1 > 0:
		attn1 *= attn1
		value += attn1 * attn1 * extrapolate(xsb + 1, ysb + 0, dx1, dy1)
		
	dx2 = dx0 - 0 - SQUISH_CONSTANT_2D
	dy2 = dy0 - 1 - SQUISH_CONSTANT_2D
	attn2 = 2 - dx2 * dx2 - dy2 * dy2
	if attn2 > 0:
		attn2 *= attn2
		value += attn2 * attn2 * extrapolate(xsb + 0, ysb + 1, dx2, dy2)
		
	if in_sum <= 1:
		zins = 1 - in_sum
		if zins > xins or zins > yins:
			if xins > yins:
				xsv_ext = xsb + 1
				ysv_ext = ysb - 1
				dx_ext = dx0 - 1
				dy_ext = dy0 + 1
			else:
				xsv_ext = xsb - 1
				ysv_ext = ysb + 1
				dx_ext = dx0 + 1
				dy_ext = dy0 - 1
		else:
			xsv_ext = xsb + 1
			ysv_ext = ysb + 1
			dx_ext = dx0 - 1 - 2 * SQUISH_CONSTANT_2D
			dy_ext = dy0 - 1 - 2 * SQUISH_CONSTANT_2D
	
	else:
		zins = 2 - in_sum
		if zins < xins or zins < yins:
			if xins > yins:
				xsv_ext = xsb + 2
				ysv_ext = ysb + 0
				dx_ext = dx0 - 2 - 2 * SQUISH_CONSTANT_2D
				dy_ext = dy0 + 0 - 2 * SQUISH_CONSTANT_2D
			else:
				xsv_ext = xsb + 0
				ysv_ext = ysb + 2
				dx_ext = dx0 + 0 - 2 * SQUISH_CONSTANT_2D
				dy_ext = dy0 - 2 - 2 * SQUISH_CONSTANT_2D
		else:
			dx_ext = dx0
			dy_ext = dy0
			xsv_ext = xsb
			ysv_ext = ysb
		xsb += 1
		ysb += 1
		dx0 = dx0 - 1 - 2 * SQUISH_CONSTANT_2D
		dy0 = dy0 - 1 - 2 * SQUISH_CONSTANT_2D
		
	attn0 = 2 - dx0 * dx0 - dy0 * dy0
	if attn0 > 0:
		attn0 *= attn0
		value += attn0 * attn0 * extrapolate(xsb, ysb, dx0, dy0)
		
	attn_ext = 2 - dx_ext * dx_ext - dy_ext * dy_ext
	if attn_ext > 0:
		attn_ext *= attn_ext
		value += attn_ext * attn_ext * extrapolate(xsv_ext, ysv_ext, dx_ext, dy_ext)
	
	return value / NORM_CONSTANT_2D

