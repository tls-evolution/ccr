#!/bin/bash

python3 plot2.py --basedir data/alexa-A-www
python3 plot2.py --basedir data/_com-net-org
python3 plot2.py --basedir data/_all-but-com-net-org
python3 plot2.py --basedir data/_all

for d in $(ls data_AS/ | grep "^_"); do python3 plot2.py --basedir data_AS/$d --nonfixedylimit | tee plot_$d.out; echo "$d done"; done;

