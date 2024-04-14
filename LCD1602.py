from time import sleep


def delay_ms(microseconds):
    seconds = microseconds / float(1000000)
    sleep(seconds)


class LCD(object):
    # Commands
    LCD_CLEAR_DISPLAY = 0x01
    LCD_RETURN_HOME = 0x02
    LCD_SET_ENTRY_MODE = 0x04
    LCD_DISPLAY_CONTROL = 0x08
    LCD_CURSOR_SHIFT = 0x10
    LCD_FUNCTION_SET = 0x20
    LCD_SET_CGRAM_ADDR = 0x40
    LCD_SET_DDRAM_ADDR = 0x80

    # Display entry mode
    LCD_ENTRY_RIGHT = 0x00
    LCD_ENTRY_LEFT = 0x02
    LCD_ENTRY_SHIFT_INCREMENT = 0x01
    LCD_ENTRY_SHIFT_DECREMENT = 0x00

    # Display on/off control
    LCD_DISPLAY_ON = 0x04
    LCD_DISPLAY_OFF = 0x00
    LCD_CURSOR_ON = 0x02
    LCD_CURSOR_OFF = 0x00
    LCD_BLINK_ON = 0x01
    LCD_BLINK_OFF = 0x00

    # Display/cursor shift
    LCD_DISPLAY_MOVE = 0x08
    LCD_CURSOR_MOVE = 0x00
    LCD_MOVE_RIGHT = 0x04
    LCD_MOVE_LEFT = 0x00

    # Function set
    LCD_8BIT_MODE = 0x10
    LCD_4BIT_MODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, lines, pin_rs=25, pin_e=24, pins_db=None, GPIO=None):
        # Emulate the old behavior of using RPi.GPIO if we haven't been given
        # an explicit GPIO interface to use
        if pins_db is None:
            pins_db = [23, 17, 21, 22]
        if not GPIO:
            import RPi.GPIO as GPIO
            GPIO.setwarnings(False)
        self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        self.GPIO.setmode(GPIO.BCM)  # GPIO=None use Raspi PIN in BCM mode
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)

        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)

        self.write_nibble(0x33)  # Initialization
        self.write_nibble(0x32)  # Initialization
        self.write_nibble(0x28)  # 2 line 5x7 matrix
        self.write_nibble(0x0C)  # Turn cursor off 0x0E to enable cursor
        self.write_nibble(0x06)  # Shift cursor right

        self.displaycontrol = self.LCD_DISPLAY_ON | self.LCD_CURSOR_OFF | self.LCD_BLINK_OFF

        self.display_function = self.LCD_4BIT_MODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.display_function |= self.LCD_2LINE

        # Initialize to default text direction (for romance languages)
        self.display_mode = self.LCD_ENTRY_LEFT | self.LCD_ENTRY_SHIFT_DECREMENT
        self.write_nibble(
            self.LCD_SET_ENTRY_MODE | self.display_mode)  # set the entry mode

        self.num_lines = lines
        self.display_function |= self.LCD_2LINE

        self.clear()

    def home(self):
        self.write_nibble(self.LCD_RETURN_HOME)
        delay_ms(3000)

    def clear(self):
        self.write_nibble(self.LCD_CLEAR_DISPLAY)
        delay_ms(
            3000)

    def set_cursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.num_lines:
            row = self.num_lines - 1  # we count rows starting w/0
        self.write_nibble(self.LCD_SET_DDRAM_ADDR | (col + row_offsets[row]))

    def display_off(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAY_ON
        self.write_nibble(self.LCD_DISPLAY_CONTROL | self.displaycontrol)

    def display_on(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAY_ON
        self.write_nibble(self.LCD_DISPLAY_CONTROL | self.displaycontrol)

    def cursor_off(self):
        """ Turns the underline cursor off """
        self.displaycontrol &= ~self.LCD_CURSOR_ON
        self.write_nibble(self.LCD_DISPLAY_CONTROL | self.displaycontrol)

    def cursor_on(self):
        """ Turns the underline cursor on """
        self.displaycontrol |= self.LCD_CURSOR_ON
        self.write_nibble(self.LCD_DISPLAY_CONTROL | self.displaycontrol)

    def blink_off(self):
        """ Turn the blinking cursor off """
        self.displaycontrol &= ~self.LCD_BLINK_ON
        self.write_nibble(self.LCD_DISPLAY_CONTROL | self.displaycontrol)

    def blink_on(self):
        """ Turn the blinking cursor on """
        self.displaycontrol |= self.LCD_BLINK_ON
        self.write_nibble(self.LCD_DISPLAY_CONTROL | self.displaycontrol)

    def scroll_left(self):
        """ These commands scroll the display without changing the RAM """
        self.write_nibble(
            self.LCD_CURSOR_SHIFT | self.LCD_DISPLAY_MOVE | self.LCD_MOVE_LEFT)

    def scroll_right(self):
        """ These commands scroll the display without changing the RAM """
        self.write_nibble(
            self.LCD_CURSOR_SHIFT | self.LCD_DISPLAY_MOVE | self.LCD_MOVE_RIGHT)

    def dir_ltr(self):
        """ This is for text that flows Left to Right """
        self.display_mode |= self.LCD_ENTRY_LEFT
        self.write_nibble(self.LCD_SET_ENTRY_MODE | self.display_mode)

    def dir_rtl(self):
        """ This is for text that flows Right to Left """
        self.display_mode &= ~self.LCD_ENTRY_LEFT
        self.write_nibble(self.LCD_SET_ENTRY_MODE | self.display_mode)

    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        self.display_mode |= self.LCD_ENTRY_SHIFT_INCREMENT
        self.write_nibble(self.LCD_SET_ENTRY_MODE | self.display_mode)

    def autoscroll_off(self):
        """ This will 'left justify' text from the cursor """
        self.display_mode &= ~self.LCD_ENTRY_SHIFT_INCREMENT
        self.write_nibble(self.LCD_SET_ENTRY_MODE | self.display_mode)

    def write_nibble(self, bits, char_mode=False):
        """ Send command to LCD """
        delay_ms(1000)
        bits = bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)
        self.pulse_enable()
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4, 8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i - 4], True)
        self.pulse_enable()

    def pulse_enable(self):
        self.GPIO.output(self.pin_e, False)
        delay_ms(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, True)
        delay_ms(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.GPIO.output(self.pin_e, False)
        delay_ms(1)  # commands need > 37us to settle

    def message(self, text):
        """ Send string to LCD. Newline wraps to next line"""
        for char in text:
            if char == '\n':
                self.write_nibble(0xC0)  # next line
            else:
                self.write_nibble(ord(char), True)
