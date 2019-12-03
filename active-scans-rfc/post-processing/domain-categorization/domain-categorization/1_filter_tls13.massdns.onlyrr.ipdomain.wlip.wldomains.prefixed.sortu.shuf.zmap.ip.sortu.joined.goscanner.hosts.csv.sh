# Input file is e.g. 1556701596_cno.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.csv
# Call by indicating the epoch, scan type, and number of domains to sample.
# Scan type may be alexa, cno, czdsnonet, cf, ua, dk, de, jp, cn, eu
export LC_ALL=C
if [ "$2" != "cno" ] && [ "$2" != "czdsnonet" ] &&  [ "$2" != "com" ] &&  [ "$2" != "net" ] &&  [ "$2" != "org" ]; then
    SORT=sortu+2ld
else
    SORT=sortu
fi
INFILE=/home/tls13/tls13/experiment/outputs/$1/$1_$2.domain.$SORT.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.csv
BASEFILE=`basename $INFILE`
BASEDIR=`dirname $INFILE`
OUTFILEPREFIX=$1_$2.domain.$SORT.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.tls13
awk -F, '$8 == "TLSv1.3" {print $4}' $INFILE | shuf | head -n $3 > $BASEDIR/$OUTFILEPREFIX.$3.csv
