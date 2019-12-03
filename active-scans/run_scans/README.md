# Getting input domains

We have an agreement with the operators of the respective DNS zones not to share their zonefiles with others. We must hence ask you to download the input data sets from DigitalOcean, which are preparsed versions of the zonefiles. See analysis/active-scans/README.md.

# Running an RFC-based scan

We provide a number of scripts to run a complete scan. The steps are:

- Run `1_run_massdns.sh` on your input list of domains
- Run `2_run_zmap.sh` on the output of the previous script (as root!)
- Run `3_run_goscanner.sh` on the output of the massdns script (as root)

Our assumed working directory is `/home/tls13/tls13/`. Underneath that directory, we organise our files as follows:
inputs/
outputs/$EPOCH

where $EPOCH is a timestamp we assign to each scan, namely the time when we created the input list.
