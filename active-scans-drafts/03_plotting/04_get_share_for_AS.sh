#!/bin/bash
for AS in $(ls data_AS/ | grep "^_");
do
	echo $AS
	for f in $(ls data_AS/$AS | sort);
		do echo -n "$f: "
		TLSANY=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLS"))) | map(.value) | add' data_AS/${AS}/${f})
		TLS13=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLSv1.3"))) | map(.value) | add' data_AS/${AS}/${f})
		ALL=$(jq '.full_or_sh_latest | to_entries | map(select(.key | match("TLSv1.3"))) | map(.value) | add' data/_all/${f})
		echo -n "TLSany: ${TLSANY} TLS13: ${TLS13}, ALL: ${ALL} --> " && echo "scale=4; ${TLS13} / ${ALL}" | bc;
	done;
	echo ""
done;

