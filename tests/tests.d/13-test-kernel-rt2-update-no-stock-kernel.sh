#!/bin/bash

. ../test-common.sh

# Test that a variant kernel update is still filtered when no stock kernel-core is installed
copy_packages kernel-rt1 test13a
copy_packages kmod-test-rt1 test13a
mkrepo test13a
mkdnfconfig test13a
installpkg kernel-rt kmod-test-rt
removepkg kernel kernel-core kernel-modules kernel-modules-core
copy_packages kernel-rt2 test13b
mkrepo test13b
mkdnfconfig test13b
testdnfcmd test13b "-y update" "INFO: kmod-test-rt: filtering kernel-rt 6.0.0-2, no precompiled modules available" "Nothing to do"
cleanup
exitcode
