#/usr/bin/python

import errno
import os
import re
import shutil
import sys

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

base_src = sys.argv[1]
base_dest = sys.argv[2]
copied_drivers = {}

for win, driver_set in driver_sets.iteritems():
        print "OS: ", win;
        for driver_name, driver in driver_set.iteritems():
                print "DRIVER: ", driver_name
                for arch in [ "x86", "amd64" ]:
                        dest_path = os.path.join(base_dest, win, arch)
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
                                        try:
                                                src_file = os.path.join(src_path, file)
                                                dest_file = os.path.join(dest_path, file)
                                                print "%s from %s to %s"%(op_name, src_file, dest_file)
                                                if (os.path.isfile(dest_file)):
                                                        raise OSError(errno.EEXIST, os.strerror(errno.EEXIST))
                                                copy_func(src_file, dest_file)
                                        except OSError as e:
                                                print "exception: ", file
                                                if e.errno != errno.EEXIST:
                                                        print "different errno"
                                                if file != "wdfcoinstaller01009.dll":
                                                        print "different file"
                                                if file != "wdfcoinstaller01009.dll" or e.errno != errno.EEXIST:
                                                        raise

                        copied_drivers[driver_key] = dest_path

