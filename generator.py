# Basic types generator
# Based on https://github.com/OpenRCE/sulley/blob/d5e60c875118637353769a113d2c53521309c657/sulley/primitives.py
import random

# Definitions
RANGE_MIN_VALUE     = 0
RANGE_MAX_VALUE     = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

class IntGenerator(object):
    def __init__(self, max_num):
        self.choices = [0xff]
        self.max_num = (1 << max_num) - 1
        if self.max_num > 0x80000000:
            self.choices.append(0x7FFFFFFF)
            self.choices.append(0x80000000)
        self.add_integer_boundaries(0)
        self.add_integer_boundaries(self.max_num / 2)
        self.add_integer_boundaries(self.max_num / 3)
        self.add_integer_boundaries(self.max_num / 4)
        self.add_integer_boundaries(self.max_num / 8)
        self.add_integer_boundaries(self.max_num / 16)
        self.add_integer_boundaries(self.max_num / 32)
        self.add_integer_boundaries(self.max_num)
        # Add some randoms
        for _ in xrange(50):
            self.choices.append(random.randint(0, self.max_num))
    def add_integer_boundaries (self, integer):
        for i in xrange(-10, 10):
            case = integer + i
            if 0 <= case < self.max_num:
                if case not in self.choices:
                    self.choices.append(case)
                    
class StringGenerator(object):
    def __init__(self):
        self.choices = [
            "",
            ".",
            "C:\\Windows\\aaa",
            "C:\\Windows\\System32\\cmd.exe",
            "C:\\Windows\\System32\\cmdU.exe",
            "C:\\Windows\\System32",
            "C:\\Windows\\System32\\",
            "http://google.fr/",
            "https://google.fr/",
            "http://42424242.fr/",
            "ssh://42424242.fr/",
            # strings ripped from spike (and some others I added)
            "/.:/"  + "A"*400 + "\x00\x00",
            "/.../" + "A"*400 + "\x00\x00",
            "/.../.../.../.../.../.../.../.../.../.../",
            "/../../../../../../../../../../../../etc/passwd",
            "/../../../../../../../../../../../../boot.ini",
            "..:..:..:..:..:..:..:..:..:..:..:..:..:",
            "\\\\*",
            "\\\\?\\",
            "/\\" * 400,
            "/." * 400,
            "!@#$%%^#$%#$@#$%$$@#$%^^**(()",
            "%01%02%03%04%0a%0d%0aADSF",
            "%01%02%03@%04%0a%0d%0aADSF",
            "/%00/",
            "%00/",
            "%00",
            "%u0000",
            "%\xfe\xf0%\x00\xff",
            "%\xfe\xf0%\x01\xff" * 20,
            
            # format strings.
            "%n"     * 100,
            "%n"     * 50,
            "\"%n\"" * 50,
            "%s"     * 100,
            "%s"     * 50,
            "\"%s\"" * 50,
            
            # command injection.
            "|touch /tmp/SULLEY",
            ";touch /tmp/SULLEY;",
            "|notepad",
            ";notepad;",
            "\nnotepad\n",
            "||cmd.exe&&id||",
            
            # SQL injection.
            "1;SELECT%20*",
            "'sqlattempt1",
            "(sqlattempt2)",
            "OR%201=1",
            
            # some binary strings.
            "\xde\xad\xbe\xef",
            "\xde\xad\xbe\xef" * 10,
            "\xde\xad\xbe\xef" * 100,
            "\xde\xad\xbe\xef" * 200,
            "\xde\xad\xbe\xef" * 200,
            "\x00"             * 200,
            
            # miscellaneous.
            "\r\n" * 100,
            "<>" * 400,         # sendmail crackaddr
        ]
        self.add_long_strings("A")
        self.add_long_strings("B")
        self.add_long_strings("1")
        self.add_long_strings("2")
        self.add_long_strings("3")
        self.add_long_strings("<")
        self.add_long_strings(">")
        self.add_long_strings("'")
        self.add_long_strings("\"")
        self.add_long_strings("/")
        self.add_long_strings("\\")
        self.add_long_strings("?")
        self.add_long_strings("=")
        self.add_long_strings("a=")
        self.add_long_strings("&")
        self.add_long_strings(".")
        self.add_long_strings(",")
        self.add_long_strings("(")
        self.add_long_strings(")")
        self.add_long_strings("]")
        self.add_long_strings("[")
        self.add_long_strings("%")
        self.add_long_strings("*")
        self.add_long_strings("-")
        self.add_long_strings("+")
        self.add_long_strings("{")
        self.add_long_strings("}")
        self.add_long_strings("\x14")
        self.add_long_strings("\xFE")   # expands to 4 characters under utf16
        self.add_long_strings("\xFF")   # expands to 4 characters under utf16
        
        # Strings with null bytes
        for length in [1, 4, 8, 16, 32, 128, 256, 512]:
            s = "B" * length
            s = s[:len(s)/2] + "\x00" + s[len(s)/2:]
            self.choices.append(s)
        
        # Add null bytes !
        choices_cp = self.choices[:]
        self.choices = []
        for i in choices_cp:
            self.choices.append(i + '\0')
        
    
    def add_long_strings(self, sequence):
        for length in [1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 255, 256, 257, 511, 512, 513, 1023, 1024]:
            long_string = sequence * length
            self.choices.append(long_string)

string_generator    = StringGenerator()
byte_generator      = IntGenerator(8)
short_generator     = IntGenerator(16)
long_generator      = IntGenerator(32)
hyper_generator     = IntGenerator(64)

def sub_generate_int(bitsize):
    """Generate a number according to bitsize"""
    choices = []
    if bitsize == 8:
        choices = byte_generator.choices
    elif bitsize == 16:
        choices = short_generator.choices
    elif bitsize == 32:
        choices = long_generator.choices
    elif bitsize == 64:
        choices = hyper_generator.choices
    else:
        raise NotImplementedError("Bad int bitsize")
    return random.choice(choices)

def generate_int(bitsize, range_min, range_max):
    """Generate a number in the provided range"""
    value = -1
    while value < range_min or value > range_max:
        value = sub_generate_int(bitsize)
        # If Range limits are too fine, FORCE the value
        if range_min != RANGE_MIN_VALUE or range_max != RANGE_MAX_VALUE:
            # After some tries
            if random.randint(0, 5) == 4:
                value = random.randint(range_min, range_max)
    return value

def generate_str(wide, range_min, range_max):
    """Generate a string (size is in the provided range)"""
    # Handle null terminaison (required for [string])
    s = random.choice(string_generator.choices)
    while len(s) < range_min or len(s) > range_max:
        s = random.choice(string_generator.choices)
        # If Range limits are too fine, FORCE the value
        if range_min != RANGE_MIN_VALUE or range_max != RANGE_MAX_VALUE:
            # After some tries
            if random.randint(0, 5) == 4:
                s = s * ((range_max / len(s)) + 1) # > range_max
                s = s[:random.randint(range_min, range_max)] # range_min > chosen > range_max
    # Dirty ...
    if wide:
        s = ''.join(map(lambda x: x + '\0', list(s)))
    return s
