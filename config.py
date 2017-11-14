# Fuzzer random seed
import random
SEED = random.randint(0, 0xffffffff)
FUZZ_LOG_MAX_SIZE_MB = 50
random.seed(SEED)

LOGFILE = None
# Create fuzzer logs file before dropping the integrity to low
LOGFILE_NAME = "{}.logfile".format(SEED)
open(LOGFILE_NAME, 'w').close()
LOGFILE = open(LOGFILE_NAME, 'r+')

# Debugs options
DEBUG_STDOUT = True