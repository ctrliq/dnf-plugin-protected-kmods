#!/bin/bash

. ../test-common.sh

# Test that installing a kernel-rt with an existing kmod package shows the correct message
copy_packages kernel1 test12a
copy_packages kernel-rt1 test12a
copy_packages kmod-test1 test12a
copy_packages kmod-test-rt1 test12a
mkrepo test12a
mkdnfconfig test12a
installpkg kmod-test kernel-rt kmod-test-rt
copy_packages kernel-rt2 test12b
copy_packages kmod-test-rt2 test12b
mkrepo test12b
mkdnfconfig test12b
testdnfcmd test12b "-y update" "Install *4 *Packages" "Upgrade *1 Package" "Complete"
cat /var/log/dnf-output-test12b.log | grep -q 'filtering kernel' && ( echo "Found unexpected kernel filtering message" && export __EXITCODE=1 ) || /bin/true
cleanup
exitcode
