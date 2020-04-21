= Inspection of an interesting case ==

Scan: 2019-11

`export FILE=1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.csv`

This file is the result of taking the zonefiles from CZDS, minus .net, extracting the domain names, sort -u, then running massdns, extracting the RR for A, bringing into ip-domain format, applying our IP and domain blacklists, adding the /32 prefix, short -u, shuf, running through zmap, taking the IPs and joining back on the input file to get the domain names back, running the TLS 1.3 goscanner, taking only the hosts with failed handshakes, and mapping to ASN with pyasn of the same epoch (timestamp at beginning of filename). It's a mouthful.

A single ASN is responsible for most IPs and also domains:

`gunzip -k $FILE.gz`

    LC_ALL=C cat 1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.csv | cut -f 2,4 -d, | sort -u -k1b,1 -t, | cut -f 2 -d, | sort | uniq -c | sort -rn | head -n 4

    839726 13335
    10969 26496
    6023 48287
    1498 16509
