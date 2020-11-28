#!/bin/bash
for list in $(ls -d data/_* data/alexa*);
do
	echo $list
	for f in $(ls $list | sort);
		do echo -n "$f: "
		DOMAINS_LIST=$(jq '.all' ${list}/${f})
		REFUSED443_LIST=$(jq '."443_refused"' ${list}/${f})
		DOMAINS_443OPEN_LIST=$(echo "${DOMAINS_LIST} - ${REFUSED443_LIST}" | bc)
		TLSANY_LIST=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLS"))) | map(.value) | add' ${list}/${f})
		TLS13_LIST=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLSv1.3"))) | map(.value) | add' ${list}/${f})
		PERCENT_TLSANY_OF_DOMAINS_LIST=$(echo "scale=4; ${TLSANY_LIST} / ${DOMAINS_LIST} * 100" | bc)
		PERCENT_DOMAINS443OPEN_OF_DOMAINS_LIST=$(echo "scale=4; ${DOMAINS_443OPEN_LIST} / ${DOMAINS_LIST} * 100" | bc)
		PERCENT_TLS13_OF_DOMAINS_LIST=$(echo "scale=4; ${TLS13_LIST} / ${DOMAINS_LIST} * 100" | bc)
		PERCENT_TLS13_OF_443OPEN_LIST=$(echo "scale=4; ${TLS13_LIST} / ${DOMAINS_443OPEN_LIST} * 100" | bc)
		PERCENT_TLS13_OF_TLSANY_LIST=$(echo "scale=4; ${TLS13_LIST} / ${TLSANY_LIST} * 100" | bc)
		echo -e "${list}  Domains: ${DOMAINS_LIST} 443open: ${DOMAINS_443OPEN_LIST} (${PERCENT_DOMAINS443OPEN_OF_DOMAINS_LIST}%) TLSany: ${TLSANY_LIST} (${PERCENT_TLSANY_OF_DOMAINS_LIST}%) TLS13: ${TLS13_LIST} (${PERCENT_TLS13_OF_DOMAINS_LIST}% / ${PERCENT_TLS13_OF_443OPEN_LIST}% / ${PERCENT_TLS13_OF_TLSANY_LIST}%)";
	done;
	echo ""
done;

