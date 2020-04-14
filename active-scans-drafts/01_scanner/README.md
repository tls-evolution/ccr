# README draft-scanner

This directory contains the code and scripts for our zgrab-based TLS 1.3 draft scanner:

* `01_basic_setup.sh` sets up the go environment for compiling the different scanner versions
* `source 02_load_go.sh` ensures usage of the just unpacked go version
* `03_compile_scanners.sh` compiles the different scanner versions. They are named according to the date when they have been deployed in our scan infrastructure.
* `04_runner-scripts` contains bash scripts that show how to use the scanner including example input files and blacklist configuration

