#!/bin/bash

function copy_packages {
    # Copy all packages from $1 to $2
    mkdir -p /var/tmp/repos/"$2"/Packages
    cp -a --reflink=auto /var/tmp/"$1"/*.rpm /var/tmp/repos/"$2"/Packages
}

function mkrepo {
    # Create repository at $1
    pushd /var/tmp/repos/"$1"
    createrepo_c .
    popd
}

function rmrepo {
    # Remove repository at $1
    rm -rf /var/tmp/repos/"$1"
}

function mkdnfconfig {
    # Create repo file at $1
    cat << EOF > /etc/yum.repos.d/"$1".repo
[$1]
name=$1
baseurl=file:///var/tmp/repos/$1
gpgcheck=0
enabled=1
EOF
}

function rmdnfconfig {
    # Remove repo file at $1
    rm -f /etc/yum.repos.d/"$1".repo
}

function snapshotpkgs {
    rm -rf /var/tmp/snapshot/rpm /var/tmp/snapshot/dnf
    mkdir -p /var/tmp/snapshot
    cp -a --reflink=auto $(readlink -f /var/lib/dnf) /var/tmp/snapshot/
    cp -a --reflink=auto $(readlink -f /var/lib/rpm) /var/tmp/snapshot/
}

function cleanup {
    if [ ! -e /var/tmp/snapshot/dnf ]; then
        return
    fi

    echo "Cleaning up"
    # Remove all dnf repos
    rm -f /etc/yum.repos.d/*.repo
    rm -rf /var/cache/dnf/*
    rm -rf /var/tmp/repos/*
    # Restore RPM and DNF packages
    dnfloc=$(readlink -f /var/lib/dnf)
    rpmloc=$(readlink -f /var/lib/rpm)
    rm -rf "$dnfloc" "$rpmloc"
    cp -a --reflink=auto /var/tmp/snapshot/dnf "$dnfloc"
    cp -a --reflink=auto /var/tmp/snapshot/rpm "$rpmloc"
}

function installpkg {
    dnf -y install "$@" 2>&1 | tee -a /var/log/dnf-output.log
}

function removepkg {
    dnf -y remove "$@" 2>&1 | tee -a /var/log/dnf-output.log
}

function testdnf {
    logloc="$1"
    rm -rf /var/cache/dnf/*
    shift 1
    verbose=""
    if [ "$1" == "-v" ]; then
        verbose=" --setopt=debuglevel=4"
        shift 1
    fi
    set -x
    dnf$verbose -y update 2>&1 | tee /var/log/dnf-output-${logloc}.log
    retval=0
    for match_line in "$@"; do
        cat /var/log/dnf-output-${logloc}.log | grep -q "$match_line"
        if [ "$?" -ne 0 ]; then
            echo -e "\n!!!!!! String $match_line not found in output !!!!!!!!\n"
            export __EXITCODE=1
            retval=1
        fi
    done
    set +x
    return $retval
}

function testdnfcmd {
    logloc="$1"
    rm -rf /var/cache/dnf/*
    shift 1
    verbose=""
    if [ "$1" == "-v" ]; then
        verbose=" --setopt=debuglevel=4"
        shift 1
    fi
    cmd="$1"
    shift 1
    set -x
    dnf$verbose $cmd 2>&1 | tee /var/log/dnf-output-${logloc}.log
    retval=0
    for match_line in "$@"; do
        cat /var/log/dnf-output-${logloc}.log | grep -q "$match_line"
        if [ "$?" -ne 0 ]; then
            echo -e "\n!!!!!! String $match_line not found in output !!!!!!!!\n"
            export __EXITCODE=1
            retval=1
        fi
    done
    set +x
    return $retval
}

function exitcode {
    exit $__EXITCODE
}

cleanup

export __EXITCODE=0
