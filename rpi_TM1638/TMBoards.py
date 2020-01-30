# coding=utf-8

"""
Contains the class TMBoards
It's a higher-level class to manipulate a TM1638 board
"""

from .Font import FONT  # import the 7-segment Font
from .TM1638s import TM1638s


class TMBoards(TM1638s):
	"""
	Consider all the chained TM1638 boards (8 leds, 8 7-segment displays and 8 switchs) in one object
	
	For the switches, the idea is to first call the method updateSwitches
	(that read in one command the state of all the switches)
	and then used those values with TM.switches[i]
	(in the TM, you read the state of the switches all together, so once you read the value for the i-th switch,
	you have the value for all the other switches)
	"""

	def __init__(self, dio, clk, stb, brightness=1):
		# initialize chainedTM
		super(TMBoards, self).__init__(dio, clk, stb, brightness)

		# nb of boards
		self._nbBoards = len(self._stb)

		# add leds, 7-segments and switches
		self._leds = Leds(self)
		self._segments = Segments(self)
		self._switches = Switches(self)


	@property
	def nbBoards(self):
		"""Returns the number of TM1638 boards chained"""
		return self._nbBoards

	@property
	def leds(self):
		"""getter for the leds"""
		return self._leds

	@property
	def segments(self):
		"""getter for the leds"""
		return self._segments

	@property
	def switches(self):
		"""getter for the switch"""
		return self._switches


class Leds(object):
	"""Class to manipulate the leds mounted on the chained TM Boards"""

	def __init__(self, TM):
		"""Initialize the Led object
		"""
		self._TM = TM

	def __setitem__(self, index, value):
		"""
		called by TM.Leds[i] = value
		:param index: index of the led or tuple of indexes
		:param value: (boolean) value to give for this led (it could be a int, evaluated as boolean)
		"""
		# the leds are on the bit 0 of the odd addresses (led[0] on address 1, led[1] on address 3)
		# leds from 8 to 15 are on chained TM #2, etc.
		self._TM.sendData((index % 8) * 2 + 1, 1 if value else 0, index // 8)



class Segments(object):
	"""Class to manipulate the 7-segment displays on the chained TM Boards"""

	def __init__(self, TM):
		"""Initialize the Segment object"""
		self._TM = TM
		self._intern = [0, ] * (8 * self._TM.nbBoards)  # 8 7-segments per board

		# TODO: add the __getitem__ method (just returns the self._intern)

	def __setitem__(self, index, value):
		"""
		called by 
			TM.segments[i] = string
				-> set the i-th 7-segment display (and all the following, according to the length of value1)
				all the 7-segment displays after the #i are filled by the characters in value1
				this could be one-character string (so 7-segment #i is set to that character)
				or a longer string, and the following 7-segment displays are modified accordingly
				Example:
				TM.segments[0] = '8'    -> the display #0 is set to '8'
				or 
				TM.segments[0] = '456'  -> the display #0 is set to '4', the display #1 to '5' and #2 to '6'

			or

			TM.segments[i,j] = boolean
				-> set the j-th segment of the i-th 7-segment
				Example:
				TM.segments[2,3] = True -> set the 3rd segment of the 2nd 7-segment display

		i: index of the 7-segment display (0 for the 1st 7-segments (left of the 1st TM Board),
			8 for the 1st of the 2nd board, etc.)
		j: number of the segment (between 0 and 8)


		:param index: index of the 7-segment, or tuple (i,j) 
		:param value: string (or one-character string) when index is a int, otherwise a boolean
		"""
		if isinstance(index, int):
			# parse string to transform it in list of 8-bit int to send to the TM1638
			# -> allows to parse the '.' characters
			lv = []
			for c in value:
				if c not in FONT:
					raise ValueError("Cannot display the character '%s'", c)
				elif c == '.' and lv:    # c is a point and the previous char doesn't a point
					lv.append(lv.pop() | 128)  # add 128 to the previous char (ie add the point)
				else:
					lv.append(FONT[c])
			# send every display if something has changed
			for val in lv:
				# check if something change (otherwise do not send data, it's useless)
				if self._intern[index] != val:
					# store the new intern value
					self._intern[index] = val
					# send the data to the TM
					self._TM.sendData((index % 8) * 2, val, index // 8)
				index += 1

		elif isinstance(index, (list, tuple)):
			# get the 7-segment display index and the led index
			i, j = index
			# determine the new intern value
			if value:
				self._intern[i] |= 1 << j
			else:
				self._intern[i] &= ~(1 << j)
			# send the data to the TM
			self._TM.sendData((i % 8) * 2, self._intern[i], i // 8)


class Switches(object):
	"""Class to manipulate the switches on the chained TM Boards"""

	def __init__(self, TM):
		"""Initialize the Segment object"""
		self._TM = TM
		# self._intern = [[0 for _ in range(8) * self._TM.nbBoards] for _ in range(4)]  # 4*8 switches per board

	def __getitem__(self, item):
		"""Getter for the switch
		the item should be:
		- a tuple (K,n)
			where K is the line number (between 0 and 3, for K0, K1, K2 and K3)
			and n is the switch number (0 to 7 for the 1st board, 8 to 15 for the 2nd, etc.)
		- or an int n (K is supposed to be equal to 0)
		"""
		# get K and n
		if isinstance(item, list):
			K, n = item
		else:
			n = item
			K = 0
			sw = self._TM.getData(0) # Case for just one board
			if n < 4:
				return bool(sw[n%4]==1)
			else:
				return bool(sw[n%4]==16)
		# get the data
		sw = self._TM._getData(n//8)        # get the complete byte
		return bool(sw[K] & (1 << n))


