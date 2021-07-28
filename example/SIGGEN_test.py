from rt_hat import SIGGEN as RT_HAT_SIGGEN
import time
#RT_HAT_SIGGEN.DEBUG_ENABLE=True
RT_HAT_SIGGEN.init("/usr/share/InnoRoute/hat_env.sh")
current_time=RT_HAT_SIGGEN.RT_HAT_TAS.RT_HAT_FPGA.now()
print("current time:"+str(current_time))
DUTY_CYCLE=0.5
PERIOD=960000
START=current_time+1000000000 #start in 10s
CNT=10
print("triggering...")
RT_HAT_SIGGEN.set(DUTY_CYCLE,PERIOD,START,CNT)
while True:
	time.sleep(3)
	print("trigger again...")
	RT_HAT_SIGGEN.trigger(RT_HAT_SIGGEN.RT_HAT_TAS.RT_HAT_FPGA.now()+200000000)
