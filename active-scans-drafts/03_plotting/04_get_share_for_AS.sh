#!/bin/bash
for AS in $(ls data_AS/ | grep "^_");
do
	echo $AS
	for f in $(ls data_AS/$AS | sort);
		do echo -n "$f: "
		DOMAINS_AS=$(jq '.all' data_AS/${AS}/${f})
		REFUSED443_AS=$(jq '."443_refused"' data_AS/${AS}/${f})
		DOMAINS_443OPEN_AS=$(echo "${DOMAINS_AS} - ${REFUSED443_AS}" | bc)
		TLSANY_AS=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLS"))) | map(.value) | add' data_AS/${AS}/${f})
		TLS13_AS=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLSv1.3"))) | map(.value) | add' data_AS/${AS}/${f})
		PERCENT_TLSANY_OF_DOMAINS_AS=$(echo "scale=4; ${TLSANY_AS} / ${DOMAINS_AS} * 100" | bc)
		PERCENT_DOMAINS443OPEN_OF_DOMAINS_AS=$(echo "scale=4; ${DOMAINS_443OPEN_AS} / ${DOMAINS_AS} * 100" | bc)
		PERCENT_TLS13_OF_DOMAINS_AS=$(echo "scale=4; ${TLS13_AS} / ${DOMAINS_AS} * 100" | bc)
		PERCENT_TLS13_OF_443OPEN_AS=$(echo "scale=4; ${TLS13_AS} / ${DOMAINS_443OPEN_AS} * 100" | bc)
		PERCENT_TLS13_OF_TLSANY_AS=$(echo "scale=4; ${TLS13_AS} / ${TLSANY_AS} * 100" | bc)
		DOMAINS_ALLZONES=$(jq '.all' data/_all/${f})
		REFUSED443_ALLZONES=$(jq '."443_refused"' data/_all/${f})
		DOMAINS_443OPEN_ALLZONES=$(echo "${DOMAINS_ALLZONES} - ${REFUSED443_ALLZONES}" | bc)
		TLSANY_ALLZONES=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLS"))) | map(.value) | add' data/_all/${f})
		TLS13_ALLZONES=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLSv1.3"))) | map(.value) | add' data/_all/${f})
		PERCENT_OF_TLS13_ALLZONES=$(echo "scale=4; ${TLS13_AS} / ${TLS13_ALLZONES} * 100" | bc)
		echo -e "$AS  Domains: ${DOMAINS_AS} 443open: ${DOMAINS_443OPEN_AS} (${PERCENT_DOMAINS443OPEN_OF_DOMAINS_AS}%) TLSany: ${TLSANY_AS} (${PERCENT_TLSANY_OF_DOMAINS_AS}%) TLS13: ${TLS13_AS} (${PERCENT_TLS13_OF_DOMAINS_AS}% / ${PERCENT_TLS13_OF_443OPEN_AS}% / ${PERCENT_TLS13_OF_TLSANY_AS}%),   \tAll_Zones  Domains: ${DOMAINS_ALLZONES} TLSany: ${TLSANY_ALLZONES} TLS13: ${TLS13_ALLZONES}) --> $AS hosts ${PERCENT_OF_TLS13_ALLZONES}% of all TLS 1.3 domains (in any zone)";
	done;
	echo ""
done;

