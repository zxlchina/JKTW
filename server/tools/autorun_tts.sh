#/bin/bash


#killall chrome

cd /home/lichzhang/code/JKTW/server/tools
date >> tts_log
python3 ./tts_job.py >> tts_log
