########################################################################
# Filename    : PCF8574.py
# Description : PCF8574 as Raspberry GPIO
# Author      : freenove
# modification: 2018/08/03
########################################################################
import smbus


class PCF8574I2C:
    OUTPUT = 0
    INPUT = 1

    def __init__(self, address):
        # Change bus number to 0 on rev1 RPI
        self.bus = smbus.SMBus(1)
        self.address = address
        self.currentValue = 0
        self.write_byte(0)  # test I2C

    def read_byte(self):
        """ Read PCF8574 all parts of the data """
        return self.currentValue

    def write_byte(self, value):
        """ Write data to PCF8574 port """
        self.currentValue = value
        self.bus.write_byte(self.address, value)

    def digital_read(self, pin):  #
        """ Read PCF8574 one part of the data """
        value = self.read_byte()
        return (value & (1 << pin) == (1 << pin)) and 1 or 0

    def digital_write(self, pin, new_value):
        """ Write data to PCF8574 one port """
        value = self.currentValue
        if new_value == 1:
            value |= (1 << pin)
        elif new_value == 0:
            value &= ~(1 << pin)
        self.write_byte(value)


class PCF8574GPIO:
    OUT = 0
    IN = 1
    BCM = 0
    BOARD = 0

    def __init__(self, address):
        self.chip = PCF8574I2C(address)
        self.address = address

    def setmode(self, mode):
        pass

    def setup(self, pin, mode):
        pass

    def input(self, pin):
        """ Read PCF8574 one port of the data """
        return self.chip.digital_read(pin)

    def output(self, pin, value):
        """ Write data to PCF8574 one port """
        self.chip.digital_write(pin, value)
