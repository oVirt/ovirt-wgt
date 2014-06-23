#/usr/bin/python

import iso
import os
import shutil
import virtio


def copy_postinst_files(base_dest, files):
    postinst_path = os.path.join(base_dest, "postinst")
    os.mkdir(postinst_path)
    with open(os.path.join(postinst_path, "postinst.cmd"), 'w') as f:
        for file in files:
            try:
                shutil.copy(file, postinst_path)
                f.write(os.path.basename(file))
                f.write("\r\n")
            except:
                print "Failed to copy postinst file", os.path.basename(file)
                continue


tempdir = "tmp"
os.makedirs(tempdir)
mountpoint = os.path.join(tempdir, "mnt")
base_dest = os.path.join(tempdir, "boxes")
drivers_dest = os.path.join(base_dest, "preinst")
version = "0.1"
output_iso_name = "boxes-unattended-win-drivers-" + version + ".iso"

iso_name = virtio.download_iso(tempdir)
iso_path = os.path.join(tempdir, iso_name)
with iso.IsoMounter(iso_path, mountpoint):
        virtio.copy_drivers(mountpoint, drivers_dest, ('block'))
shutil.copy(os.path.join("boxes-unattended-win-drivers", "README"), base_dest)
shutil.copy(os.path.join("boxes-unattended-win-drivers", "txtsetup.oem"),
os.path.join(drivers_dest, "winxp", "x86"))
iso.geniso(base_dest, output_iso_name, "Boxes Win Drivers")
print output_iso_name, "created"
