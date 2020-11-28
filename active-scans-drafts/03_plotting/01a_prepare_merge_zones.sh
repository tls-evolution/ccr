#!/bin/bash

# For those month were two scanner versions run in parallel, prioritize the results of the most recent scanner
for LIST in $(ls ../02_postprocessing/03_tls13version_aggregate2/tls-version-grabber-all/); do mkdir -p data/${LIST}; cp ../02_postprocessing/03_tls13version_aggregate2/tls-version-grabber-all/${LIST}/* data/${LIST}/; done;
for LIST in $(ls ../02_postprocessing/03_tls13version_aggregate2/tls-version-grabber-all-recent/); do mkdir -p data/${LIST}; cp ../02_postprocessing/03_tls13version_aggregate2/tls-version-grabber-all-recent/${LIST}/* data/${LIST}/; done;
