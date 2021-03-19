#programm reads current fpga status
from rt_hat import TAS as RT_HAT_TAS
RT_HAT_TAS.DEBUG_ENABLE=True
RT_HAT_TAS.init("/usr/share/InnoRoute/hat_env.sh")
my_GCL=[
	[0xff,5000000],
	[0x00,5000000]
	] #GCL with 5ms open and 5ms close
RT_HAT_TAS.set_GCL(my_GCL,0) #set GCL of port0
print(RT_HAT_TAS.get_GCL(0)) #print GCL
RT_HAT_TAS.apply(0)#apply tas settings to port 0

