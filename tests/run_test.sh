#!/bin/bash

cd "$(dirname "$(realpath -- "$0")")";

. ./test-common.sh

# Initial snapshot
snapshotpkgs

cd tests.d
retval=0
for i in *; do
    echo "Running $i"
    /bin/sh "$i"
    if [ "$?" -ne 0 ]; then
        retval=1
    fi
done
cat /var/log/dnf-output* | grep "!!!!!!"
exit $retval
