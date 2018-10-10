#/bin/bash


#killall chrome

cd /home/lichzhang/code/JKTW/server/tools
date >> content_log
python3 ./cap_tt_content.py >> content_log
