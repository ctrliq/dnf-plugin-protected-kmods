#!/bin/bash

. ../test-common.sh

# Test that installing a kernel-rt with an existing kmod package shows the correct message
copy_packages kernel1 test10a
copy_packages kernel-rt1 test10a
copy_packages kmod-test1 test10a
copy_packages kmod-test-rt1 test10a
mkrepo test10a
mkdnfconfig test10a
installpkg kmod-test
installpkg kernel-rt
testdnfcmd test10a "-y install kmod-test-rt" "Install.* 1 [Pp]ackage" '^Complete!$'
cat /var/log/dnf-output-test10a.log | grep -q 'filtering kernel' && ( echo "Found unexpected kernel filtering message" && export __EXITCODE=1 ) || /bin/true
testdnfcmd test10a "-y update"
cat /var/log/dnf-output-test10a.log | grep -q 'filtering kernel' && ( echo "Found unexpected kernel filtering message" && export __EXITCODE=1 ) || /bin/true
cleanup
exitcode
