import I2C_LCD_driver as LCD

DEFAULT_NUM_COLUMNS = 20
DEFAULT_NUM_ROWS = 4

class I2CLCD:
    """
    Wrapper around char LCD:
    - Shows Progress Bar
    - Communicates over I2C
    """

    def __init__(self,
                 num_cols = DEFAULT_NUM_COLUMNS,
                 num_rows = DEFAULT_NUM_ROWS):
        self._lcd = LCD.lcd()
        self._lines = ['' for i in range(num_rows)]
        self._num_rows = num_rows
        self._num_cols = num_cols

    def _gen_text(self, message):
	if len(message) == 0:
            blank_line = " " * self._num_cols
	    self._lines[0] = blank_line
            self._lines[1] = blank_line
            self._lines[2] = blank_line
	    return 
        words = iter(message.split())
        lines, current = [], next(words)
        for word in words:
            if len(current) + 1 + len(word) > self._num_cols:
                lines.append(current)
                current = word
            else:
                current += " " + word
        lines.append(current)
        self._lines[0] = lines[0] + " " * (self._num_cols - len(lines[0])) 
        self._lines[1] = lines[1] + " " * (self._num_cols - len(lines[1])) if 1 < len(lines) else " " * (self._num_cols)
        self._lines[2] = lines[2] + " " * (self._num_cols - len(lines[2])) if 2 < len(lines) else " " * (self._num_cols)
        self._lines[3] = ""

    def _gen_progress(self, progress):
        # self._lines[3] = ('#' * (int(progress*self._num_cols))).ljust(self._num_cols)
        self._lines[3] = ('#' * (int(int(progress)*self._num_cols/100))).ljust(self._num_cols)
        print self._lines[3]

    def _gen_status(self, status):
        self._lines[3] = status[:self._num_cols].ljust(self._num_cols)

    def display_message(self, message):
        self._gen_text(message)
        for index, line in enumerate(self._lines): 
            self._lcd.lcd_display_string(line, index+1)

    def display_progress(self, progress):
        self._gen_progress(progress)
        self._lcd.lcd_display_string(self._lines[3], 4)

    def display_status(self, status):
        self._gen_status(status)
        self._lcd.lcd_display_string(self._lines[3], 4)


