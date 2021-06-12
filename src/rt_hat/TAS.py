from rt_hat import FPGA as RT_HAT_FPGA
import time
from goto import with_goto

__GCL=[[[],[]],[[],[]],[[],[]]]
ADMIN_BASE_TIME=0
ADMIN_CYCLE_TIME=0
ADMIN_CYCLE_TIME_EXT=0
__TASvar={}
DEBUG_ENABLE=False
DEBUG_OUTPUT=False
__pollcount=100
__timewindow=2000000000

def __init_TASvar():
	global __TASvar
	__TASvar["granularity"]=RT_HAT_FPGA.reg_read("C_ADDR_TM_SCHED_TAS_TICK_GRANULARITY")
	if (__TASvar["granularity"] == 0) or (__TASvar["granularity"] > 10):
		raise Exception("TAS granularity "+str(__TASvar["granularity"])+" not valid! Maybe your FPGA bitstream don't supports this feature.")
	__TASvar["PORT_TSN_width"]=0x800
	__TASvar["GateControl_list_base"]=RT_HAT_FPGA.get_addr("C_ADDR_SCHED_TAS_GCL_MEM_GATES")
	__TASvar["GateControl_list_entry_length"]=4
	__TASvar["GateControl_list_length"]=RT_HAT_FPGA.reg_read("C_ADDR_TM_SCHED_TAS_ADMIN_GCL_LEN")
	__TASvar["GateControl_TIME_list_base"]=RT_HAT_FPGA.get_addr("C_ADDR_SCHED_TAS_GCL_MEM_TIMES")
	__TASvar["GateControl_TIME_list_entry_length"]=4
	__TASvar["GateControl_TIME_list_length"]=RT_HAT_FPGA.reg_read("C_ADDR_TM_SCHED_TAS_ADMIN_GCL_LEN")
#	__TASvar[""]=RT_HAT_FPGA.get_addr("")

def __checkport(port):
	if port>4:
		raise Exception("Invalid TAS port ID:"+str(port))
	
def get_TASvar(name):
	global __TASvar
	return __TASvar[name]
	
def __debug(message):
	global DEBUG_ENABLE
	if DEBUG_ENABLE:
		print(message)
	
def init(envfile):
	global __granularity
	global DEBUG_ENABLE
	global DEBUG_OUTPUT
	RT_HAT_FPGA.DEBUG_ENABLE=DEBUG_ENABLE
	RT_HAT_FPGA.DEBUG_OUTPUT=DEBUG_OUTPUT
	RT_HAT_FPGA.init(envfile)
	
	__init_TASvar()

def set_GCL(new_GCL,port):
	global __GCL
	global __TASvar
	__checkport(port)
	for entry in new_GCL:
		if len(entry) != 2:
			raise Exception("entry "+str(entry)+" of gcl is not valid")
		if (int(entry[1]) % int(__TASvar["granularity"]))>0:
			print("Warning: entry "+str(entry)+" of GCL don't match minimal TAS ganularity of "+str(__TASvar["granularity"])+"ns")
	__GCL[port]=new_GCL
	
	
def get_GCL(port):
	global __GCL
	__checkport(port)
	return __GCL[port]

def __portalign_base_addr(addr,port):
	__checkport(port)
	return RT_HAT_FPGA.get_addr(addr)+port*get_TASvar("PORT_TSN_width")
	
def __get_cycle_time(port):
	global __GCL
	cycle=0
	for entry in __GCL[port]:
		cycle+=entry[1]
	return cycle
	
def __apply_GCL(port):
	ID=0
	for GCL_entry in __GCL[port]:
		RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_SCHED_TAS_GCL_MEM_GATES",port) + get_TASvar("GateControl_list_entry_length") * ID, GCL_entry[0])
		RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_SCHED_TAS_GCL_MEM_TIMES",port) + get_TASvar("GateControl_TIME_list_entry_length") * ID, GCL_entry[1])
		ID=ID+1
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_GCL_LEN",port),len(__GCL[port]))
	

	
@with_goto		
def apply(port):
	global ADMIN_BASE_TIME
	global ADMIN_CYCLE_TIME
	global ADMIN_CYCLE_TIME_EXT
	global __pollcount
	global __timewindow
	__checkport(port)
	__apply_GCL(port)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_GATE_ENABLE",port),1) #enable_TAS	
	if ADMIN_CYCLE_TIME==0:
		ADMIN_CYCLE_TIME=__get_cycle_time(port)
		__debug("calc cycle time to sum of GCL: "+str(ADMIN_CYCLE_TIME)+"ns")
	poll=0
	__debug("wait for config_pending is cleared")
	while RT_HAT_FPGA.ll_read(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE_PENDING",port)) > 0:
		poll+=1
		time.sleep(0.01)
		if poll> __pollcount:
			raise Exception("TAS pending to long!")
			break
	currenttime=RT_HAT_FPGA.now()
	__debug("Current time: "+str(currenttime))
	label .timecalc
	if ADMIN_BASE_TIME<currenttime:
		__debug("Oper time in the past, using time machine!")
		diff=currenttime-ADMIN_BASE_TIME
		cycles=int(diff/ADMIN_CYCLE_TIME)+2
		ADMIN_BASE_TIME=ADMIN_BASE_TIME+cycles*ADMIN_CYCLE_TIME
	poll=0
	__debug("ADMIN_BASE_TIME first iteration:"+str(ADMIN_BASE_TIME))
	while ADMIN_BASE_TIME<currenttime:
		ADMIN_BASE_TIME=ADMIN_BASE_TIME+ADMIN_CYCLE_TIME
		currenttime=RT_HAT_FPGA.now()
		poll+=1
		if poll> __pollcount*10:
			raise Exception("no valid ADMIN_BASE_TIME found!")
	__debug("ADMIN_BASE_TIME:"+str(ADMIN_BASE_TIME))
	while ADMIN_BASE_TIME>(currenttime+__timewindow):
		currenttime=RT_HAT_FPGA.now()
		sleeptime_ns=ADMIN_BASE_TIME-currenttime-__timewindow
		time.sleep(sleeptime_ns/1000000000)
	if ADMIN_BASE_TIME<currenttime:
		__debug("sleeped to long , calculating basetime again...")
		goto .timecalc
	ADMIN_BASE_TIME&=0xffffffff
	CONFIG_CHANGE_TIME=ADMIN_BASE_TIME
	CYCLE_START_TIME=ADMIN_BASE_TIME
#	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE_TIME",port),ADMIN_BASE_TIME)
#	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CYCLE_START_TIME",port),ADMIN_BASE_TIME)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_BASE_TIME",port),ADMIN_BASE_TIME)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_CYCLE_TIME",port),ADMIN_CYCLE_TIME)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_CYCLE_TIME_EXT",port),ADMIN_CYCLE_TIME_EXT)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE",port),1)#trigger config
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
		
	
