#!/bin/bash

set -e

path_script="$(pwd -P)"

export PATH=$path_script/go1.11.5.linux-amd64/go/bin:$PATH
export GOPATH=$path_script/go

pushd go/src/github.com/zmap/

scanner_versions=$(git -C zgrab tag -l | grep rabbitQueue_tls-13-all)
for version in $scanner_versions;
do
	echo "building version $scanner_version ..."
	git -C zgrab checkout $version
	git -C zcrypto checkout $version
	pushd zgrab
	go get && go build && cp zgrab zgrab_$version
	popd
	echo -e "Done.\n"
done;
popd

ln -fs go/src/github.com/zmap/zgrab zgrab-binaries

