import Adafruit_CharLCD as LCD
from time import sleep

DEFAULT_RS_PIN        = 27
DEFAULT_EN_PIN        = 22
DEFAULT_D4_PIN        = 25
DEFAULT_D5_PIN        = 24
DEFAULT_D6_PIN        = 23
DEFAULT_D7_PIN        = 18
DEFAULT_BACKLIGHT_PIN = None

# Alternatively specify a 20x4 LCD.
DEFAULT_NUM_COLUMNS = 20
DEFAULT_NUM_ROWS    = 4

class ProgressLCD:
    "Simple wrapper around adafruits char LCD that shows progress bar"
    def __init__(self,
                 num_cols = DEFAULT_NUM_COLUMNS,
                 num_rows = DEFAULT_NUM_ROWS,
                 rs_pin = DEFAULT_RS_PIN,
                 en_pin = DEFAULT_EN_PIN,
                 d4_pin = DEFAULT_D4_PIN,
                 d5_pin = DEFAULT_D5_PIN,
                 d6_pin = DEFAULT_D6_PIN,
                 d7_pin = DEFAULT_D7_PIN,
                 backlight_pin = DEFAULT_BACKLIGHT_PIN):
        self._lcd = LCD.Adafruit_CharLCD(rs_pin, en_pin, d4_pin, d5_pin, d6_pin, d7_pin, num_cols, num_rows, backlight_pin)
        self._lines = ['' for i in range(num_rows)]
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._num_chars = num_rows*num_cols

    def display_message(self, message):
        self._add_text(message)
        self._lcd.clear()
        self._lcd.message('\n'.join(self._lines))

    def display_progress(self, progress):
        self._gen_progress(progress)
        self._lcd.clear()
        self._lcd.message('\n'.join(self._lines))

    def display_status(self, status):
        self._gen_status(status)
        self._lcd.clear()
        self._lcd.message('\n'.join(self._lines))

    def _add_text(self, message):
        lines = message.split('\n')
        message_padded = ''.join(line + ' ' * ((self._num_cols - len(line)) % self._num_cols)
                                for line in lines)
        for i in range(self._num_rows-1):
            line = ''
            if message_padded:
                line = message_padded[:self._num_cols]
                message_padded = message_padded[self._num_cols:]
            self._lines[i] = line

    def _gen_status(self, status):
        self._lines[self._num_rows-1] = status[:DEFAULT_NUM_COLUMNS]

    def _gen_progress(self, progress):
        self._lines[self._num_rows-1] = '#' * (int(progress*self._num_cols))


if __name__ == '__main__':
    #do a short test/demo
    lcd = ScrollingLCD()
    for x in range(10):
        lcd.display("This is line {}".format(x))
        sleep(0.5)
