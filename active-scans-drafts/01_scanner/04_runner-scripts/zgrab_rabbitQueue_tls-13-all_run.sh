#!/bin/bash

# TODO: Update the Useragent: You MUST change the URL! It MUST provide information that enables scan-targets to contact YOU to request blacklisting.
USERAGENT="Mozilla/5.0 zgrab/0.x (compatible; Researchscan/t13l; +http://scan-info-url.de; Community Version for Reproducibility"
ZGRAB=./../zgrab-binaries/zgrab_rabbitQueue_tls-13-all_since-2017-10-16

# Blacklisting already done by infrastructure, no additional downstream blacklist recognition in this scanner version
# BLACKLIST_IP=./blacklist-ip_example.txt
# BLACKLIST_DOM=./blacklist-dom_example.txt

# ulimit -n 900000
# cat example_in.txt | HOME="/" jq -R -c 'fromjson? | select(type == "object")' | HOME="/" jq --unbuffered -c -r 'if .status == "NOERROR" then . as $full | ."comsys-source" as $cs | ."comsys-date" as $cd | .altered_name as $an | [.data.answers[] | select(.type=="A")][0] | if (.answer != null) then [.answer, $an, $cs, $cd, ($full | tostring | [.] | @csv)] | join(",") else empty end else empty end' | ${ZGRAB} -http-user-agent "${USERAGENT}" --tls --http-max-redirects 20 -http-method GET -http-max-size 0 -port 443 --http="/" -tls-version=TLSv1.3 > example_out.json

# Instead of the full input format in example_in.txt used above, we can use a minimal input format which is easier to set up:
cat example_in_minimal.txt | ${ZGRAB} -http-user-agent "${USERAGENT}" --tls --http-max-redirects 20 -http-method GET -http-max-size 0 -port 443 --http="/" -tls-version=TLSv1.3 > example_out.json

