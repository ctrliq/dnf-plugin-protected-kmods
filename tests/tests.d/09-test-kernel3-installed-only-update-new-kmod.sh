#!/bin/bash

. ../test-common.sh

# Test that everything updates when latest kmod-test and kernel have matching symbols
copy_packages kernel1 test9
copy_packages kmod-test1 test9
mkrepo test9
mkdnfconfig test9
installpkg kernel
installpkg kmod-test
rmrepo test9
copy_packages kernel3 test9
mkrepo test9
dnf -y --refresh --disableplugin=protected-kmods update kernel
rmrepo test9
copy_packages kmod-test2 test9
mkrepo test9
testdnf test9 "Upgrading *: *kmod-test-1.0-2.x86_64"
cleanup
exitcode
