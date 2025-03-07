#!/bin/bash

. ../test-common.sh

# Test that kernel3 update works when no kmod-test is in the repos, but block_updates_when_kmod_not_in_repos is False
cat << EOF > /etc/dnf/plugins/protected-kmods.conf
[main]
block_updates_when_kmod_not_in_repos = False
EOF
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
testdnfcmd test7b " --disablerepo=test7b -y update" "WARNING: Kernel updates will not be blocked based on kmod-test." "kernel *x86_64 *6.0.0-3 *test7a" "Install.* 4 [Pp]ackages" '^Complete!$'
cleanup
rm -f /etc/dnf/plugins/protected-kmods.conf
exitcode
