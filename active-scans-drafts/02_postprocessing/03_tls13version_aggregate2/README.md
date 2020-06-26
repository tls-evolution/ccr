# README aggreagate step 2

The first aggregation step aggregated information for each domain. Step 2 aggregates the information zone, yielding the number of domains that used a specific version of a draft and further meta-information such as the total number of domains, for later calculations. The processing works similar as for the first aggregation step:

```bash
# run all lists one after another in one go (this will take a very long time)
python3 tls13version_aggregate2_run.py --basedir ${LOGS_TOPLEVEL_DIRECTORY}

# preprocess lists of a specific zone
python3 tls13version_aggregate2_run.py --basedir ${ZONE_DIRECTORY}
```


## Option 1: Split along first letter, but preprocess large lists

As before, we first processed large zones, before finalizing the aggregation by including all other lists

### Large lists (alexa, com, net, org, de, se, toplistsAlexaUmbrellaMajestic-A-www, toplistsAlexaUmbrellaMajestic-A-www_domainsNotInZoneLists)

```bash
for LIST in alexa-A-www com-A-www net-A-www org-A-www de-A-www se-A-www toplistsAlexaUmbrellaMajestic-A-www toplistsAlexaUmbrellaMajestic-A-www_domainsNotInZoneLists; do SCREEN_NAME=agg2_${LIST}_all && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LIST=${LIST} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LIST}); do echo "--- START \$d" && python3 tls13version_aggregate2_run.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done;
```

```bash
for LIST in alexa-A-www com-A-www net-A-www org-A-www de-A-www se-A-www toplistsAlexaUmbrellaMajestic-A-www toplistsAlexaUmbrellaMajestic-A-www_domainsNotInZoneLists; do screen -x agg2_${LIST}_all; done;
```

### All other

```bash
for LETTER in {a..z}; do SCREEN_NAME=agg2_${LETTER}_all && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LETTER=${LETTER} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LETTER}* | grep -v -e alexa-A-www -e com-A-www -e net-A-www -e org-A-www -e de-A-www -e se-A-www); do echo "--- START \$d" && python3 tls13version_aggregate2_run.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done;
```

```bash
for LETTER in {a..z}; do screen -x agg2_${LETTER}_all; done;
```


## Option 2: Split along first letter (w/o special handling of large lists)

```bash
for LETTER in {a..z}; do SCREEN_NAME=agg2_${LETTER}_all && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LETTER=${LETTER} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LETTER}*); do echo "--- START \$d" && python3 tls13version_aggregate2_run.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done;
```

```bash
for LETTER in {a..z}; do screen -x agg2_${LETTER}_all; done;
```

