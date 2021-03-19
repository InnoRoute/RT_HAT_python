# python functions for basic fpga accesses
import os
import time
environment={}
pollcount=100


#init, load environment addresses
def init(envfile):
	global environment
	with open(envfile) as file_in:
		for line in file_in:
			if "C_ADDR" in line:    
				C_NAME=line.split('"')[0].split('=')[0].replace(" ", "")
				C_VALUE=int(line.split('"')[1].replace(" ", ""),16)
				environment[C_NAME]=C_VALUE
				
#low level register access	
def ll_read(address):
	global pollcount
	poll=0
	while int(os.popen('cat /proc/InnoRoute/SPI_write').read())>0:
		time.sleep(0.1)
		poll=poll+1
		if poll>pollcount:
			return 0
	os.popen('echo '+str(address)+' > /proc/InnoRoute/SPI_read')
	return int(os.popen('cat /proc/InnoRoute/SPI_data').read(),16)


#low level register access
def ll_write(address,value):
	global pollcount
	poll=0
	while int(os.popen('cat /proc/InnoRoute/SPI_write').read())>0:
		time.sleep(0.1)
		poll=poll+1
		if poll>pollcount:
			return 0
	os.popen('echo '+str(value)+' > /proc/InnoRoute/SPI_data')
	os.popen('echo '+str(address)+' > /proc/InnoRoute/SPI_write')

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
	
def status():
	FPGA_status={}
	FPGA_status["ID"]=hex(reg_read("C_ADDR_SPI_FPGA_ID0")+(reg_read("C_ADDR_SPI_FPGA_ID1") << 32))
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
	FPGA_status["ACCESS_ERROR"]=hex(reg_read("C_ADDR_SPI_ACCESS_ERROR"))
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
	
	
