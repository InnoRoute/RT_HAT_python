#programm reads current fpga status
from rt_hat import FPGA as RT_HAT_FPGA

RT_HAT_FPGA.init("/usr/share/InnoRoute/hat_env.sh")
print(RT_HAT_FPGA.status())
