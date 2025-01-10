#!/bin/bash

. ../test-common.sh

# Test upgrade to kernel2 with matching kmod-test1
copy_packages kernel1 test1
copy_packages kernel2 test1
copy_packages kmod-test1 test1
mkrepo test1
mkdnfconfig test1
installpkg kmod-test
testdnf test1 "kernel *x86_64 *6.0.0-2 *test1" "Install.* 4 [Pp]ackages" '^Complete!$'
exitcode
