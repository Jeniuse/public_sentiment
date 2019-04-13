#!/bin/bash
echo 'start spark streaming'
ss='analysis.py'
cd poa_ss
function start_ss(){
    /usr/hdp/current/spark2-client/bin/spark-submit \
    --name "KafkaDirectAnalysis" \
    --master local[10] \
    --executor-memory 10G \
    --driver-memory 10G  \
    --driver-cores 10 \
    --executor-cores 10 \
    --jars spark-streaming-kafka-0-8-assembly_2.11-2.1.1.jar \
    --conf spark.default.parallelism=3 \
    --conf spark.ui.port=7077 \
    analysis.py
}
ps -fe|grep $ss |grep -v grep
if [ $? -ne 0 ]
then
start_ss
else
echo "spark streaming is running"
fi


