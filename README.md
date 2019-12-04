# CCR
Reproducibility instructions for CCR paper on TLS 1.3 evolution

We apologise for the need to distribute data sets and tools across several locations and repositories. Data is generally too large to store centrally, but we will endeavor to honor any reviewer request for transfer of larger chunks of data. Tools are often developed inside their own repositories; we link to these.

## Data sets and measurement tools

### Preparation

We provide IP ranges as determined by us for the chosen providers in `preparation/ipranges`. In `preparation/mappings`, you find key-value pairs of scan timestamps to respective months. Some of our analysis scripts use these to automatically figure out which file to load next. The scripts have environment variables that you can point at the directory holding the mappings.

### Active scans (RFC)

[Quick link to data for the impatient](https://github.com/tls-evolution/ccr/tree/master/active-scans-rfc/data)

Our RFC-based scanner is published in this [repository](https://github.com/tls-evolution/goscanner). We provide the scripts to run the scans in the directory `active-scans/run-scans/` in this repo.

Our data sets are massive - we upload these into a DigitalOcean space. We are currently offering the output data for all our scans, but the PCAPs for just 2019-05 because they need 0.5TB storage.
We are happy to offer all PCAPs via direct transfer if requested.

### Passive monitoring

For our passive TLS 1.3 measurements, we cannot release the data for privacy reasons. We can provide high-level statistics in the paper. For reproducibility, we publish the entirety of our passive measurement pipeline in this repository.

https://github.com/0xxon/tls-1.3-passive-pipeline

### Android and Lumen

For our analysis of TLS 1.3 adoption in Android, we used data collected by Lumen. We have released the portion of Lumen data used for this study on the Haystack Project [website](https://haystack.mobi/datasets) and on [Zenodo](https://zenodo.org).

## Analysis scripts

### Active scans (RFC)



### Android data analysis

The script used to analyze the Lumen dataset can be found on this repository.
