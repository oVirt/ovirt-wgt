#!/usr/bin/python

import os
import re
import shutil
import subprocess
import urllib2

vdagentVersion= "0.7.3"
source_path = "http://www.spice-space.org/download/windows/vdagent/"
fedora_version = "21"
spice_guest_tools_version = "0.74"

class RpmArch : pass
class X86_64(RpmArch): pass
class i686(RpmArch): pass
class NoArch(RpmArch): pass
class Src(RpmArch): pass

def getRpmName(arch):
    if arch is NoArch:
        arch_suffix = ".src"
        mingw_prefix = "mingw-"
    else:
        arch_suffix = ".noarch"
        if arch is X86_64:
            mingw_prefix = "mingw64-"
        else:
            if arch is i686:
                mingw_prefix = "mingw32-"
            else:
                # error - unexpected arch
                return None

    basename = mingw_prefix + "spice-vdagent"
    nevr = vdagentVersion + "-1.fc" + fedora_version
    extension = arch_suffix + ".rpm"
    return basename + "-" + nevr + extension

def generateSourcesFile(tarball):
    cmd = [ "md5sum", tarball ]
    fd = os.open("sources", os.O_WRONLY|os.O_EXCL|os.O_CREAT)
    subprocess.check_call(cmd, stdout=fd)

def buildRpm():
    print "Building mingw-spice-vdagent"
    cmd = [ "/usr/bin/fedpkg", "--module-name", "mingw-spice-vdagent", "--dist=f"+fedora_version, "scratch-build", "--srpm" ]
    #print "cmd:", cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    print "return code:", p.returncode
    print "stdout: ", stdout
    print "stderr: ", stderr

def extractBuildUrl(stdout):
    srcRpmName = "mingw-cximage-600-11.fc20.src.rpm"
    #pattern = "^  ([0-9]+) buildArch \("+srcRpmName+", noarch\): free$"
    pattern = "^  ([0-9]+) buildArch \("+srcRpmName+", noarch\): free$"
    match = re.search(pattern, stdout, re.MULTILINE)
    if match:
        taskId = match.group(1)
    else:
        return None

    return "https://kojipkgs.fedoraproject.org/work/tasks/"+taskId[-4:]+"/"+taskId+"/"

def downloadFile(url, filename):
    print "Downloading", url
    fd = os.open(filename, os.O_WRONLY|os.O_EXCL|os.O_CREAT)
    local_file = os.fdopen(fd, "w")
    remote_file = urllib2.urlopen(url)
    shutil.copyfileobj(remote_file, local_file)
    local_file.close

def dummyScratchBuild(filename):
    cmd = [ "cat", filename ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    #print "return code:", p.returncode
    print "stdout: ", stdout
    #print "stderr: ", stderr
    print "Base URL:", extractBuildUrl(stdout)
    downloadFile(extractBuildUrl(stdout)+"mingw32-cximage-600-11.fc20.noarch.rpm", "foo.rpm")

def downloadSourceTarball():
    filename = "vdagent-win-%s.tar.xz"%vdagentVersion
    sourceUrl = "http://www.spice-space.org/download/windows/vdagent/vdagent-win-%s/"%vdagentVersion + filename
    downloadFile(sourceUrl, filename)

    return filename

def extractSpecFile(tarball):
    cmd = [ "tar", "xfO", tarball, "vdagent-win-*/mingw-spice-vdagent.spec" ]
    fd = os.open("mingw-spice-vdagent.spec", os.O_WRONLY|os.O_EXCL|os.O_CREAT)
    subprocess.check_call(cmd, stdout=fd)




local_dir = "spice-guest-tools-" + spice_guest_tools_version + "-src"
win64_rpm = getRpmName(X86_64)
win32_rpm = getRpmName(i686)

print "local_dir:", local_dir
print "win64 RPM:", win64_rpm
print "win32 RPM:", win32_rpm
#buildRpm("/home/teuf/fedora/mingw-spice-gtk")
#dummyScratchBuild("scratch-build.log")
os.mkdir("mingw-build")
os.chdir("mingw-build")
sourceTarball = downloadSourceTarball()
#hack for testing as current upstream tarball does not contain the .spec file
sourceTarball ="../vdagent-win-0.7.4.tar.xz"
os.symlink(sourceTarball, "vdagent-win-0.7.4.tar.xz")
#end of hack
extractSpecFile(sourceTarball)
generateSourcesFile(sourceTarball)
buildRpm()


#task_id=""
#base_url=""
#remote_rpm = urllib2.urlopen(base_url + iso_name)
#fd = os.open(iso_path, os.O_WRONLY|os.O_EXCL|os.O_CREAT)
#local_iso = os.fdopen(fd, "w")
#shutil.copyfileobj(remote_iso, local_iso)
#local_iso.close
