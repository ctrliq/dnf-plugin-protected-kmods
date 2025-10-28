#!/bin/bash

. ../test-common.sh

# Test that installing a kernel-rt with an existing kmod package shows the correct message
copy_packages kernel1 test11a
copy_packages kernel-rt1 test11a
copy_packages kmod-test1 test11a
copy_packages kmod-test-rt1 test11a
mkrepo test11a
mkdnfconfig test11a
installpkg kmod-test kernel-rt kmod-test-rt
copy_packages kernel-rt2 test11b
mkrepo test11b
mkdnfconfig test11b
testdnfcmd test11b "-y update" "INFO: kmod-test-rt: filtering kernel-rt 6.0.0-2, no precompiled modules available" "Nothing to do"
cleanup
exitcode
