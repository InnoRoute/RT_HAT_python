from rt_hat import TAS as RT_HAT_TAS
import math
#RT_HAT_TAS.DEBUG_ENABLE=True
#RT_HAT_TAS.DEBUG_OUTPUT=True
DEBUG_ENABLE=False
DEBUG_OUTPUT=False

def init(envfile):
	global __granularity
	global DEBUG_ENABLE
	global DEBUG_OUTPUT
	RT_HAT_TAS.DEBUG_ENABLE=DEBUG_ENABLE
	RT_HAT_TAS.DEBUG_OUTPUT=DEBUG_OUTPUT
	RT_HAT_TAS.init(envfile)


def set(DUTY_CYCLE,PERIOD,PHASE,COUNT):
#PHASE=starttime
	granularity=RT_HAT_TAS.get_granularity()
	if (DUTY_CYCLE<=0 or DUTY_CYCLE>=1):
		raise Exception("ERROR: 0<DUTY_CYCLE<1 !")
	if (PERIOD<=0 or PERIOD>=2000000000):
		raise Exception("ERROR: 0<PERIOD<2s !")
#	if (PHASE<0 or PHASE>PERIOD):
#		raise Exception("ERROR: 0 <=PHASE<=PERIOD !")
	port=2 # select virtual trigger port
	my_GCL=[ # gatestates hex and times in ns
		[0x01,math.floor(PERIOD*DUTY_CYCLE)], #all gates open for 48ms
		[0x00,math.floor(PERIOD*(1-DUTY_CYCLE))] #all gates closed for 48ms
		]
	if sum([entry[1] for entry in my_GCL])!=PERIOD:
		my_GCL[0][1]+=1
	RT_HAT_TAS.set_GCL(my_GCL,port) #set GCL of port
	RT_HAT_TAS.ADMIN_BASE_TIME=PHASE
	RT_HAT_TAS.ADMIN_CYCLE_TIME=0#0:automatic calculated from sum of GCL
	RT_HAT_TAS.ADMIN_CYCLE_TIME_EXT=0
	RT_HAT_TAS.TRIGGER_CNT=COUNT
	RT_HAT_TAS.apply(port)#apply tas settings to port 
