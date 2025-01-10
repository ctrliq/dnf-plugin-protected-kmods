#!/bin/bash

. ../test-common.sh

# Test that both kernel3 and kmod-test2 are blocked when kernel3 is in a lower priority repo
copy_packages kernel2 test5a
copy_packages kmod-test1 test5a
mkrepo test5a
mkdnfconfig test5a
echo "priority=1" >> /etc/yum.repos.d/test5a.repo
installpkg kmod-test
# Add kmod-test2 to higher priority repo
copy_packages kmod-test2 test5a
mkrepo test5a
# Add kernel1 and kernel3 to lower priority repo
copy_packages kernel1 test5b
copy_packages kernel3 test5b
mkrepo test5b
mkdnfconfig test5b
testdnf test5 -v 'DEBUG: kmod-test: filtering kernel 6.0.0-1, repo priority value higher than other repos with kernels' \
    'DEBUG: kmod-test: filtering kernel 6.0.0-3, repo priority value higher than other repos with kernels' \
    'DEBUG: kmod-test: filtering kmods 1.0-2, no matching kernel' \
    'kernel *x86_64 *6.0.0-2 *test5a' \
    'Install.* 4 [Pp]ackages' \
    '^Complete!$'
cleanup
exitcode
