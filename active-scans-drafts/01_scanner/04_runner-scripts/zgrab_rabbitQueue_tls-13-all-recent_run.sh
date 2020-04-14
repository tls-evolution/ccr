#!/bin/bash

USERAGENT="Mozilla/5.0 zgrab/0.x (compatible; Researchscan/t13rl; +http://researchscan.comsys.rwth-aachen.de)"
ZGRAB=./../zgrab-binaries/zgrab_rabbitQueue_tls-13-all-recent_since-2019-06-14

# Blacklisting done by infrastructure already, additional recognition implemented in scanner
BLACKLIST_IP=blacklist-ip_example.txt
BLACKLIST_DOM=blacklist-dom_example.txt

# ulimit -n 900000
cat example_in.txt | ${ZGRAB} -http-user-agent "${USERAGENT}" --tls --http-max-redirects 20 -http-method GET -http-max-size 0 -port 443 --http="/" -tls-version=TLSv1.3 --blacklist-ip=${BLACKLIST_IP} --blacklist-dom=${BLACKLIST_DOM} -senders 3000 > example_out.json

