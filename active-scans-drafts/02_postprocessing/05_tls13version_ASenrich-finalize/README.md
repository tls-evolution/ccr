# README AS finalizing

This step uses the results of the AS-enriching aggregate2 step and aggregates all information per AS, i.e., it yields the results with the amount of domains per AS that support a specific TLS 1.3 draft version.

# Commands to run the eval

for LASTDIGIT in {0..9}; do for SECONDLASTDIGIT in 0-4 5-9; do SCREEN_NAME=ASenrich-final_${LASTDIGIT}_${SECONDLASTDIGIT} && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LASTDIGIT=${LASTDIGIT} && SECONDLASTDIGIT=${SECONDLASTDIGIT} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_*[\${SECONDLASTDIGIT}]\${LASTDIGIT}); do echo "--- START \$d \$(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir \$d; echo -e "--- DONE \$d \$(date)\\n\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done; done;

for LASTDIGIT in {0..9}; do for SECONDLASTDIGIT in 0-4 5-9; do SCREEN_NAME=ASenrich-final_${LASTDIGIT}_${SECONDLASTDIGIT} && screen -x $SCREEN_NAME; done; done;

# reverse from behind to speed up
for LASTDIGIT in {0..9}; do for SECONDLASTDIGIT in 0-4 5-9; do SCREEN_NAME=ASenrich-final-reverse_${LASTDIGIT}_${SECONDLASTDIGIT} && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LASTDIGIT=${LASTDIGIT} && SECONDLASTDIGIT=${SECONDLASTDIGIT} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_*[\${SECONDLASTDIGIT}]\${LASTDIGIT} | tac); do echo "--- START \$d \$(date)" && python3 tls13version_ASenrich-finalize_run-reverse.py --basedir \$d; echo -e "--- DONE \$d \$(date)\\n\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done; done;

for LASTDIGIT in {0..9}; do for SECONDLASTDIGIT in 0-4 5-9; do SCREEN_NAME=ASenrich-final-reverse_${LASTDIGIT}_${SECONDLASTDIGIT} && screen -x $SCREEN_NAME; done; done;

# Process for important AS groups

See zone_merge_as_run.py for AS number lists

```
for AS in $AMAZON; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
```

