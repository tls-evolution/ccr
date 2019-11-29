#!/bin/bash

export LC_ALL=C

if [[ $# == 0 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage $0 MONTHS"
    exit
fi

for MONTH in $@; do
MAPPING_DIR=/srv/tls13/experiment/analysis/deployment/per_zone_group/bin
SCHEMA=`grep $MONTH $MAPPING_DIR/db_month_schema_mapping.csv | cut -f 2 -d,`
psql -U tls13 tls13 << EOF
DROP INDEX $SCHEMA.ipranges_v4_range;
CREATE INDEX ipranges_v4_range ON $SCHEMA.ipranges_v4 USING gist (range)
EOF
done
