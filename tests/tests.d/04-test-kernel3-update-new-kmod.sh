#!/bin/bash

. ../test-common.sh

# Test that everything updates when latest kmod-test and kernel have matching symbols
copy_packages kernel1 test4
copy_packages kernel2 test4
copy_packages kmod-test1 test4
mkrepo test4
mkdnfconfig test4
installpkg kmod-test
copy_packages kernel3 test4
copy_packages kmod-test2 test4
mkrepo test4
testdnf test4 "kernel *x86_64 *6.0.0-3 *test4" "Install  4 Packages" '^Complete!$'
cleanup
exitcode
