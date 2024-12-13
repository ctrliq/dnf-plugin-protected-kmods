#!/bin/bash

# This build should work with both Docker and Podman, assuming that `podman-docker` has been
# installed
cd "$(dirname "$(realpath -- "$0")")";
cd ..

for i in test-build/Dockerfile-base-*; do
    ttype=$(echo $i | awk -F '-' '{ print $4 }')
    docker build -t test-base -f "$i" .
    docker build -t test-${ttype} -f test-build/Dockerfile .
done
