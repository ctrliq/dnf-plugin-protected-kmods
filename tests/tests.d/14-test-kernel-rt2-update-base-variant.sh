#!/bin/bash

. ../test-common.sh

# Test that a "-base" suffixed variant protects the plain variant kernel
copy_packages kernel-rt1 test14a
copy_packages kmod-test-rt-base1 test14a
mkrepo test14a
mkdnfconfig test14a
installpkg kernel-rt kmod-test-rt-base
copy_packages kernel-rt2 test14b
mkrepo test14b
mkdnfconfig test14b
testdnfcmd test14b "-y update" "INFO: kmod-test-rt-base: filtering kernel-rt 6.0.0-2, no precompiled modules available" "Nothing to do"
cleanup
exitcode
