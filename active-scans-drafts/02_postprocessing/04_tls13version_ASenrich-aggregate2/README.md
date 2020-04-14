# README AS enrich-aggregate2

The scripts in this directory add AS information to the domain-aggregated results of the first aggregation step

## Large lists (alexa, com, net, org, de, se, ru, nu)

```bash
for LIST in com-A-www; do for YEAR in {2017..2019}; do for MONTH in {01..12}; do SCREEN_NAME=asenrich_${LIST}_helper_${YEAR}_${MONTH} && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LIST=${LIST} && YEAR=${YEAR} && MONTH=${MONTH} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LIST}/\${YEAR}/\${MONTH}*); do echo "--- START \$d" && python3 tls13version_ASenrich-aggregate2.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done; done; done;
```
```bash
for LIST in com-A-www; do for YEAR in {2017..2019}; do for MONTH in {01..12}; do screen -x asenrich_${LIST}_helper_${YEAR}_${MONTH}; done; done; done;
```

```bash
for LIST in com-A-www; do for YEAR in {2017..2019}; do SCREEN_NAME=asenrich_${LIST}_${YEAR} && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LIST=${LIST} && YEAR=${YEAR} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LIST}/\${YEAR}); do echo "--- START \$d" && python3 tls13version_ASenrich-aggregate2.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done; done;
```
```bash
for LIST in com-A-www; do for YEAR in {2017..2019}; do screen -x asenrich_${LIST}_${YEAR}; done; done;
```

```bash
for LIST in alexa-A-www net-A-www org-A-www de-A-www se-A-www ru-A-www nu-A-www; do SCREEN_NAME=asenrich_${LIST}_all && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LIST=${LIST} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LIST}); do echo "--- START \$d" && python3 tls13version_ASenrich-aggregate2.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done;
```
```bash
for LIST in alexa-A-www net-A-www org-A-www de-A-www se-A-www ru-A-www nu-A-www; do screen -x asenrich_${LIST}_all; done;
```

## All other

```bash
for LETTER in {a..z}; do SCREEN_NAME=asenrich_${LETTER}_all && screen -S $SCREEN_NAME && screen -S $SCREEN_NAME -X stuff "bash -c 'LETTER=${LETTER} && set -e && " && screen -S $SCREEN_NAME -X stuff 'for d in \$(ls -d ../02_tls13version_aggregate1/tls-version-grabber-all*/\${LETTER}* | grep -v -e alexa-A-www -e com-A-www -e net-A-www -e org-A-www -e de-A-www -e se-A-www -e ru-A-www -e nu-A-www); do echo "--- START \$d" && python3 tls13version_ASenrich-aggregate2.py --basedir \$d; echo -e "--- DONE \$dn\\n"; done;' && screen -S $SCREEN_NAME -X stuff "'"; done;
```

```bash
for LETTER in {a..z}; do screen -x asenrich_${LETTER}_all; done;
```

