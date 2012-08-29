import errno
import os
import re
import shutil
import sys
import urllib2

_debug_regex = re.compile(".*\.pdb$")

class Driver:
        def __init__(self, x86_path, amd64_path, file_regex):
                self.paths = { "x86": x86_path, "amd64": amd64_path }
                self.file_regex = file_regex


driver_sets = {
    "winxp": {
        "netkvm": Driver("XP/x86", "XP/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Wxp/x86", "Wnet/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Wxp/x86", "Wnet/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Wxp/x86", "Wnet/amd64", "viostor.*"),
        "scsi": Driver("Wnet/x86", "Wnet/amd64", "vioscsi.*"),
    },
    "win2k3": {
        "netkvm": Driver("XP/x86", "XP/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Wnet/x86", "Wnet/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Wnet/x86", "Wnet/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Wnet/x86", "Wnet/amd64", "viostor.*"),
        "scsi": Driver("Wnet/x86", "Wnet/amd64", "vioscsi.*"),
    },
    "vista": {
        "netkvm": Driver("Vista/x86", "Vista/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Wlh/x86", "Wlh/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Wlh/x86", "Wlh/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Wlh/x86", "Wlh/amd64", "viostor.*"),
        "scsi": Driver("Wlh/x86", "Wlh/amd64", "vioscsi.*"),
    },
    "win2k8": {
        "netkvm": Driver("Vista/x86", "Vista/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Wlh/x86", "Wlh/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Wlh/x86", "Wlh/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Wlh/x86", "Wlh/amd64", "viostor.*"),
        "scsi": Driver("Wlh/x86", "Wlh/amd64", "vioscsi.*"),
    },
    "win7": {
        "netkvm": Driver("Win7/x86", "Win7/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Win7/x86", "Win7/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Win7/x86", "Win7/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Win7/x86", "Win7/amd64", "viostor.*"),
        "scsi": Driver("Win7/x86", "Win7/amd64", "vioscsi.*"),
    },
    "win2k8r2": {
        "netkvm": Driver("Win7/x86", "Win7/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Win7/x86", "Win7/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Win7/x86", "Win7/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Wlh/x86", "Wlh/amd64", "viostor.*"),
        "scsi": Driver("Win7/x86", "Win7/amd64", "vioscsi.*"),
    },
    "win8": {
        "netkvm": Driver("Win7/x86", "Win7/amd64", "(netkvm.*|readme.doc)"),
        "serial": Driver("Win7/x86", "Win7/amd64", "(vioser.*|wdfcoinstaller.*.dll)"),
        "balloon": Driver("Win7/x86", "Win7/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)"),
        "block": Driver("Wlh/x86", "Wlh/amd64", "viostor.*"),
        "scsi": Driver("Win7/x86", "Win7/amd64", "vioscsi.*"),
    }
}

copied_drivers = {}

def _copy_driver(base_src, base_dest, driver, win_name, copy_debug = False):
        for arch in [ "x86", "amd64" ]:
                dest_path = os.path.join(base_dest, win_name, arch)
                try:
                        os.makedirs(dest_path)
                except OSError as e:
                        if e.errno != errno.EEXIST:
                                raise

                driver_key = (os.path.join(driver.paths[arch], driver.file_regex))
                try:
                        src_path = copied_drivers[driver_key]
                        copy_func = os.link
                        op_name = "hardlink"
                except KeyError:
                        src_path = os.path.join(base_src, driver.paths[arch].lower())
                        copy_func = shutil.copy
                        op_name = "copy"

                file_regex = re.compile(driver.file_regex)
                for file in os.listdir(src_path):
                        if (file_regex.match(file)):
                                if not copy_debug and _debug_regex.match(file):
                                        continue
                                try:
                                        src_file = os.path.join(src_path, file)
                                        dest_file = os.path.join(dest_path, file)
                                        print "%s from %s to %s"%(op_name, src_file, dest_file)
                                        if (os.path.isfile(dest_file)):
                                                raise OSError(errno.EEXIST, os.strerror(errno.EEXIST))
                                        copy_func(src_file, dest_file)
                                except OSError as e:
                                        if file != "wdfcoinstaller01009.dll" or e.errno != errno.EEXIST:
                                                raise

                        copied_drivers[driver_key] = dest_path

def copy_drivers(base_src, base_dest, driver_filter = None, copy_debug = False):
        for win, driver_set in driver_sets.iteritems():
                print "OS: ", win;
                for driver_name, driver in driver_set.iteritems():
                        if driver_filter != None and not driver_name in driver_filter:
                                print "skipping ", driver_name
                                continue
                        print "DRIVER: ", driver_name
                        _copy_driver(base_src, base_dest, driver, win, copy_debug)

def download_iso(dest):
        base_url = "http://alt.fedoraproject.org/pub/alt/virtio-win/latest/images/bin/"
        try:
                response = urllib2.urlopen(base_url)
                html = response.read()

                isos = set(re.findall("virtio-win.*?\.iso", html))
                if len(isos) != 1:
                        raise Exception("failure parsing http://alt.fedoraproject.org/pub/alt/virtio-win/latest/images/bin/ for iso name")

                iso_name = isos.pop()
                iso_path = os.path.join(dest, iso_name)
                print "Downloading", iso_name, "..."
                remote_iso = urllib2.urlopen(base_url + iso_name)
                fd = os.open(iso_path, os.O_WRONLY|os.O_EXCL|os.O_CREAT)
                local_iso = os.fdopen(fd, "w")
                shutil.copyfileobj(remote_iso, local_iso)
                local_iso.close
                print iso_name, "successfully downloaded"

                return iso_name

        except:
                if 'fd' in locals():
                        os.remove(iso_name)
                raise
