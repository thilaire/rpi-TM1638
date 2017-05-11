# coding=utf-8

from RPi import GPIO
from time import sleep

# suppresses warnings on RasPi
GPIO.setwarnings(False)

# some constant to command the TM1638
READ_MODE = 0x02
WRITE_MODE = 0x00
INCR_ADDR = 0x00
FIXED_ADDR = 0x04

# TODO: allow multiple DIO, so that we can receive data from the TMs (the switches) in parallel


class TM1638s(object):
	"""TM1638s class"""

	def __init__(self, dio, clk, stb, brightness=1):
		"""
		Initialize a TM1638 (or some chained TM1638s) 
		GPIO numbers refer to "Broadcom SOC Channel", so CLK=11 means CLK is GPIO11 (so pin 23)
		:param dio: Data I/O GPIO
		:param clk: clock GPIO
		:param stb: Chip Select GPIO    -> a tuple if several TM1638s boards are chained
		:param brightness: brightness of the display (between 0 and 7)
		"""

		# store the GPIOs
		self._dio = dio
		self._clk = clk
		self._stb = tuple(stb)

		# configure the GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self._dio, GPIO.OUT)
		GPIO.setup(self._clk, GPIO.OUT)
		for stb in self._stb:
			GPIO.setup(stb, GPIO.OUT)

		# Clk and Stb <- High for every TM
		self._setStb(True, None)
		GPIO.output(self._clk, True)

		# init the displays
		self.turnOn(brightness)
		self.clearDisplay()



	def clearDisplay(self, TMindex=None):
		"""Turn off every led
		if TMindex is given, every TM of TMindex is cleared
		otherwise, they are all cleared
		"""
		self._setStb(False, TMindex)
		self._setDataMode(WRITE_MODE, INCR_ADDR)   # set data read mode (automatic address increased)
		self._sendByte(0xC0)   # address command set to the 1st address
		for i in range(16):
			self._sendByte(0x00)   # set to zero all the addresses
		self._setStb(True, TMindex)


	def turnOff(self, TMindex=None):
		"""Turn off (physically) the leds"""
		self.sendCommand(0x80, TMindex)


	def turnOn(self, brightness, TMindex=None):
		"""
		Turn on the display and set the brightness
		The pulse width used is set to:
		0 => 1/16       4 => 11/16
		1 => 2/16       5 => 12/16
		2 => 4/16       6 => 13/16
		3 => 10/16      7 => 14/16
		:param brightness: between 0 and 7
		:param TMindex: number of the TM to turn on (None if it's for all the TM)
		"""
		self.sendCommand(0x88 | (brightness & 7), TMindex)


	# ==========================
	# Communication with the TM
	# (mainly used by TMBoards)
	# ==========================
	def sendCommand(self, cmd, TMindex):
		"""
		Send a command
		:param cmd: cmd to send
		:param TMindex: number of the TM to send the command (None if it's for all the TM)
		"""
		self._setStb(False, TMindex)
		self._sendByte(cmd)
		self._setStb(True, TMindex)


	def sendData(self, addr, data, TMindex):
		"""
		Send a data at address addr
		:param addr: adress of the data
		:param data: value of the data
		:param TMindex: number of the TM to send some data (None if it's for all the TM)
		"""
		# set mode
		self._setStb(False, TMindex)
		self._setDataMode(WRITE_MODE, FIXED_ADDR)
		self._setStb(True, TMindex)
		# set address and send byte (stb must go high and low before sending address)
		self._setStb(False, TMindex)
		self._sendByte(0xC0 | addr)
		self._sendByte(data)
		self._setStb(True, TMindex)


	def getData(self, TMindex):
		"""
		Get the data (buttons) of the TM
		:param TMindex: number of the TM to receive some data (cannot be None)
		:return: the four octets read (as a list)
		"""
		# set in read mode
		self._setStb(False, TMindex)
		self._setDataMode(READ_MODE, INCR_ADDR)
		sleep(20e-6) # wait at least 10µs ?
		# read four bytes
		b = []
		for i in range(4):
			b.append(self._getByte())
		self._setStb(True, TMindex)
		return b


	# ==================
	# Internal functions
	# ==================
	def _setStb(self, value, TMindex):
		"""
		Set all the Stb pinouts (if TMindex is True)
		or only one Stb (given by TMindex) to Value
		:param value: value given to the Stb(s)
		:param TMindex: None if all the TM1638s are impacted, or the index of that TM if it concerns only one
		"""
		if TMindex is None:
			for stb in self._stb:
				GPIO.output(stb, value)
		else:
			GPIO.output(self._stb[TMindex], value)


	def _setDataMode(self, wr_mode, addr_mode):
		"""
		Set the data modes
		:param wr_mode: READ_MODE (read the key scan) or WRITE_MODE (write data)
		:param addr_mode: INCR_ADDR (automatic address increased) or FIXED_ADDR
		"""
		self._sendByte(0x40 | wr_mode | addr_mode)

	def _sendByte(self, data):
		"""
		Send a byte (Stb must be Low)
		:param data: a byte to send 
		"""
		for i in range(8):
			GPIO.output(self._clk, False)
			GPIO.output(self._dio, (data & 1) == 1)
			data >>= 1
			GPIO.output(self._clk, True)

	def _getByte(self):
		"""
		Receive a byte (from the TM previously configured)
		:return: the byte received
		"""
		# configure DIO in input with pull-up
		GPIO.setup(self._dio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		# read 8 bits
		temp = 0
		for i in range(8):
			temp >>= 1
			GPIO.output(self._clk, False)
			if GPIO.input(self._dio):
				temp |= 0x80
			GPIO.output(self._clk, True)
		# put back DIO in output mode
		GPIO.setup(self._dio, GPIO.OUT)
		return temp

