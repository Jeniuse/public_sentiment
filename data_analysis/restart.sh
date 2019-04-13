#!/bin/bash
source /etc/profile
cd /home/public_sentiment
source ./stop_proc.sh streaming
sleep 2s
source ./stop_proc.sh analysis.py
sleep 3s
echo 'restarting'
nohup ./start-spark-streaming.sh > spark_output.log 2>&1 &
sleep 5s
# echo 'delete log'
# rm -rf spark_output.log
echo 'finish'
