#!/bin/bash -xe
[[ -d exported-artifacts ]] \
|| mkdir -p exported-artifacts

[[ -d tmp.repos/SOURCES ]] \
|| mkdir -p tmp.repos/SOURCES

make dist
yum-builddep -y ovirt-guest-tools-iso.spec

rpmbuild \
    -D "_topdir $PWD/tmp.repos" \
    -ta *.tar.bz2

find \
    "$PWD/tmp.repos" \
    -iname \*.rpm \
    -exec mv {} exported-artifacts/ \;

find \
    "$PWD/tmp.repos" \
    -iname \*.iso \
    -exec mv {} exported-artifacts/ \;
