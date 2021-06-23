from rt_hat import SIGGEN as RT_HAT_SIGGEN
import time
import random
RT_HAT_SIGGEN.DEBUG_ENABLE=True
RT_HAT_SIGGEN.init("/usr/share/InnoRoute/hat_env.sh")
current_time=RT_HAT_SIGGEN.RT_HAT_TAS.RT_HAT_FPGA.now()
print("current time:"+str(current_time))
DUTY_CYCLE=0.5
PERIOD= random.randrange(1000, 10000, 100)
START=current_time+10000000000 #start in 10s
CNT=0
RT_HAT_SIGGEN.set(DUTY_CYCLE,PERIOD,START,CNT)
time.sleep(10)
