#!/bin/bash

export PATH=/home/tls13/tls13/go/bin/:$PATH
export GOPATH=/home/tls13/tls13/experiment/lib/go/
export GOROOT=/home/tls13/tls13/go/

export LC_ALL=C
INFILE=$1
INFILE_BASE=`basename $1`
EPOCH=`echo $INFILE_BASE | sed 's/_.*//g'`
OUTPUT_DIR=$2
OUTBASE=$OUTPUT_DIR/$EPOCH/${INFILE_BASE}
HASHMAPSIZE=10000
RETRIES=50
RESOLVERS=/etc/resolv-local.conf
TYPE=A
INTERVAL=200

BLACKLIST_DIR=/home/tls13/tls13/repos/git.net.in.tum.de/scan-meta

MASSDNS=/home/tls13/tls13/repos/github.com/quirins/massdns/bin/massdns
FOLLOWCNAMES=/home/tls13/tls13/repos/github.com/tumi8/net-utils/followcnames.go
GREPCIDR=/home/tls13/tls13/repos/github.com/frohoff/grepcidr/grepcidr 

# prepare output dir
mkdir -p $OUTPUT_DIR/$EPOCH
rm $OUTPUT_DIR/latest
ln -s $OUTPUT_DIR/$EPOCH $OUTPUT_DIR/latest

# run massdns
/bin/cat $INFILE | $MASSDNS -p -s $HASHMAPSIZE -a -c $RETRIES -o -r $RESOLVERS -t $TYPE -i $INTERVAL --finalstats - 2> >(tee $OUTBASE.massdns.log >&2) > $OUTBASE.massdns

# Filter out relevant RRs
cat $OUTBASE.massdns | awk '($4 == "A" || $4 == "CNAME") {print}' > $OUTBASE.massdns.onlyrr

# Follow CNAMEs
gzip $INFILE
timeout 3h nice -n20 go run $FOLLOWCNAMES $INFILE.gz $OUTBASE.massdns.onlyrr | sort -u -T /srv/tls13/ | sort -t, -k1b,1 -T /srv/tls13/ > ${OUTBASE}.massdns.onlyrr.ipdomain

$GREPCIDR -f ${BLACKLIST_DIR}/release/ipv4-bl-merged.txt -i ${OUTBASE}.massdns.onlyrr.ipdomain > ${OUTBASE}.massdns.onlyrr.ipdomain.wlip

grep -f ${BLACKLIST_DIR}/release/domain-blacklist.txt -v ${OUTBASE}.massdns.onlyrr.ipdomain.wlip > ${OUTBASE}.massdns.onlyrr.ipdomain.wlip.wldomains

# Some insane DNS operators put a \ into an A record - hence the extra grep
cut -f 1 -d, ${OUTBASE}.massdns.onlyrr.ipdomain.wlip.wldomains | sed 's/$/\/32/g' | grep -v '\\' | sort -u | shuf > ${OUTBASE}.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf

mv $INFILE.gz $OUTPUT_DIR/$EPOCH
