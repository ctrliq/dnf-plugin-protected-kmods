#!/bin/bash

. ../test-common.sh

# Install a protected kmod, then drop its repo so the available sack is empty
copy_packages kernel1 test6
copy_packages kmod-test1 test6
mkrepo test6
mkdnfconfig test6
installpkg kmod-test
rmdnfconfig test6
testdnfcmd test6 -v "list installed" 'DEBUG: available sack is empty, so temporarily disabling protected-kmods plugin'
cleanup
exitcode
