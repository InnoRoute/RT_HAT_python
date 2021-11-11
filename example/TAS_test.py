#programm reads current fpga status
from rt_hat import TAS as RT_HAT_TAS
RT_HAT_TAS.DEBUG_ENABLE=True
RT_HAT_TAS.DEBUG_OUTPUT=True
RT_HAT_TAS.init("/usr/share/InnoRoute/hat_env.sh")
port=2
my_GCL=[
	[0x00,48000000], #all gates open for 48ms
	[0x01,48000000] #gate 0 closed for 48ms
	] 
RT_HAT_TAS.set_GCL(my_GCL,port) #set GCL of port
print(RT_HAT_TAS.get_GCL(port)) #print GCL
RT_HAT_TAS.apply(port)#apply tas settings to port 


