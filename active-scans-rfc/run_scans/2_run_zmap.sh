#!/bin/bash

export PATH=/home/tls13/tls13/go/bin/:$PATH
export GOPATH=/home/tls13/tls13/experiment/lib/go/
export GOROOT=/home/tls13/tls13/go/

export LC_ALL=C

INFILE=$1
EPOCH=`basename $1 | sed 's/_.*//g'`
DOMAIN_FILE=`echo $INFILE | sed 's/.prefixed.sortu.shuf$//g'`
INFILE_BASE=`basename $1`
DATA_OUTPUT_DIR=$2/$EPOCH/
META_DIR=${DATA_OUTPUT_DIR}/meta
ZMAP_LOG_FILE=${META_DIR}/zmap.log
ZMAP_OUTPUT_FILE=${DATA_OUTPUT_DIR}/$INFILE_BASE.zmap
OWNER=$3

mkdir -p $META_DIR

# Increase file limit
ulimit -Hn 1024000
ulimit -Sn 65535

# TCP: too many orphaned sockets
echo 16384 > /proc/sys/net/ipv4/tcp_max_orphans

ZMAP=/home/tls13/tls13/repos/github.com/zmap/zmap/src/zmap
ZMAP_CONF_FILE=/home/tls13/tls13/experiment/conf/zmap.conf

# Create meta file
echo $DATE >> ${META_DIR}/zmap.meta

# copy configuration
cp $ZMAP_CONF_FILE $META_DIR

# run zmap
$ZMAP --config $ZMAP_CONF_FILE --whitelist-file $INFILE --output-file $ZMAP_OUTPUT_FILE --log-file $ZMAP_LOG_FILE

cut -f 1 -d, $ZMAP_OUTPUT_FILE | sort -u > $ZMAP_OUTPUT_FILE.ip.sortu
join -t, $ZMAP_OUTPUT_FILE.ip.sortu $DOMAIN_FILE > $ZMAP_OUTPUT_FILE.ip.sortu.joined

chown -R $OWNER:$OWNER $DATA_OUTPUT_DIR $META_DIR
