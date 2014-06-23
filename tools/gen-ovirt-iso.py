#/usr/bin/python

import iso
import sys

if len(sys.argv) < 2:
    print "Requires version param"
    sys.exit(1)

isodir = "iso"
output_iso_name = "ovirt-guest-tools-" + sys.argv[1] + ".iso"

iso.geniso(isodir, output_iso_name)

print "done"
