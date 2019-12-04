#!/bin/bash

set -e

path_script="$(pwd -P)"

if [ ! -f "go1.11.5.linux-amd64/go/bin/go" ]; then
    if [ ! -f "go1.11.5.linux-amd64.tar.gz" ]; then
        wget https://dl.google.com/go/go1.11.5.linux-amd64.tar.gz
    fi
    mkdir -p go1.11.5.linux-amd64
    tar -xzf go1.11.5.linux-amd64.tar.gz --directory go1.11.5.linux-amd64
fi
mkdir -p go
export PATH=$path_script/go1.11.5.linux-amd64/go/bin:$PATH
export GOPATH=$path_script/go

mkdir -p go/src/github.com/zmap
pushd go/src/github.com/zmap/
if [ ! -d "zcrypto" ]; then
    git clone https://github.com/tls-evolution/zcrypto.git
fi
if [ ! -d "zgrab" ]; then
    git clone https://github.com/tls-evolution/zgrab.git
fi
popd

# Set up some legacy code not available via go get with go1.11
# Available at https://go.googlesource.com/net/+/refs/heads/release-branch.go1.10/lex/httplex
if [ ! -f "go/src/golang.org/x/net/lex/httplex/httplex.go" ]; then
    go get golang.org/x/net/http/httpguts  # we first need to download the base package, otherwise go get will fail to download it
    mkdir -p go/src/golang.org/x/net/lex/httplex
    curl https://go.googlesource.com/net/+/refs/heads/release-branch.go1.10/lex/httplex/httplex.go?format=TEXT | base64 -d > go/src/golang.org/x/net/lex/httplex/httplex.go
    curl https://go.googlesource.com/net/+/refs/heads/release-branch.go1.10/lex/httplex/httplex_test.go?format=TEXT | base64 -d > go/src/golang.org/x/net/lex/httplex/httplex_test.go
fi

