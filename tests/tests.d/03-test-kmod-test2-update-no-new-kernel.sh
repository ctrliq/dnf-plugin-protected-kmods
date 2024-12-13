#!/bin/bash

. ../test-common.sh

# Test that kmod-test2 update is hidden when no kernel with matching symbols is found
copy_packages kernel1 test3
copy_packages kernel2 test3
copy_packages kmod-test1 test3
mkrepo test3
mkdnfconfig test3
installpkg kmod-test
copy_packages kmod-test2 test3
mkrepo test3
testdnf test3 -v "DEBUG: kmod-test: filtering kmods 1.0-2, no matching kernel" "kernel *x86_64 *6.0.0-2 *test3" "Install  4 Packages" '^Complete!$'
cleanup
exitcode
