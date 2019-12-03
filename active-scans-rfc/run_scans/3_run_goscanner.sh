#!/bin/bash

export PATH=/home/tls13/tls13/go/bin/:$PATH

EPOCH=`basename $1 | sed 's/_.*//g'`
export LC_ALL=C

INFILE=$1
INFILE_BASE=`basename $1`
OUTPUT_DIR=$2/$EPOCH
META_DIR=${OUTPUT_DIR}/meta
USER=$3

GOSCANNER_LOG_FILE=${META_DIR}/{$INFILE_BASE}.goscanner.log
GOSCANNER_OUTPUT_DIR=${OUTPUT_DIR}/
TCPDUMP_OUTPUT_FILE=${OUTPUT_DIR}/${INFILE_BASE}.goscanner.tcpdump.pcap
TCPDUMP_LOGFILE=${META_DIR}/${INFILE_BASE}.goscanner.tcpdump.log

mkdir -p $META_DIR

# Increase file limit
ulimit -Hn 1024000
ulimit -Sn 65535

# TCP: too many orphaned sockets
echo 16384 > /proc/sys/net/ipv4/tcp_max_orphans

GOSCANNER=/home/tls13/tls13/workspaces/goscanner/src/github.com/tumi8/goscanner/goscanner
GOSCANNER_CONF_FILE=/home/tls13/tls13/experiment/conf/goscanner.conf
TCPDUMP=/usr/sbin/tcpdump
TCPDUMP_IFACE=eno1

# Create meta file
echo $DATE >> ${META_DIR}/$INFILE_BASE.goscanner.meta

# copy configuration
CONF_BASENAME=`basename $GOSCANNER_CONF_FILE`
cp $GOSCANNER_CONF_FILE $META_DIR/$INFILE_BASE.$CONF_BASENAME

# shuffle input
shuf $INFILE > $INFILE.shuf

# run tcpdump
$TCPDUMP -n -i $TCPDUMP_IFACE -w $TCPDUMP_OUTPUT_FILE "tcp port 443" 2> $TCPDUMP_LOGFILE &
TCPDUMPPID=$!
sleep 5

# run goscanner
$GOSCANNER -C $GOSCANNER_CONF_FILE -i $INFILE.shuf -o $GOSCANNER_OUTPUT_DIR -l $GOSCANNER_LOG_FILE
sleep 5

# stop tcpdump
/bin/kill -INT $TCPDUMPPID
sleep 5

# rename output files
mv $OUTPUT_DIR/hosts.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.hosts.csv
mv $OUTPUT_DIR/http.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.http.csv
mv $OUTPUT_DIR/certs.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.certs.csv
mv $OUTPUT_DIR/cert_host_rel.csv $OUTPUT_DIR/$INFILE_BASE.goscanner.cert_host_rel.csv

chown -R $USER:$USER $OUTPUT_DIR
