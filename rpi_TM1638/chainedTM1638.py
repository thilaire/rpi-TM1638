# coding=utf-8

from RPi import GPIO

# suppresses warnings on RasPi
GPIO.setwarnings(False)

# some constant to command the TM1638
READ_MODE = 0x02
WRITE_MODE = 0x00
INCR_ADDR = 0x00
FIXED_ADDR = 0x04


class chainedTM1638(object):
	"""chainedTM1638 class"""

	def __init__(self, dio, clk, stb, brightness=1):
		"""
		Initialize the chainedTM1638 
		GPIO numbers refer to "Broadcom SOC Channel", so CLK=11 means CLK is GPIO11 (so pin 23)
		:param dio: Data I/O GPIO
		:param clk: clock GPIO
		:param stb: Chip Select GPIO    -> a tuple if several chainedTM1638 boards are chained
		:param brightness: brightness of the display (between 0 and 7)
		"""

		# store the GPIOs
		self.dio = dio
		self.clk = clk
		self.stb = tuple(stb)

		# configure the GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.dio, GPIO.OUT)
		GPIO.setup(self.clk, GPIO.OUT)
		for stb in self.stb:
			GPIO.setup(stb, GPIO.OUT)

		# Clk and Stb <- High for every TM
		self._setStb(True, None)
		GPIO.output(self.clk, True)

		# init the displays
		self.turnOn(brightness)
		self.clearDisplay()



	def clearDisplay(self, TMindex=None):
		"""Turn off every led
		if TMindex is given, every TM of TMindex is cleared
		otherwise, they are all cleared
		"""
		self._setDataMode(WRITE_MODE, INCR_ADDR, TMindex)   # set data read mode (automatic address increased)
		self._setStb(False, TMindex)
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


	# ==================
	# Internal commands
	# ==================
	def _setStb(self, value, TMindex):
		"""
		Set all the Stb pinouts (if TMindex is True)
		or only one Stb (given by TMindex) to Value
		:param value: value given to the Stb(s)
		:param TMindex: None if all the chainedTM1638 are impacted, or the index of that TM if it concerns only one
		"""
		if TMindex is None:
			for stb in self.stb:
				GPIO.output(stb, value)
		else:
			GPIO.output(self.stb[TMindex], value)


	def _setDataMode(self, wr_mode, addr_mode, TMindex):
		"""
		Set the data modes
		:param wr_mode: READ_MODE (read the key scan) or WRITE_MODE (write data)
		:param addr_mode: INCR_ADDR (automatic address increased) or FIXED_ADDR
		:param TMindex: number of the TM to turn on (None if it's for all the TM)
		"""
		self.sendCommand(0x40 | wr_mode | addr_mode, TMindex)

	def _sendByte(self, data):
		"""
		Send a byte (Stb must be Low)
		:param data: a byte to send 
		"""
		for i in range(8):
			GPIO.output(self.clk, False)
			GPIO.output(self.dio, (data & 1) == 1)
			data >>= 1
			GPIO.output(self.clk, True)


	def sendCommand(self, cmd, TMindex):
		"""
		Send a command
		:param cmd: cmd to send
		:param TMindex: number of the TM to turn on (None if it's for all the TM)
		"""
		self._setStb(False, TMindex)
		self._sendByte(cmd)
		self._setStb(True, TMindex)


	def sendData(self, addr, data, TMindex):
		"""
		Send a data at address addr
		:param addr: adress of the data
		:param data: value of the data
		:param TMindex: number of the TM to turn on (None if it's for all the TM)
		"""
		self._setDataMode(WRITE_MODE, FIXED_ADDR, TMindex)
		self._setStb(False, TMindex)
		self._sendByte(0xC0 | addr)
		self._sendByte(data)
		self._setStb(True, TMindex)




