# README logfilter

The first filter step removes information from the scan-logs that are not needed for this research. This yields smaller logs which allows for faster processing in the following steps.
Furthermore, for very large lists, we split the result logs into multiple parts. Thereby, we sort each measurement entry of a specific domain to the same part such that the later domain-aggregation step is possible with sensible memory resources.



```bash
# Run the filter for com-A-www; this requires a large number of part due to the huge number of domains
list=com-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 50 --basedir $d/; echo -e "--- DONE $d\n\n"; done;

# alexa, net, and org work with 5 buckets (actually we did not use buckets for alexa)
# list=alexa-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 5 --basedir $d/; echo -e "--- DONE $d\n\n"; done;
list=net-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 5 --basedir $d/; echo -e "--- DONE $d\n\n"; done;
list=org-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 5 --basedir $d/; echo -e "--- DONE $d\n\n"; done;

# Run filter for all zones that start with letter a (do this for all other letters in parallel, too, but not in parallel with the large lists above)
letter=a && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${letter}* | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 0 --basedir $d/; echo -e "--- DONE $d\n\n"; done;
```

Finally, we also want to have a list that contains all toplists
```bash
for f in $(find ../../01_scanner/logs/tls-version-grabber-all*/alexa-A-www/ ../../01_scanner/logs/tls-version-grabber-all*/umbrella-A-www/ ../../01_scanner/logs/tls-version-grabber-all*/majestic-A-www/ -type f); do b=$(echo $f | python -c 'import sys; toplistname = "toplistsAlexaUmbrellaMajestic-A-www"; f = sys.stdin.read().rstrip("\n"); path = f.split("/"); path_index_list = 1; path_index_filename = -1; path[path_index_list] = toplistname; filename = path[path_index_filename].split("_"); filename_index_list = 1; filename[filename_index_list] = toplistname; path[path_index_filename] = "_".join(filename); print("/".join(path))') && echo "$(date +%F_%Hh-%Mm-%Ss_%Z) copy $f --> $b" && mkdir -p $(dirname $b) && cat $f >> $b; done;
 ```
 