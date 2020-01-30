from time import sleep
from rpi_TM1638 import TMBoards

"""
Test case of LED, segments, and switches. 
Press S2/S1 to increase/decrease the number on the left; 
S6/S5 for the number on the right; 
S3/S7 resets the numbers; 
S4/S8 quits the cycle.
Whenever a switch is on, the corresponding LED is on as well.
"""

STB = 14
CLK = 15
DIO = 18

TM = TMBoards(DIO, CLK, STB, 0)
TM.clearDisplay()

num_left = 0
num_right = 9999

def num_update():
    TM.segments[0] = '{:04d}'.format(abs(num_left)%10000)
    TM.segments[4] = '{:04d}'.format(abs(num_right)%10000)
    return

while True:
    for i in range(8):
        TM.leds[i] = True if TM.switches[i] else False
        sleep(0.01)
    if TM.switches[0]: num_left -= 1
    if TM.switches[1]: num_left += 1
    if TM.switches[2]: num_left = 0
    if TM.switches[4]: num_right -= 1
    if TM.switches[5]: num_right += 1
    if TM.switches[6]: num_right = 9999
    if TM.switches[3] or TM.switches[7]:
        TM.clearDisplay()
        break
    num_update()
    sleep(0.01)
