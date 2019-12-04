#!/bin/bash

set -e

path_script="$(pwd -P)"

export PATH=$path_script/go1.11.5.linux-amd64/go/bin:$PATH
export GOPATH=$path_script/go

