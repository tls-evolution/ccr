#!/bin/bash

USERAGENT="Mozilla/5.0 zgrab/0.x (compatible; Researchscan/t13l; +http://researchscan.comsys.rwth-aachen.de)"
ZGRAB=./../zgrab-binaries/zgrab_rabbitQueue_tls-13-all_since-2017-10-16

# Blacklisting already done by infrastructure, no additional downstream blacklist recognition in this scanner version
# BLACKLIST_IP=./blacklist-ip_example.txt
# BLACKLIST_DOM=./blacklist-dom_example.txt

# ulimit -n 900000
cat example_in.txt | ${ZGRAB} -http-user-agent "${USERAGENT}" --tls --http-max-redirects 20 -http-method GET -http-max-size 0 -port 443 --http="/" -tls-version=TLSv1.3 > example_out.json

