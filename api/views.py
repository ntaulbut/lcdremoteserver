from django.http import HttpResponse
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD


pcf8574_address = 0x27  # I2C address of the PCF8574 chip.
pcf8574_a_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(pcf8574_address)
except:
    try:
        mcp = PCF8574_GPIO(pcf8574_a_address)
    except:
        print('I2C Address Error !')
        exit(1)
# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)
mcp.output(3, 1)  # turn on LCD backlight
lcd.begin(16, 2)  # set number of LCD lines and columns


def index(request):
    lcd.setCursor(0, 0)  # set cursor position
    lcd.message("Hello Django!\n")
    lcd.message("abcdefghijklmnop")
    return HttpResponse("Hi")


def clear(request):
    lcd.clear()
    return HttpResponse("Cleared")

