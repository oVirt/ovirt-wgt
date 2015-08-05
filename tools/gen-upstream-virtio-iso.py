#!/usr/bin/python

import iso
import os
import virtio

tempdir = "tmp"
try:
    os.makedirs(tempdir)
except OSError as e:
    print "Failed to create %s: %s" % (tempdir, e)
mountpoint = os.path.join(tempdir, "mnt")
drivers_dest = os.path.join(tempdir, "drivers")
output_iso_name = "drivers.iso"

iso_name = virtio.download_iso(tempdir)
iso_path = os.path.join(tempdir, iso_name)
with iso.IsoMounter(iso_path, mountpoint):
    virtio.copy_drivers(mountpoint, drivers_dest, copy_debug=True)
    iso.geniso(drivers_dest, output_iso_name)
print "done"


# vim: expandtab tabstop=4 shiftwidth=4
