from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from django_ratelimit.decorators import ratelimit

from .forms import MessageForm

HTTP_NO_CONTENT = 204

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

global_key = lambda _, __: "global"


@csrf_exempt
@ratelimit(group="lcd", rate="1/s", method=ratelimit.ALL, block=True, key=global_key)
def message(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        row_one = form.cleaned_data["row_one"]
        row_two = form.cleaned_data["row_two"]
        lcd.clear()
        lcd.message(row_one + "\n" + row_two)
        return HttpResponse(status=HTTP_NO_CONTENT)
    elif request.method == "DELETE":
        lcd.clear()
        return HttpResponse(status=HTTP_NO_CONTENT)
    else:
        return HttpResponseNotAllowed(["POST", "DELETE"])

