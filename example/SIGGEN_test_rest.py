from rt_hat import SIGGEN as RT_HAT_SIGGEN
import time
import flask
from flask import Flask, request
app = Flask(__name__)


@app.route('/configure', methods = ['POST'])
def configure():
    if request.method == 'POST':
        print("POST'd", request.json)
    DUTY_CYCLE=0.5
    PERIOD=960000
    START=request.json['START'] #start in 10s
    CNT=10
    RT_HAT_SIGGEN.set(DUTY_CYCLE,PERIOD,START,CNT)
    return "handled"
    
@app.route('/trigger', methods = ['POST'])
def trigger():
    if request.method == 'POST':
        print("POST'd", request.json)
    DUTY_CYCLE=0.5
    PERIOD=960000
    START=request.json['START'] #start in 10s
    CNT=10
    RT_HAT_SIGGEN.set(DUTY_CYCLE,PERIOD,START,CNT)
    wait=100000000
    RT_HAT_SIGGEN.trigger(START+wait*1)
    RT_HAT_SIGGEN.trigger(START+wait*2)
    RT_HAT_SIGGEN.trigger(START+wait*3)
    RT_HAT_SIGGEN.trigger(START+wait*4)
    return "handled"
    
@app.route('/time')
def time():
    return str(RT_HAT_SIGGEN.RT_HAT_TAS.RT_HAT_FPGA.now())
    

if __name__ == '__main__':
	RT_HAT_SIGGEN.init("/usr/share/InnoRoute/hat_env.sh")
	app.run(host="0.0.0.0", port=5000,debug=True)




