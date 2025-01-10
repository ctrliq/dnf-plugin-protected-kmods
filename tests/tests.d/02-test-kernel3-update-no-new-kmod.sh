#!/bin/bash

. ../test-common.sh

# Test that kernel3 update is hidden when no kmod-test with matching symbols is found
copy_packages kernel1 test2
copy_packages kernel2 test2
copy_packages kmod-test1 test2
mkrepo test2
mkdnfconfig test2
installpkg kmod-test
copy_packages kernel3 test2
mkrepo test2
testdnf test2 "INFO: kmod-test: filtering kernel 6.0.0-3, no precompiled modules available" "kernel *x86_64 *6.0.0-2 *test2" "Install.* 4 [Pp]ackages" '^Complete!$'
cleanup
exitcode
