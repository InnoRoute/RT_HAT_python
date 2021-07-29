#programm reads current fpga status
from rt_hat import TAS as RT_HAT_TAS
import time
RT_HAT_TAS.DEBUG_ENABLE=True
RT_HAT_TAS.DEBUG_OUTPUT=True
RT_HAT_TAS.AUTOCORRECT_GCL=False

RT_HAT_TAS.init("/usr/share/InnoRoute/hat_env.sh")
port=2
my_GCL=[
    [0xff,4800000], #all gates open for 50us
    [0x00,4800000] #all gates closed for 50us
    ]
my_GCL2=[
    [0x00,48000000], #all gates open for 50us
    [0x00,48000000] #all gates closed for 50us
    ]
#current_time=RT_HAT_TAS.RT_HAT_FPGA.now()
#print("current time:"+str(current_time))
RT_HAT_TAS.set_GCL(my_GCL,port) #set GCL of port
#print(RT_HAT_TAS.get_GCL(port)) #print GCL
RT_HAT_TAS.TRIGGER_CNT=10
RT_HAT_TAS.ADMIN_BASE_TIME=RT_HAT_TAS.RT_HAT_FPGA.now()+4000000000
RT_HAT_TAS.ADMIN_CYCLE_TIME=0#0:automatic calculated from sum of GCL
RT_HAT_TAS.ADMIN_CYCLE_TIME_EXT=0
#RT_HAT_TAS.set_trigger_en(1)
RT_HAT_TAS.apply(port)#apply tas settings to port

#time.sleep(10)
#RT_HAT_TAS.set_GCL(my_GCL2,port) #set GCL of port
##print(RT_HAT_TAS.get_GCL(port)) #print GCL
#RT_HAT_TAS.TRIGGER_CNT=0
#RT_HAT_TAS.set_trigger_en(1)
#RT_HAT_TAS.apply(port)#apply tas settings to port
