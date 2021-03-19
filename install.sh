#!/bin/bash
IP_addr="192.168.1.110"
python3 -m build &
ssh pi@$IP_addr 'python3 -m pip uninstall rt-hat-inr -y '&
wait
scp dist/rt_hat_inr-*-py3-none-any.whl pi@$IP_addr:~/ &
scp example/* pi@$IP_addr:~/ &
wait
ssh pi@$IP_addr 'python3 -m pip install rt_hat_inr-*-py3-none-any.whl'
ssh pi@$IP_addr 'python3 TAS_test.py'

