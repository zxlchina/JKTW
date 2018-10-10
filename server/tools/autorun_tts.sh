#/bin/bash


#killall chrome

logname="./log/tts.log"

cd /home/lichzhang/release/JKTW/server/tools
date >> $logname
python3 ./tts_job.py >> $logname
