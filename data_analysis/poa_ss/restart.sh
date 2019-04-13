#!/bin/bash
#
source ../stop_proc.sh streaming
sleep 2s
source ../stop_proc.sh analysis.py
sleep 2s
echo 'restarting'
nohup ../start-spark-streaming.sh > ../spark_output.log 2>&1 &
sleep 10s
#echo 'delete log'
#rm -rf spark_output.log
echo 'finish'
