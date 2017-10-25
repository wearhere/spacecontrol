import Adafruit_CharLCD as LCD

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


class ScrollingLCD:
    "Simple wrapper around adafruits char LCD that auto-scrolls"
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
        self._lcd = LCD(rs_pin, en_pin, d4_pin, d5_pin, d6_pin, d7_pin, backlight_pin)
        self._buffer = ''
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._num_chars = num_rows*num_cols

    def display(self, message):
        self.add_text(message)
        self._lcd.message(self._buffer)

    def _add_text(self, message):
        lines = message.split('\n')
        self._buffer = (self._buffer + 
                        ''.join(line + ' ' * ((self._num_cols - len(line)) % self._num_cols)
                                for line in lines))
        self._buffer = self._buffer[:-self._num_chars]
            
                
        
# Print a two line message
lcd.message('Hello\nworld!')


