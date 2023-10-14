# python functions for basic fpga accesses
import os
import time
import fcntl, array
from fcntl import ioctl
environment={}
pollcount=100
DEBUG_ENABLE=False
DEBUG_OUTPUT=False
MMI_FALLBACK=False #use old mmi method, not ioctl
__mmi_file=0


#init, load environment addresses
def init(envfile):
	global environment
	global __mmi_file
	global MMI_FALLBACK
	global DEBUG_ENABLE
	with open(envfile) as file_in:
		for line in file_in:
			if "C_ADDR" in line:    
				C_NAME=line.split('"')[0].split('=')[0].replace(" ", "")
				C_VALUE=int(line.split('"')[1].replace(" ", ""),16)
				environment[C_NAME]=int(C_VALUE)
			if "FEATURE_" in line and not "FEATURE_MAP" in line:
				C_NAME=line.split('"')[0].split('=')[0].replace(" ", "")
				C_VALUE=line.split('"')[1]
				environment[C_NAME]=C_VALUE
	__mmi_file=open("/proc/InnoRoute/SPI_write")
	try:
		if(reg_read('C_ADDR_SPI_FPGA_ID0')==0): #if id is ioctl read not working (or other error)
			MMI_FALLBACK=True
	except:
		MMI_FALLBACK=True
	
				
#low level register access
def ll_read_ioctl(address): #new faster ioctl function
	global DEBUG_OUTPUT
	global __mmi_file
	if DEBUG_OUTPUT:
		print("TNbar1 "+hex(address))
	buf = array.array('L', [address,0])
	rv = fcntl.ioctl(__mmi_file, 0x80046162, buf)
	return buf[1]
	

def ll_read(address):
	global pollcount
	global DEBUG_OUTPUT
	global MMI_FALLBACK
	if(MMI_FALLBACK==False):
		return ll_read_ioctl(address)
	poll=0
	while int(os.popen('cat /proc/InnoRoute/SPI_write').read())>0:
		time.sleep(0.01)
		poll=poll+1
		if poll>pollcount:
			return 0
	os.popen('echo '+str(address)+' > /proc/InnoRoute/SPI_read')
	if DEBUG_OUTPUT:
		print("TNbar1 "+hex(address))
	time.sleep(0.01)
	return int(os.popen('cat /proc/InnoRoute/SPI_data').read(),16)
	
def __debug(message):
	global DEBUG_ENABLE
	if DEBUG_ENABLE:
		print(message)

#low level register access
def ll_write_ioctl(address,value): #new faster ioctl function
	global DEBUG_OUTPUT
	global __mmi_file
	if DEBUG_OUTPUT:
		print("TNbar1 "+hex(address)+" "+hex(value))
	__debug(hex(value)+" written to "+hex(address))
	buf = array.array('L', [address,value])
	rv = fcntl.ioctl(__mmi_file, 0x40046161, buf)

	
def ll_write(address,value):
	global pollcount
	global DEBUG_OUTPUT
	global MMI_FALLBACK
	if(MMI_FALLBACK==False):
		ll_write_ioctl(address,value)
		return
	poll=0
	while int(os.popen('cat /proc/InnoRoute/SPI_write').read())>0:
#		time.sleep(0.1)
		poll=poll+1
		if poll>pollcount:
			__debug("write error to "+hex(address));
			return 0
	os.popen('echo '+str(value)+' > /proc/InnoRoute/SPI_data')
	os.popen('echo '+str(address)+' > /proc/InnoRoute/SPI_write')
	time.sleep(0.01)
	__debug(hex(value)+" written to "+hex(address))
	if DEBUG_OUTPUT:
		print("TNbar1 "+hex(address)+" "+hex(value))

#check if address available	
def check_register(register):
	global environment
	if register in environment:
		return True
	else:
		return False
		
def reg_read(register):
	global environment
	if not check_register(register):
		raise Exception("register "+register+" not defined") 
	return ll_read(environment[register])


def reg_write(register,value):
	global environment
	if not check_register(register):
		raise Exception("register "+register+" not defined")
	ll_write(environment[register],value)
	
def get_addr(register):
	if not check_register(register):
		raise Exception("register "+register+" not defined")
	return environment[register]
	
