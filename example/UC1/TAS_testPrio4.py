#programm reads current fpga status
from rt_hat import TAS as RT_HAT_TAS
RT_HAT_TAS.DEBUG_ENABLE=True
RT_HAT_TAS.DEBUG_OUTPUT=True
RT_HAT_TAS.init("/usr/share/InnoRoute/hat_env.sh")
port=0
my_GCL=[
        [0xEF, 40000000], #all gates open except TSN (gate 4) for 4ms > non-TSN traffic
        [0x00, 10000000], #all gates closed for 1ms > guard time
        [0x10, 10000000], #gate 4 open for 1ms >  TSN Traffic
        [0x00, 10000000], #guard time
        [0xEF, 40000000]  # non-TSN traffic for 4ms
        ]
RT_HAT_TAS.set_GCL(my_GCL,port) #set GCL of port
print(RT_HAT_TAS.get_GCL(port)) #print GCL
RT_HAT_TAS.apply(port)#apply tas settings to port
