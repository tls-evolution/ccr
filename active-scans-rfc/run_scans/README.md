# Getting input domains

We have an agreement with the operators of the respective DNS zones not to share their zonefiles with others. We must hence ask you to download the input data sets from DigitalOcean, which are preparsed versions of the zonefiles. See `active-scans-rfc/data/README.md`.

# Running an RFC-based scan

Our assumed working directory is `/home/tls13/tls13/`. Underneath that directory, we organise our files as follows:

```
.
+-- bin/ -- this is where our scripts go
+-- inputs/ -- this is where input files go
+-- outputs/$EPOCH -- you guessed it, the output files will be written to this location
```

where `$EPOCH` is a timestamp we assign to each scan, namely the time when we created the input list.

We provide a number of scripts to run a complete scan. The steps are below.

## Run massdns

Run `1_run_massdns.sh` on your input list of domains.

This will require that you have a power DNS resolver installed somewhere. We used unbound on a machine with 512GB RAM and 48 cores, but you will not need that much. We provide a config file for unbound. The most important thing to remember is that unbound must have a large number of ports available - it will complain about lack of system memory if it cannot get them, but it will also helpfully tell you the command line to set it.

## Run zmap

Run `2_run_zmap.sh` on the output of the previous script (as root!) - the format of the expected filename is in the comments.

This will not require many resources. We limit zmap to 10Mbits.

## Run goscanner

Run `3_run_goscanner.sh` on the output of the massdns script (as root)




