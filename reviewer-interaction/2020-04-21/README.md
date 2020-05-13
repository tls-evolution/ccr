# Inspection of an interesting case

Scan: 2019-11

`export FILE=1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.csv`

This file is the result of taking the zonefiles from CZDS, minus .net, extracting the domain names, sort -u, then running massdns, extracting the RR for A, bringing into ip-domain format, applying our IP and domain blacklists, adding the /32 prefix, short -u, shuf, running through zmap, taking the IPs and joining back on the input file to get the domain names back, running the TLS 1.3 goscanner, taking only the hosts with failed handshakes, and mapping to ASN with pyasn of the same epoch (timestamp at beginning of filename). It's a mouthful.

(Note: we tested a simple random sample of these domains with the latest OpenSSL as well. All handshakes failed as well. Tests with curl on the same sample show that we get HTTP on the HTTPS port.If we force HTTS, we get an "sslv3 alert handshake" for all domains in the sample.)

A single ASN is responsible for most IPs and also domains:

`gunzip -k $FILE.gz`

    LC_ALL=C cat 1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.csv | cut -f 2,4 -d, | sort -u -k1b,1 -t, | cut -f 2 -d, | sort | uniq -c | sort -rn | head -n 4

    839726 13335
    10969 26496
    6023 48287
    1498 16509

ASN 13335 is Cloudflare.

We used IP ranges that Cloudflare reported as theirs (as on ) as of 1 Aug 04:36:58 GMT.

    cat cloudflare_ranges_ipv4_1572573861.txt

    173.245.48.0/20
    103.21.244.0/22
    103.22.200.0/22
    103.31.4.0/22
    141.101.64.0/18
    108.162.192.0/18
    190.93.240.0/20
    188.114.96.0/20
    197.234.240.0/22
    198.41.128.0/17
    162.158.0.0/15
    104.16.0.0/12
    172.64.0.0/13
    131.0.72.0/22

We apply grepcidr on these:

`grepcidr -x -f cloudflare_ranges_ipv4_1572573861.txt $FILE > 1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.cloudflare.csv`

    wc -l 1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.cloudflare.csv
    841242

Looking inside:

    shuf 1572573861_czdsnonet.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined.goscanner.hosts.handshakefailure.asn.cloudflare.csv | head -n 10
    104.24.105.128,dspwn.club,remote error: tls: handshake failure,13335
    104.28.162.8,oqoye.icu,remote error: tls: handshake failure,13335
    104.31.199.102,ytmewt.icu,remote error: tls: handshake failure,13335
    104.28.219.157,gcyuu.icu,remote error: tls: handshake failure,13335
    104.24.28.238,spezv.icu,remote error: tls: handshake failure,13335
    104.18.29.173,tcytkf.live,remote error: tls: handshake failure,13335
    104.28.238.240,xlrywt.live,remote error: tls: handshake failure,13335
    104.28.137.66,lngbh.icu,remote error: tls: handshake failure,13335
    104.28.158.141,mwfmu.icu,remote error: tls: handshake failure,13335
    104.31.215.170,puwqds.icu,remote error: tls: handshake failure,13335

The format of these domain names is interesting: always six random alphabetic characters under the TLD suffices .icu and .live, mostly.

One check we did not do for the paper: check the NS of the domain. Sadly, we only looked up the NS for domains with successful TLS 1.3 handshakes. We pulled this data from OpenINTEL, but note that their vantage point is in the Netherlands. However, the NS is the same as when resolving the NS record for `oqoye.icu` and `tcytkf.live` from Australia, on 2020-04-21: ns1.ecpage.com. and ns2.ecpage.com.

When we took a sample of domains in `.icu` and `.live` and tested plain HTTP on the HTTPS port, this showed an HTTP error by Cloudflare (as it should). Testing this again on 2020-04-21, but with HTTPS, we get the SSLv3 handshake error.
