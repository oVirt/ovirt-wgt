#!/bin/bash

if [ -f $(dirname ${BASH_SOURCE[0]})/config ]; then
	source $(dirname ${BASH_SOURCE[0]})/config
else
	echo "Requires config to be present."
	echo "$(dirname ${BASH_SOURCE[0]})/config couldn't be found."
	exit 1
fi

if [ -z $1 ]; then
	echo "Usage get-spice-agent.sh <destination directory>"
	echo "Note!: Destination directory requires full path."
	exit 1
fi

TMP_LOC=/tmp/$$-${RANDOM}
mkdir ${TMP_LOC}
pushd ${TMP_LOC}

for file in mingw32-spice-vdagent-0.7.2-1.fc19.noarch.rpm mingw64-spice-vdagent-0.7.2-1.fc19.noarch.rpm
do
	wget ${SPICE_URL}/${file}
	rpm2cpio ${file} | cpio -idmv
done

mkdir -p $1/bin/{vdagent_x86,vdagent_x64}
cp -v ./usr/i686-w64-mingw32/sys-root/mingw/bin/vdagent.exe $1/bin/vdagent_x86/
cp -v ./usr/i686-w64-mingw32/sys-root/mingw/bin/vdservice.exe $1/bin/vdagent_x86/
cp -v ./usr/x86_64-w64-mingw32/sys-root/mingw/bin/vdagent.exe $1/bin/vdagent_x64/
cp -v ./usr/x86_64-w64-mingw32/sys-root/mingw/bin/vdservice.exe $1/bin/vdagent_x64/

popd

rm -rf ${TMP_LOC}
