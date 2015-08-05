#/usr/bin/python

import md5
import os
import sys

src_dir = sys.argv[1]
dest_dir = sys.argv[2]

source_files = {}
dest_files = set([])
for dirname, dirs, files in os.walk(src_dir):
        for filename in files:
                absolute_path = os.path.join(dirname, filename)
                content = file(absolute_path, 'r').read()
                source_files[md5.md5(content).digest()] = absolute_path

for dirname, dirs, files in os.walk(dest_dir):
        for filename in files:
                absolute_path = os.path.join(dirname, filename)
                content = file(absolute_path, 'r').read()
                dest_files.add(md5.md5(content).digest())

missing = set(source_files.keys()).difference(dest_files)

for md5_hash in missing:
        print source_files[md5_hash]
