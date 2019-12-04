# README logfilter

The first filter step removes information from the scan-logs that are not needed for this research. This yields smaller logs which allows for faster processing in the following steps.
Furthermore, for very large lists, we split the result logs into multiple parts. Thereby, we sort each measurement entry of a specific domain to the same part such that the later domain-aggregation step is possible with sensible memory resources.



```bash
# Run the filter for com-A-www; this requires a large number of part due to the huge number of domains
list=com-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 50 --basedir $d/; echo -e "--- DONE $d\n\n"; done;

# alexa, net, and org work with 5 buckets
list=alexa-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 5 --basedir $d/; echo -e "--- DONE $d\n\n"; done;
list=net-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 5 --basedir $d/; echo -e "--- DONE $d\n\n"; done;
list=org-A-www && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${list} | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 5 --basedir $d/; echo -e "--- DONE $d\n\n"; done;

# Run filter for all zones that start with letter a (do this for all other letters in parallel, too, but not in parallel with the large lists above)
letter=a && for d in $(ls -d ../../01_scanner/logs/tls-version-grabber-all*/${letter}* | grep -v '\-A$'); do echo "--- START $d" && python3 tls13version_logfilter_run.py --buckets 0 --basedir $d/; echo -e "--- DONE $d\n\n"; done;
```

