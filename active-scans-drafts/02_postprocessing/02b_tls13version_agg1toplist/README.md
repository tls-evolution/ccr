# README

We want to build a list with all entries of the toplists to later compile a list of scans for domains that have been scanned as part of the toplists but do not appear in the zone scans.

Can run in parallel:
```bash
python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all/alexa-A-www/
python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all-recent/alexa-A-www/

python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all/umbrella-A-www/
python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all-recent/umbrella-A-www/

python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all/majestic-A-www/
python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all-recent/majestic-A-www/

python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all/toplistsAlexaUmbrellaMajestic-A-www/
python3 tls13version_agg1toplist.py --basedir ../02_tls13version_aggregate1/tls-version-grabber-all-recent/toplistsAlexaUmbrellaMajestic-A-www/
```

Copy relevant results:
```
mv tls-version-grabber-all/toplistsAlexaUmbrellaMajestic-A-www_domainsNotInZoneLists ../02_tls13version_aggregate1/tls-version-grabber-all/
mv tls-version-grabber-all-recent/toplistsAlexaUmbrellaMajestic-A-www_domainsNotInZoneLists ../02_tls13version_aggregate1/tls-version-grabber-all-recent/
```

