# ccr
Reproducibility instructions for CCR paper on TLS 1.3 evolution

We apologise for the need to distribute data sets and tools across several locations and repositories. Data is generally too large to store centrally, but we will endeavor to honor any reviewer request for transfer of larger chunks of data. Tools are often developed inside their own repositories; we link to these.

## Data sets and measurement tools

### Active scans

Our RFC-based scanner is published in this repository: https://github.com/ralphholz-usyd/goscanner/. We provide the scripts to run the scans in active-scans/.

Data sets are massive - we upload these into a DigitalOcean space. We are currently making these files available without any credentials, but ask reviewers not to share the paths with others.

### Passive monitoring

For our passive TLS 1.3 measurements, we cannot release the data for privacy reasons. We can provide high-level statistics in the paper. For reproducibility, we publish the entirety of our passive measurement pipeline in this repository.

https://github.com/0xxon/tls-1.3-passive-pipeline

## Analysis scripts
