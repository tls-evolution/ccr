# Pre-requisites

## Tools
You will need the following tools:

- grepcidr
- join in GNU implementation
- followcnames (see tools/)
- Go in version 1.12 (for perfect replication, otherwise higher is OK)

These tools are needed at various stages in the scripts below. There are environment variables where you can set the correct paths.

## Blacklists

You should ideally also have a working blacklist of IPs and domains so you do not annoy anyone with your scans. We share our blacklist with a team at TU Munich and are not at liberty to hand it out, but we can share it with reviewers if requested. The format is simply one IP prefix per line.

## Input domains

We have an agreement with the operators of the respective DNS zones not to share their zonefiles with others. We must hence ask you to download the input data sets from DigitalOcean, which are preparsed versions of the zonefiles. See `active-scans-rfc/data/README.md`.

# Running an RFC-based scan

Our assumed working directory is `/home/tls13/tls13/`. Underneath that directory, we organise our files as follows:

```
.
+-- go/ -- we put a local installation of Go here
+-- bin/ -- this is where our scripts go
+-- inputs/ -- this is where input files go
+-- outputs/$EPOCH -- you guessed it, the output files will be written to this location
```

where `$EPOCH` is a timestamp we assign to each scan, namely the time when we created the input list.

We provide a number of scripts to run a complete scan. The steps are below.

## Run massdns

Run `1_run_massdns.sh` on your input list of domains.

This will require that you have a power DNS resolver installed somewhere. We used unbound on a machine with 512GB RAM and 48 cores, but you will not need that much. We provide a config file for unbound. The most important thing to remember is that unbound must have a large number of ports available - it will complain about lack of system memory if it cannot get them, but it will also helpfully tell you the command line to set it.

The output of the script are files that are named something like this - each dot in the filename separates the outcome of a step in the script from the next:

```
1564651686_cno.domain.sortu.csv.gz - the compressed input file
1564651686_cno.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains - massdns, filtered for RR and CNAMEs followed; grepcidr'ed with our blacklist for IPs and domains
```

## Run zmap

Run `2_run_zmap.sh` on the output of the previous script (as root!) - the format of the expected filename is in the comments.

This will not require many resources. We limit zmap to 10Mbits.

The script output will be a file like this:
```
1564651686_cno.domain.sortu.csv.massdns.onlyrr.ipdomain.wlip.wldomains.prefixed.sortu.shuf.zmap.ip.sortu.joined - each IP in the massdns output is given a /32 network mask, sort -u and shuffled, then used in zmap. Result IPs are extracted, sort -u applied, and the joined back to the domain list.
```

## Run goscanner

Run `3_run_goscanner.sh` on the output of the massdns script (as root)




