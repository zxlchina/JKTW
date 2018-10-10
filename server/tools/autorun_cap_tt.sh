#/bin/bash


killall chrome

logname="./log/cap_tt.log"

cd /home/lichzhang/release/JKTW/server/tools
date >> $logname
python3 ./cap_tt.py >> $logname
date >> $logname
echo "####################################" >> $logname
