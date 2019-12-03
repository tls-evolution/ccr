#!/bin/bash
export LC_ALL=C

USER=tls13
DB=tls13

# host file, e.g.
# /srv/tls13/experiment/outputs/1556701596/1556701596_alexa.domain.sortu+2ld.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.csv
HOST_FILE=$1
SCHEMA=$2

for SCHEMA in may_2019 jun_2019 jul_2019 aug_2019; do
    for ZONE in alexa czds cno cctld; do
        if [ "$ZONE" != "cno" ] && [ "$ZONE" != "czds" ] &&  [ "$ZONE" != "com" ] &&  [ "$ZONE" != "net" ] &&  [ "$ZONE" != "org" ]; then
            SORT=sortu+2ld
        else
            SORT=sortu
        fi
        if [[ "$ZONE" == "czds" ]]; then
            REALZONE=czdsnonet
        else
            REALZONE=$ZONE
        fi
        EPOCH=`grep "$ZONE,$SCHEMA" import_mappings.csv | cut -f 3 -d,`
        INFILE=/home/tls13/tls13/experiment/outputs/$EPOCH/${EPOCH}_${REALZONE}.domain.$SORT.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.csv
        #echo "psql -U $USER $DB \copy ${SCHEMA}_${ZONE}.hosts FROM '$INFILE' WITH CSV HEADER DELIMITER ','"
        #ls $INFILE
#        psql -U $USER $DB << EOF
#            \copy $SCHEMA_{$ZONE}.hosts FROM '$1' WITH CSV HEADER DELIMITER ','
#EOF
    done
done
