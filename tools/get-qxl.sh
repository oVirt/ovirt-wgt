#!/bin/sh

if [ -f $(dirname ${BASH_SOURCE[0]})/config ]; then
	source $(dirname ${BASH_SOURCE[0]})/config
else
	echo "Requires config to be present."
	echo "$(dirname ${BASH_SOURCE[0]})/config couldn't be found."
	exit 1
fi

if [ -z $1 ]; then
	echo "Usage: get-qxl.sh <destination directory>"
	exit 1
fi

pushd $1

for file in qxl_8k2R2_x64.zip qxl_w7_x64.zip qxl_w7_x86.zip qxl_xp_x86.zip
do
	wget ${QXL_URL}/${file}
	unzip ${file}
	rm ${file}
done

mv xp winxp
mv w7 win7
mv 2k8R2 win2k8r2

popd
