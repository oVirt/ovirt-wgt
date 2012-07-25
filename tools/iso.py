import subprocess

def geniso(src_dir, iso_path):
        subprocess.call(["genisoimage", "--cache-inodes", "-J", "-r", "-o", iso_path, src_dir])

class IsoMounter:
        def __init__(self, iso_path, mountpoint):
            self.iso_path = iso_path
            self.mountpoint = mountpoint

        def __enter__(self):
            subprocess.call(["fuseiso", "-p", self.iso_path, self.mountpoint])

        def __exit__(self, type, value, traceback):
            subprocess.call(["fusermount", "-u", self.mountpoint])

