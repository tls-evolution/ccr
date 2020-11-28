# README aggregation step 1

The first aggregation step aggregates the information per domain such that we only use a single results for each domain per month, even though each domain might have been scanned multiple times per month. The processing works as for the first step.

## Commands to run the eval

Running this can take quite a while. It is a good idea to first process larger lists separately before following up with all other smaller zones.
```bash
# run all lists one after another in one go (this will take forever)
python3 tls13version_aggregate1_run.py --basedir ${LOGS_TOPLEVEL_DIRECTORY}

# preprocess lists of a specific zone
python3 tls13version_aggregate1_run.py --basedir ${ZONE_DIRECTORY}
```

In reality, we split up the processing into a phase where first processing the large lists and then following up with every list that is left. Furthermore, we parallelized the workload using multiple screen sessions.

### Large lists (alexa, com, net, org, de, se, nu, majestic, toplistsAlexaUmbrellaMajestic)

Setting up screen sessions (example for com-A-www)
```bash
LIST=com-A-www && for YEAR in {2017..2019}; do for MONTH in {01..12}; do SCREEN_NAME=agg1_${LIST}_${YEAR}-${MONTH} && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'MONTH=${MONTH} && YEAR=${YEAR} && LIST=${LIST} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../01_tls13version_logfilter/tls-version-grabber-all*/\${LIST}/\${YEAR}/\${MONTH}); do echo "--- START \$d" && python3 tls13version_aggregate1_run.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done; done;
```

Connect to the screen sessions to start and overlook the processing
```bash
LIST=com-A-www && for YEAR in {2017..2019}; do for MONTH in {01..12}; do screen -x agg1_${LIST}_${YEAR}-${MONTH}; done; done;
```

### All other (run after large, otherwise large are included)

Set up screen sessions that will preprocess any left logs; split according to first letter.
WARNING: This must not be started before the workers with specific lists finished. Otherwise the processes will interfere with each other!
```bash
for LETTER in {a..z}; do SCREEN_NAME=agg1_${LETTER}_all && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LETTER=${LETTER} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../01_tls13version_logfilter/tls-version-grabber-all*/\${LETTER}*/*/* | grep -v "/2019/11"); do echo "--- START \$d" && python3 tls13version_aggregate1_run.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done;
```

Connect to the screen sessions to start and overlook the processing
```bash
for LETTER in {a..z}; do screen -x agg1_${LETTER}_all; done;
```

