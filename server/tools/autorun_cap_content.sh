#/bin/bash


#killall chrome

logname="./log/content.log"

cd /home/lichzhang/release/JKTW/server/tools
date >> $logname
python3 ./cap_tt_content.py >> $logname
