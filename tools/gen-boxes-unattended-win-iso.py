#/usr/bin/python

import iso
import os
import shutil
import virtio

tempdir = "tmp"
os.makedirs(tempdir)
mountpoint = os.path.join(tempdir, "mnt")
base_dest = os.path.join(tempdir, "boxes")
drivers_dest = os.path.join(base_dest, "preinst")
output_iso_name = "boxes-unattended-win-drivers.iso"

iso_name = virtio.download_iso(tempdir)
iso_path = os.path.join(tempdir, iso_name)
with iso.IsoMounter(iso_path, mountpoint):
        virtio.copy_drivers(mountpoint, drivers_dest, ( 'block' ) )
shutil.copy(os.path.join("boxes-unattended-win-drivers", "README"), base_dest)
shutil.copy(os.path.join("boxes-unattended-win-drivers", "txtsetup.oem"), os.path.join(drivers_dest, "winxp", "x86"))
iso.geniso(base_dest, output_iso_name)
print "done"
