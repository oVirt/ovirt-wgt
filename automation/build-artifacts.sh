#!/bin/bash -xe
[[ -d exported-artifacts ]] \
|| mkdir -p exported-artifacts

[[ -d tmp.repos/SOURCES ]] \
|| mkdir -p tmp.repos/SOURCES

make dist

SUFFIX=
. automation/config.sh
[ -n "${RELEASE_SUFFIX}" ] && SUFFIX=".$(date -u +%Y%m%d%H%M%S).git$(git rev-parse --short HEAD)"

yum-builddep -y ovirt-guest-tools-iso.spec

rpmbuild \
    -D "_topdir $PWD/tmp.repos" \
    ${SUFFIX:+-D "release_suffix ${SUFFIX}"} \
    -ta *.tar.bz2

mv *.tar.bz2 exported-artifacts

find \
    "$PWD/tmp.repos" \
    -iname ovirt-guest-tools\*.rpm \
    -exec mv {} exported-artifacts/ \;

find \
    "$PWD/tmp.repos" \
    -iname \*.iso \
    -exec mv {} exported-artifacts/ \;
