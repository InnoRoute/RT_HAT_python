#!/bin/bash
IP_addr="192.168.178.169"
rm dist/*
python3 -m build &
ssh pi@$IP_addr 'sudo python3 -m pip uninstall rt-hat-inr -y '
ssh pi@$IP_addr 'python3 -m pip uninstall rt-hat-inr -y '&
wait
ssh pi@$IP_addr 'rm rt_hat_inr-*-py3-none-any.whl'
scp dist/rt_hat_inr-*-py3-none-any.whl pi@$IP_addr:~/ &
scp example/* pi@$IP_addr:~/ &
wait
ssh pi@$IP_addr 'sudo python3 -m pip install rt_hat_inr-*-py3-none-any.whl'



#IP_addr="192.168.14.172"
#ssh pi@$IP_addr 'sudo python3 -m pip uninstall rt-hat-inr -y '
#ssh pi@$IP_addr 'python3 -m pip uninstall rt-hat-inr -y '&
#wait
#ssh pi@$IP_addr 'rm rt_hat_inr-*-py3-none-any.whl'
#scp dist/rt_hat_inr-*-py3-none-any.whl pi@$IP_addr:~/ &
#scp example/* pi@$IP_addr:~/ &
#wait
#ssh pi@$IP_addr 'sudo python3 -m pip install rt_hat_inr-*-py3-none-any.whl'


