#!/bin/bash

python3 plot2.py --basedir data/alexa-A-www | tee plot_alexa-A-www.out
python3 plot2.py --basedir data/_com-net-org | tee plot__com-net-org.out
python3 plot2.py --basedir data/_all-but-com-net-org | tee plot__all-but-com-net-org.out
python3 plot2.py --basedir data/_all | tee plot__all.out

for d in $(ls data_AS/ | grep "^_"); do python3 plot2.py --basedir data_AS/$d --nonfixedylimit | tee plot_$d.out; echo "$d done"; done;

python3 plot2.py --basedir data_AS/_SINGLEHOP --basedirtwo data_AS/_OVH --nonfixedylimit

