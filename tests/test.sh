#!/bin/bash

# This build should work with both Docker and Podman, assuming that `podman-docker` has been
# installed
cd "$(dirname "$(realpath -- "$0")")";
cd ..

retval=0
for i in test-build/Dockerfile-base-*; do
    ttype=$(echo $i | awk -F '-' '{ print $4 }')
    docker run --rm "test-$ttype"
    if [ "$?" -ne 0 ]; then
        retval=1
    fi
done
exit $retval
