# README AS finalizing

This step uses the results of the AS-enriching aggregate2 step and aggregates all information per AS, i.e., it yields the results with the amount of domains per AS that support a specific TLS 1.3 draft version.

# Commands to run the eval

**This will take a while. If you are impatient, selectively process the AS numbers that belong to important ASes (see below)**

```bash
for LASTDIGIT in {0..9}; do for SECONDLASTDIGIT in 0-4 5-9; do SCREEN_NAME=ASenrich-final_${LASTDIGIT}_${SECONDLASTDIGIT} && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LASTDIGIT=${LASTDIGIT} && SECONDLASTDIGIT=${SECONDLASTDIGIT} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_*[\${SECONDLASTDIGIT}]\${LASTDIGIT}); do echo "--- START \$d \$(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir \$d; echo -e "--- DONE \$d \$(date)\\n\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done; done;
```

```bash
for LASTDIGIT in {0..9}; do for SECONDLASTDIGIT in 0-4 5-9; do SCREEN_NAME=ASenrich-final_${LASTDIGIT}_${SECONDLASTDIGIT} && screen -x $SCREEN_NAME; done; done;
```


# Process for important AS groups

**This action is also performed by `../../03_plotting/02a_prepare_merge_AS.sh` thus you can skip the step here**

See `../../03_plotting/config_AS.sh` for AS number lists

```bash
for AS in $AMAZON; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
```


## Commands with AS numbers integrated:

```bash
screen -S ASenrich-final_AMAZON
for AS in 7224 8987 10124 14618 16509 17493 38895 58588 62785 135630 395343; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_GOOGLE
for AS in 6432 15169 16550 16591 19448 19527 22577 22859 24424 26684 26910 36039 36040 36384 36385 36492 40873 41264 45566 139070 139190 394507 394639 394699 395973 396982 36987; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_CLOUDFLARE
for AS in 13335 14789 132892 133877 139242 202623 203898 209242 394536 395747; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_AKAMAI
for AS in 12222 16625 16702 17334 18680 18717 20189 20940 21342 21357 21399 22207 23454 23455 23903 24319 30675 31107 31108 31109 31110 31377 32787 33905 34164 34850 35204 35993 35994 36183 39836 43639 45700 55409 55770 393234 39356; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_MICROSOFT
for AS in 3598 5761 6182 6194 6291 6584 8068 8069 8070 8071 8072 8073 8074 8075 12076 13399 13811 14719 17345 20046 22692 23468 25796 26222 30135 30575 31792 32476 35106 36006 40066 45139 58862 59067 63314 395496 395524 395851 396463 397466; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_FACEBOOK
for AS in 32934 54115 63293; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_DIGITALOCEAN
for AS in 14061 39690 62567 133165 135340 200130 201229 202018 202109 205301 393406 394362; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_OVH
for AS in 16276 35540; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_GODADDY
for AS in 20773 21499 26496 44273 397513 397514 397515 397516 397517 397518 397519 397520 397521 397522; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_SQUARESPACE
for AS in 53831; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;

screen -S ASenrich-final_SINGLEHOP
for AS in 32475 47080; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
```


```bash
for AS in AMAZON GOOGLE CLOUDFLARE AKAMAI MICROSOFT FACEBOOK DIGITALOCEAN OVH GODADDY SQUARESPACE SINGLEHOP; do SCREEN_NAME=ASenrich-final_${AS} && screen -x $SCREEN_NAME; done;
```