def status():
	FPGA_status={}
	FPGA_status["ID"]=hex(reg_read("C_ADDR_SPI_FPGA_ID0")+(reg_read("C_ADDR_SPI_FPGA_ID1") << 32))
	FPGA_status["ID: FUSE_DNA"]=hex(int((bin(reg_read("C_ADDR_SPI_FPGA_ID0")+(reg_read("C_ADDR_SPI_FPGA_ID1") << 32))[2:])[::-1], 2))
	FPGA_status["ID: DNA_PORT"] = hex(int(bin(reg_read("C_ADDR_SPI_FPGA_ID0") + (reg_read("C_ADDR_SPI_FPGA_ID1") << 32))[2:], 2))
	FPGA_status["ACCESS_ERROR"]=hex(reg_read("C_ADDR_SPI_ACCESS_ERROR"))
	FPGA_status["Board_REV"]=hex(reg_read("C_ADDR_SPI_BOARD_REV"))
	FPGA_status["TEMP"]=reg_read("C_ADDR_SPI_FPGA_TEMP")*504/4096-273
	FPGA_status["FPGA_REV"]=hex(reg_read("C_ADDR_SPI_FPGA_REV"))	
	FPGA_status["FEATURE_MAP"]=hex(reg_read("C_ADDR_SPI_FEATURE_MAP"))
	FPGA_status["INT_PENDING"]=hex(reg_read("C_ADDR_SPI_INT_PENDING"))
	FPGA_status["INT_STATUS"]=hex(reg_read("C_ADDR_SPI_INT_STATUS"))
	FPGA_status["INT_SET_EN"]=hex(reg_read("C_ADDR_SPI_INT_SET_EN"))
	FPGA_status["INT_CLR_EN"]=hex(reg_read("C_ADDR_SPI_INT_CLR_EN"))
	FPGA_status["FPGA_ALARM"]=hex(reg_read("C_ADDR_SPI_FPGA_ALARM"))
	FPGA_status["CONFIG_CHECK"]=hex(reg_read("C_ADDR_SPI_CONFIG_CHECK"))
	FPGA_status["LICENSE"]=hex(reg_read("C_ADDR_SPI_LICENSE"))
	FPGA_status["FIFO_OVERFLOW"]=hex(reg_read("C_ADDR_SPI_FIFO_OVERFLOW"))
	FPGA_status["FIFO_UNDERRUN"]=hex(reg_read("C_ADDR_SPI_FIFO_UNDERRUN"))
	FPGA_status["EXT_INTERRUPT"]=hex(reg_read("C_ADDR_SPI_EXT_INTERRUPT"))
	FPGA_status["EVENT"]=hex(reg_read("C_ADDR_SPI_EVENT"))
	FPGA_status["MMI_INT_BITMAP"]=hex(reg_read("C_ADDR_SPI_MMI_INT_BITMAP"))
	FPGA_status["BACKPRESSURE"]=hex(reg_read("C_ADDR_SPI_BACKPRESSURE"))
	FPGA_status["RESET"]=hex(reg_read("C_ADDR_SPI_RESET"))
	FPGA_status["TEST_DRIVE"]=hex(reg_read("C_ADDR_SPI_TEST_DRIVE"))
	FPGA_status["TEST_VALUE"]=hex(reg_read("C_ADDR_SPI_TEST_VALUE"))	
	return FPGA_status
	
def license_features():
	FPGA_features=[]	
	featuremap=reg_read("C_ADDR_SPI_LICENSE")>>8
	for x in range(32):
		if check_register("FEATURE_"+str(x)+'_NAME'):
			FPGA_features.append({"name":environment["FEATURE_"+str(x)+'_NAME'],"description":environment["FEATURE_"+str(x)+'_DESCRIPTION'],"status":(featuremap & (1<< x)) > 0})
		
	return FPGA_features
	
def now():
#		BRIDGE_clock_value_L=reg_read("C_ADDR_RTC_BRIDGE_LOW");
#		BRIDGE_clock_value_H=reg_read("C_ADDR_RTC_BRIDGE_HIGH");
#		CTRLD_clock_value_L=reg_read("C_ADDR_RTC_CTRLD_LOW");
#		CTRLD_clock_value_H=reg_read("C_ADDR_RTC_CTRLD_HIGH");
#		return CTRLD_clock_value_L + (CTRLD_clock_value_H<<32);
#	prevent interactions with ptp clock access
		return int(os.popen('sudo phc_ctl /dev/ptp0 get').read().split(' ')[4].split('\n', 1)[0].replace('.', ''))
		
	
	
