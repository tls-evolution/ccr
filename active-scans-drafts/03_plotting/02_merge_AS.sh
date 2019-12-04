#!/bin/bash

ASLIST='AMAZON GOOGLE CLOUDFLARE AKAMAI MICROSOFT FACEBOOK DIGITALOCEAN OVH GODADDY SQUARESPACE SINGLEHOP'

AMAZON='7224 8987 10124 14618 16509 17493 38895 58588 62785 135630 395343'
GOOGLE='6432 15169 16550 16591 19448 19527 22577 22859 24424 26684 26910 36039 36040 36384 36385 36492 40873 41264 45566 139070 139190 394507 394639 394699 395973 396982 36987'
CLOUDFLARE='13335 14789 132892 133877 139242 202623 203898 209242 394536 395747'
AKAMAI='12222 16625 16702 17334 18680 18717 20189 20940 21342 21357 21399 22207 23454 23455 23903 24319 30675 31107 31108 31109 31110 31377 32787 33905 34164 34850 35204 35993 35994 36183 39836 43639 45700 55409 55770 393234 39356'
MICROSOFT='3598 5761 6182 6194 6291 6584 8068 8069 8070 8071 8072 8073 8074 8075 12076 13399 13811 14719 17345 20046 22692 23468 25796 26222 30135 30575 31792 32476 35106 36006 40066 45139 58862 59067 63314 395496 395524 395851 396463 397466'
FACEBOOK='32934 54115 63293'
DIGITALOCEAN='14061 39690 62567 133165 135340 200130 201229 202018 202109 205301 393406 394362'
OVH='16276 35540'
GODADDY='20773 21499 26496 44273 397513 397514 397515 397516 397517 397518 397519 397520 397521 397522'
SQUARESPACE='53831'
SINGLEHOP='32475 47080'

# Selectively preprocess important AS groups
pushd ../02_postprocessing/05_tls13version_ASenrich-finalize
for AS in $AMAZON; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $GOOGLE; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $CLOUDFLARE; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $AKAMAI; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $MICROSOFT; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $FACEBOOK; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $DIGITALOCEAN; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $OVH; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $GODADDY; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $SQUARESPACE; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
for AS in $SINGLEHOP; do set -e && for d in $(ls -d ../04_tls13version_ASenrich-aggregate2/tls-version-grabber-all*/as_${AS}); do echo "--- START $d $(date)" && python3 tls13version_ASenrich-finalize_run.py --basedir $d; echo -e "--- DONE $d $(date)\n\n"; done; done;
popd

# Copy the aggregated data
for AS in $AMAZON; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $GOOGLE; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $CLOUDFLARE; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $AKAMAI; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $MICROSOFT; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $FACEBOOK; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $DIGITALOCEAN; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $OVH; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $GODADDY; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $SQUARESPACE; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;
for AS in $SINGLEHOP; do mkdir -p data_AS/as_${AS}; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all/as_${AS}/* data_AS/as_${AS}/; cp ../02_postprocessing/05_tls13version_ASenrich-finalize/tls-version-grabber-all-recent/as_${AS}/* data_AS/as_${AS}/; done;

# Merge results of different AS numbers into one
python3 merge.py --prefix=data_AS/ --out _AMAZON $(for AS in $AMAZON; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _GOOGLE $(for AS in $GOOGLE; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _CLOUDFLARE $(for AS in $CLOUDFLARE; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _AKAMAI $(for AS in $AKAMAI; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _MICROSOFT $(for AS in $MICROSOFT; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _FACEBOOK $(for AS in $FACEBOOK; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _DIGITALOCEAN $(for AS in $DIGITALOCEAN; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _OVH $(for AS in $OVH; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _GODADDY $(for AS in $GODADDY; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _SQUARESPACE $(for AS in $SQUARESPACE; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _SINGLEHOP $(for AS in $SINGLEHOP; do echo -n " --in as_${AS}"; done; echo "")

