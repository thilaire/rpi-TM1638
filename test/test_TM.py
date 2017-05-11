# coding=utf-8
from time import sleep
from rpi_TM1638 import TMBoards

# my GPIO settings (two TM1638 boards connected on GPIO19 and GPIO13 for DataIO and Clock; and on GPIO06 and GPIO26 for the STB)
DIO = 19
CLK = 13
STB = 06, 26

# instanciante my TMboards
TM = TMBoards(DIO, CLK, STB, 0)

TM.clearDisplay()

# some LEDs manipulation
TM.leds[0] = True       # turn on led 0 (1st led of the 1st board)
TM.leds[12] = True      # turn on led 12 (5th led of the 2nd board, since there is 8 leds per board)

TM.segments[1] = '0'        # display '0' on the display 1 (2nd 7-segment display of the 1st board)
TM.segments[4] = '98.76'     # display '9876' on the 7-segment display number 4, 5, 6 and 7 (the point is on segment 5)
TM.segments[3,1] = True     # turn on the segment #1 of the 7-segment number 3

TM.leds = (True, False, True)   # set the three first leds


while True:
	a=TM.getData(0)
	b=TM.getData(1)
	TM.segments[0] = ''.join("%02d"%x for x in a)
	TM.segments[8] = ''.join("%02d" % x for x in b)
	sleep(0.01)