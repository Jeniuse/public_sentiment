#!/bin/bash
source /etc/profile
cd /home/public_sentiment
source ./stop_proc.sh together.py
sleep 2s
source ./stop_proc.sh scrapy
sleep 3s
echo 'restarting scrapy'
nohup ./start-scrapy.sh > scrapy_output.log 2>&1 &
sleep 5s
# echo 'delete log'
# rm -rf scrapy_output.log
echo 'finish'
