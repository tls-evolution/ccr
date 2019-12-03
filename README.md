# CCR
Reproducibility instructions for CCR paper on TLS 1.3 evolution

We apologise for the need to distribute data sets and tools across several locations and repositories. Data is generally too large to store centrally, but we will endeavor to honor any reviewer request for transfer of larger chunks of data. Tools are often developed inside their own repositories; we link to these.

## Data sets and measurement tools

### Active scans

Our RFC-based scanner is published in this repository: https://github.com/ralphholz-usyd/goscanner/. We provide the scripts to run the scans in active-scans/.

Data sets are massive - we upload these into a DigitalOcean space. We are currently offering full data to the data of 2019-05; other uploads are still going on. These files are publicly visibile, but we would prefer if reviewers are OK with private links. The reason the uploads are so slow is that, e.g., a full PCAP is 0.5TB.

### Passive monitoring

For our passive TLS 1.3 measurements, we cannot release the data for privacy reasons. We can provide high-level statistics in the paper. For reproducibility, we publish the entirety of our passive measurement pipeline in this repository.

https://github.com/0xxon/tls-1.3-passive-pipeline

### Android and Lumen

For our analysis of TLS 1.3 adoption in Android, we used data collected by Lumen. We have released the portion of Lumen data used for this study on the Haystack Project [website](https://haystack.mobi/datasets) and on [Zenodo](https://zenodo.org).

## Analysis scripts

### Android data analysis

The script used to analyze the Lumen dataset can be found on this repository.
