# rpi-TM1638

`rpi-TM1638` is (yet another) Raspberry Pi library (driver) for (chained) TM1638 boards like the 2$ cheap ones you can buy online.

![One of these TM1638 board](doc/TM1638.JPG)

It can be used with the LED&KEY (see photo), but also the QYF-TM1638 and JY-LKM1638 (they only differ from the number of switches on the board or the number of leds).

These boards have onboard eight 7-segment displays, 8 LEDs and 8 switches, both controlled by the TM1638 chip.
You can control several TM1638 boards, and uses several LEDs, 7-segment displays and switches with only three (Clock, Data and Enable) GPIOs of your Raspberry Pi.

This library proposes:
- a low level support for the TM1638 chip
- a higher level support for the LED&KEY TM1638-based board (that can be easily used for the two other boards) 

## Installation
Just use `pip` to install the library

    pip install rpi-TM1638
  
or clone the latest version on [Github](https://github.com/thilaire/rpi-TM1638) 
   
## Example
Suppose you have two TM1638 boards, that share DataIO on GPIO19 and the clock on GPIO13. They have their STB plugged on GPIO 6 and 26. 
The following program turns on the LEDs #0 (3rd left of the 1st board) and #9 (2nd left of the 2nd board). It displays `12345678` on the first 7-segment display, and `2.3` on the 2nd one.
It captures the #2 switch (3rd of the 1st board)
  
    DIO = 19
    CLK = 13
    STB = 06, 26

    TM = TMBoards(DIO, CLK, STB, 0)

    TM.leds[3] = True
    TM.leds[9] = True

    TM.segments[0] = '12345678'
    TM.segments[10] = '2.3'
    
    a = TM.switches[2]

## Details

The `rpi-TM1638` proposes a two-level API:
- The class `TM1638s` proposes low-level functions to manipulate the TM chips:
  - `turnOn(brightness)`,  `turnOff` and `clearDisplay` to turn on/off the displays, clear the displays or set the brightness
  - `sendCommand` and `sendData` to talk with the TM chip
  - plus some intern functions (to change the data mode, etc.)
- The class `TMboards` (that inherits from `TM1638s`) proposes somes methods to manipulate the LEDs, 7-segment displays and switches, with some getter/setter on the properties:
  - `leds`: for the leds
  - `segments`: for the 7-segment displays
  - `switches`: for the switches
  
  
To use the package, you just need to create a `TMboards` object or create a class that inherits from `TMboards` and proposes some high-level properties on top of it.
