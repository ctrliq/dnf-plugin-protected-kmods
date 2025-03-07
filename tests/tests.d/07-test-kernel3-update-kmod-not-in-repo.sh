#!/bin/bash

. ../test-common.sh

# Test that kernel3 update is hidden when no kmod-test is in the repos
copy_packages kernel1 test7a
copy_packages kernel2 test7a
mkrepo test7a
mkdnfconfig test7a
copy_packages kmod-test1 test7b
mkrepo test7b
mkdnfconfig test7b
installpkg kmod-test
copy_packages kernel3 test7a
mkrepo test7a
testdnfcmd test7b " --disablerepo=test7b -y update" "INFO: kmod-test: filtering kernel 6.0.0-3, no precompiled modules available" "kernel *x86_64 *6.0.0-2 *test7a" "Install.* 4 [Pp]ackages" '^Complete!$'
cleanup
exitcode
