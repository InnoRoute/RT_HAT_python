# python functions for basic phy accesses
import os
import time
import pyrpio
from rt_hat import FPGA as RT_HAT_FPGA

DEBUG_ENABLE=False
RT_HAT_FPGA.init("/usr/share/InnoRoute/hat_env.sh")

