# python functions for basic fpga accesses
environment={}


#init, load environment addresses
def init(envfile):
	global environment
	with open(envfile) as file_in:
    for line in file_in:
        print(line)
