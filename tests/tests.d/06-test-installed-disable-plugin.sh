#!/bin/bash

. ../test-common.sh

testdnfcmd test6 -v "list installed" 'DEBUG: available sack is empty, so temporarily disabling protected-kmods plugin'
cleanup
exitcode
