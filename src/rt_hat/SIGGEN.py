from rt_hat import TAS as RT_HAT_TAS
import math
import time
#RT_HAT_TAS.DEBUG_ENABLE=True
#RT_HAT_TAS.DEBUG_OUTPUT=True
DEBUG_ENABLE=False
DEBUG_OUTPUT=False
__pollcount=1000

def init(envfile):
	global __granularity
	global DEBUG_ENABLE
	global DEBUG_OUTPUT
	RT_HAT_TAS.DEBUG_ENABLE=DEBUG_ENABLE
	RT_HAT_TAS.DEBUG_OUTPUT=DEBUG_OUTPUT
	RT_HAT_TAS.AUTOCORRECT_GCL=False
	RT_HAT_TAS.init(envfile)

def trigger(ADMIN_BASE_TIME):
	global DEBUG_ENABLE
	global __pollcount
	now=RT_HAT_TAS.RT_HAT_FPGA.now()
	if ADMIN_BASE_TIME-now<50000000: #50ms is an empirical value, free free to adjust, if to less, you have to reset the FPGA
		if DEBUG_ENABLE:
			print("trigger failed, time to short:"+str(ADMIN_BASE_TIME-now)+"ns")
		return 1
	ADMIN_BASE_TIME&=0xffffffff
	while RT_HAT_TAS.RT_HAT_FPGA.ll_read(RT_HAT_TAS.get_portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE_PENDING",2)) > 0:
		time.sleep(0.01)

	RT_HAT_TAS.RT_HAT_FPGA.ll_write(RT_HAT_TAS.get_portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_BASE_TIME",2),ADMIN_BASE_TIME)
	if RT_HAT_TAS.TRIGGER_CNT>0:
		RT_HAT_TAS.RT_HAT_FPGA.ll_write(RT_HAT_TAS.get_portalign_base_addr("C_ADDR_TM_SCHED_TAS_TRIGGER_CNT",2),RT_HAT_TAS.TRIGGER_CNT)
	RT_HAT_TAS.RT_HAT_FPGA.ll_write(RT_HAT_TAS.get_portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE",2),1)#trigger config
	return 0
	
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
#	if sum([entry[1] for entry in my_GCL])!=PERIOD:
#		my_GCL[0][1]+=1
	RT_HAT_TAS.set_GCL(my_GCL,port) #set GCL of port
	RT_HAT_TAS.set_trigger_en(1)
	RT_HAT_TAS.ADMIN_BASE_TIME=PHASE
	RT_HAT_TAS.ADMIN_CYCLE_TIME=0#0:automatic calculated from sum of GCL
	RT_HAT_TAS.ADMIN_CYCLE_TIME_EXT=0
	RT_HAT_TAS.TRIGGER_CNT=COUNT
	RT_HAT_TAS.apply(port)#apply tas settings to port 
