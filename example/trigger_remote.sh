#!/bin/bash
time=$(curl 192.168.14.161:5000/time)
start=$(( $time + 3000000000))
curl 192.168.14.161:5000/trigger -d '{"START": '$start'}' -H 'Content-Type: application/json' &
curl 192.168.14.172:5000/trigger -d '{"START": '$start'}' -H 'Content-Type: application/json' &
wait
echo "done"


