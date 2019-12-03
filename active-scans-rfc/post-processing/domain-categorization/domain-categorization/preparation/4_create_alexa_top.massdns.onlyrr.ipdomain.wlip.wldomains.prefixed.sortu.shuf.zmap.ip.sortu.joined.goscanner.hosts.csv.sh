# Input file is e.g. 1572573861_alexa.domain.sortu+2ld.withranks.csv
# Call by indicating the epoch and number of domains to sample.
export LC_ALL=C

EPOCH=$1
SAMPLE_SIZE=$2
INFILE=/home/tls13/tls13/experiment/inputs/$EPOCH/${EPOCH}_alexa.domain.sortu+2ld.withranks.csv
# Note that the below output file is named such that the vt-request.py script can determine all parameters itself from the filename
sort -t , -k1,1 -n $INFILE | head -n $SAMPLE_SIZE > /home/tls13/tls13/experiment/inputs/$EPOCH/${EPOCH}_alexa.domain.sortu+2ld.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.top.${SAMPLE_SIZE}.csv
