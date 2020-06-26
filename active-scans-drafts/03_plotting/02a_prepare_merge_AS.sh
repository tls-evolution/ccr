#!/bin/bash

source ./config_AS.sh

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

