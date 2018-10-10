#/bin/bash


killall chrome

cd /home/lichzhang/code/JKTW/server/tools
date >> log
python3 ./cap_tt.py >> log
date >> log
echo "####################################" >> log
