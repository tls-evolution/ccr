#!/bin/bash

export LC_ALL=C

if [[ $# == 0 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage $0 MONTHS"
    exit
fi

for MONTH in $@; do
MAPPING_DIR=/srv/tls13/experiment/analysis/deployment/per_zone_group/bin
SCHEMA=`grep $MONTH $MAPPING_DIR/db_month_schema_mapping.csv | cut -f 2 -d,`
if [[ $MONTH == "2019-05" ]] || [[ $MONTH == "2019-06" ]] || [[ $MONTH == "2019-07" ]]; then
IPRANGES_FILE=/srv/tls13/experiment/analysis/hosting/data/ipranges/1557491412_results/1557491412.all.ipv4.ranges
else
IPRANGES_FILE=/srv/tls13/experiment/analysis/hosting/data/ipranges/1564627018_results/1564627018.all.ipv4.ranges
fi
cut -f 1,3 -d, $IPRANGES_FILE > /tmp/ipranges.csv
psql -U tls13 tls13 << EOF
DELETE FROM $SCHEMA.ipranges_v4; 
\copy $SCHEMA.ipranges_v4 FROM '/tmp/ipranges.csv' WITH CSV
EOF
rm /tmp/ipranges.csv
done
