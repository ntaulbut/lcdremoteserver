from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from PCF8574 import PCF8574GPIO
from LCD1602 import LCD
from django_ratelimit.decorators import ratelimit

from .forms import MessageForm

HTTP_NO_CONTENT = 204

pcf8574_address = 0x27
pcf8574_a_address = 0x3F
try:
    mcp = PCF8574GPIO(pcf8574_address)
except OSError:
    try:
        mcp = PCF8574GPIO(pcf8574_a_address)
    except OSError:
        print("I2C Address Error")
        exit(1)
lcd = LCD(2, pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)
mcp.output(3, 1)  # Turn on LCD backlight


def global_key(_, __):
    return "global"


@csrf_exempt
@ratelimit(group="lcd", rate="1/s", method=ratelimit.ALL, key=global_key)
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
    elif request.method == "GET":
        return HttpResponse(lcd.text, content_type="text/plain")
    elif request.method == "DELETE":
        lcd.clear()
        return HttpResponse(status=HTTP_NO_CONTENT)
    else:
        return HttpResponseNotAllowed(["POST", "DELETE"])

