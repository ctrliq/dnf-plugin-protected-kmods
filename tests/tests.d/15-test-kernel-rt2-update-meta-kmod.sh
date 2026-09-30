#!/bin/bash

. ../test-common.sh

# Test that a config naming a meta kmod protects the kernel its installed subpackage requires
copy_packages kernel-rt1 test15a
copy_packages kmod-test-meta1 test15a
mkrepo test15a
mkdnfconfig test15a
installpkg kernel-rt kmod-test-meta
copy_packages kernel-rt2 test15b
mkrepo test15b
mkdnfconfig test15b
testdnfcmd test15b "-y update" "INFO: kmod-test-meta-rt: filtering kernel-rt 6.0.0-2, no precompiled modules available" "Nothing to do"
if grep -q "config implies" /var/log/dnf-output-test15b.log; then
    echo -e "\n!!!!!! Unexpected config mismatch warning for a matching variant !!!!!!!!\n"
    export __EXITCODE=1
fi
cleanup
exitcode
