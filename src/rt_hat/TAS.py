from rt_hat import FPGA as RT_HAT_FPGA
import time
from goto import with_goto

__GCL=[[[],[]],[[],[]],[[],[]]]
ADMIN_BASE_TIME=0
ADMIN_CYCLE_TIME=0
ADMIN_CYCLE_TIME_EXT=0
TRIGGER_CNT=0
__TASvar={}
DEBUG_ENABLE=False
DEBUG_OUTPUT=False
__correct_value_up=True
AUTOCORRECT_GCL=True
__pollcount=1000
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

def get_granularity():
	global __TASvar
	return int(__TASvar["granularity"])
	
def init(envfile):
	global __granularity
	global DEBUG_ENABLE
	global DEBUG_OUTPUT
	RT_HAT_FPGA.DEBUG_ENABLE=DEBUG_ENABLE
	RT_HAT_FPGA.DEBUG_OUTPUT=DEBUG_OUTPUT
	RT_HAT_FPGA.init(envfile)
	
	__init_TASvar()

def __correct_value(value):
	granularity=get_granularity()
	global __correct_value_up
	if (__correct_value_up==True):
		__correct_value_up=False
		while(value%granularity):
			value-=1
	else:
		__correct_value_up=True
		while(value%granularity):
			value+=1
	return value
		
	
def __blowup_GCL(GCL):
	global DEBUG_ENABLE
	global __correct_value_up
	maxfactor=2
	big_GCL=[[entry[0],__correct_value(entry[1])] for entry in GCL]
	granularity=get_granularity()
	cycle=0
	factor=1
	for entry in GCL:
		cycle+=entry[1]
	cycle_new=cycle
	if(DEBUG_ENABLE==True):
		print("cycle: "+str(cycle))
	error=True
	pos=0
	while error==True:
		
		if factor<maxfactor:	
			factor+=1
			big_GCL=big_GCL+GCL
		if len(GCL)%2==0:
			__correct_value_up=not __correct_value_up
		big_GCL=[[entry[0],__correct_value(entry[1])] for entry in big_GCL]
		cycle_new=0
		for entry in big_GCL:
			cycle_new+=entry[1]
		error_ns=(factor*cycle)-cycle_new
		if(DEBUG_ENABLE==True):
			print("error:"+str(error_ns))
#		pos=factor+1
		while (error_ns!=0):
			if error_ns>granularity:
				old=big_GCL[pos][1]
				if error_ns<0:
					__correct_value_up=True
					big_GCL[pos][1]=__correct_value(big_GCL[pos][1]+round(granularity/2))
				else:				
					__correct_value_up=False
					big_GCL[pos][1]=__correct_value(big_GCL[pos][1]-round(granularity/2))
				error_ns-=big_GCL[pos][1]-old
			else: 
				big_GCL[pos][1]+=error_ns
				error_ns=0
				maxfactor+=1
			pos+=1
			if pos>len(big_GCL):
				pos=0
		big_GCL=[[entry[0],__correct_value(entry[1])] for entry in big_GCL]
		cycle_new=0
		for entry in big_GCL:
			cycle_new+=entry[1]
		if cycle_new==(factor*cycle):
			error=False
		if(DEBUG_ENABLE==True):
			print(big_GCL)
		

#	while (cycle*factor)!:
#		factor+=1
	if(DEBUG_ENABLE==True):
		print("blowing up GCL by factor "+str(factor)+" new cycle time is "+str(sum([entry[1] for entry in big_GCL]))+" mean cycle is "+str(sum([entry[1] for entry in big_GCL])/factor))
	
	
	
	return big_GCL

def set_GCL(new_GCL,port):
	global __GCL
	global __TASvar
	__checkport(port)
	for entry in new_GCL:
		if len(entry) != 2:
			raise Exception("entry "+str(entry)+" of gcl is not valid")
	if AUTOCORRECT_GCL:
		new_GCL=__blowup_GCL(new_GCL)	
	__GCL[port]=[]
	for entry in new_GCL:	
		if (int(entry[1]) % int(__TASvar["granularity"]))>0:
			print("Warning: entry "+str(entry)+" of GCL don't match minimal TAS ganularity of "+str(__TASvar["granularity"])+"ns")
		__correct_value_up=False		
		__GCL[port].append([entry[0],__correct_value(entry[1])])
	
	
	
	
def get_GCL(port):
	global __GCL
	__checkport(port)
	return __GCL[port]

def get_portalign_base_addr(addr,port):
	return __portalign_base_addr(addr,port)
	
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
	
def set_trigger_en(val):
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_TRIGGER_EN",2),val)
	

	
@with_goto		
def apply(port):
	global ADMIN_BASE_TIME
	global ADMIN_CYCLE_TIME
	global ADMIN_CYCLE_TIME_EXT
	global __pollcount
	global __timewindow
	global TRIGGER_CNT
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
		if sleeptime_ns>0:
			__debug("sleeping: "+str(sleeptime_ns)+"ns")
			time.sleep(sleeptime_ns/1000000000)
		else:
			break
	#currenttime=RT_HAT_FPGA.now()
	if ADMIN_BASE_TIME<currenttime:
		__debug("sleeped to long , calculating basetime again...")
		ADMIN_BASE_TIME-=ADMIN_CYCLE_TIME*10
		goto .timecalc
	ADMIN_BASE_TIME&=0xffffffff
	CONFIG_CHANGE_TIME=ADMIN_BASE_TIME
	CYCLE_START_TIME=ADMIN_BASE_TIME
#	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE_TIME",port),ADMIN_BASE_TIME)
#	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CYCLE_START_TIME",port),ADMIN_BASE_TIME)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_BASE_TIME",port),ADMIN_BASE_TIME)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_CYCLE_TIME",port),ADMIN_CYCLE_TIME)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_ADMIN_CYCLE_TIME_EXT",port),ADMIN_CYCLE_TIME_EXT)
	if TRIGGER_CNT>0 and port==2:
		RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_TRIGGER_CNT",port),TRIGGER_CNT)
	RT_HAT_FPGA.ll_write(__portalign_base_addr("C_ADDR_TM_SCHED_TAS_CONFIG_CHANGE",port),1)#trigger config
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
		
	
