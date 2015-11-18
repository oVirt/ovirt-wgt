NAME=spice-nsis
VERSION=0.103
DISPLAYED_VERSION=$(VERSION)
ARCHIVE=$(NAME)-$(VERSION).tar.bz2

# set to OVIRT to build the ovirt guest tools installer
MODE=SPICE

# Note: If you want to change the UN/INSTALLER name, you
# have to edit also the nsis source.
ifeq ($(MODE),SPICE)
# generated executable
INSTALLER=spice-guest-tools-$(VERSION).exe
# 'make install' target (in /usr/share)
INSTALL_NAME=spice-guest-tools-iso
# ISO image filename
ISO_IMAGE=SPICE-tools-$(DISPLAYED_VERSION).iso
# name of the installer on the ISO
ISO_INSTALLER_NAME=spice-guest-tools.exe
# link also to this name which has no version
ISO_GENERIC=SPICE-tools.iso
# ISO image preparer and publisher
ISO_P_TEXT=SPICE project
# ISO image label/identifier. Limited to 16 chars (with joliet extensions)
ISO_LABEL=SPICE-WGT-$(DISPLAYED_VERSION)
else
ifeq ($(MODE),OVIRT)
INSTALLER=ovirt-guest-tools-setup-$(VERSION).exe
INSTALL_NAME=ovirt-guest-tools-iso
ISO_IMAGE=oVirt-toolsSetup_$(DISPLAYED_VERSION).iso
ISO_INSTALLER_NAME=ovirt-guest-tools-setup.exe
ISO_GENERIC=ovirt-tools-setup.iso
ISO_P_TEXT=oVirt - KVM Virtualization Manager Project (www.ovirt.org)
ISO_LABEL=oVirt-WGT-$(DISPLAYED_VERSION)
else
$(error Please set MODE to one of SPICE or OVIRT, not [$(MODE)])
endif
endif

TEMP_DIR=temp_dir

# common dependencies/sources

# From RPMs available at http://www.spice-space.org/download/windows/vdagent/vdagent-win-0.7.3/
VDA32BIN=/usr/i686-w64-mingw32/sys-root/mingw/bin
VDA64BIN=/usr/x86_64-w64-mingw32/sys-root/mingw/bin

# From virtio-win package available in https://fedoraproject.org/wiki/Windows_Virtio_Drivers#Yum.7CDnf_Repo
# TODO:
# We are currently extracting the drivers from an iso inside this RPM.
# Copy directly from the RPM once they are there. See also:
# https://bugzilla.redhat.com/1167941
VIRTIOWINISO=/usr/share/virtio-win/virtio-win.iso
# Replace this with the final directory once it's there
VIRTIOWINDRIVERS=$(TEMP_DIR)/virtio-win-drivers
# Used to re-de-duplicate the drivers as the tool we use (7z) does not support hard links.
# Built into recent Fedora because dracut requires it.
HARDLINK=/usr/sbin/hardlink
# We copy things around using rsync -H to keep hardlinked files hardlinked.
# Many of virtio-win drivers are so - using both of these together currently reduces the
# final oVirt iso from around 230MB to around 100MB.
RSYNC_AH=rsync --archive --hard-links

# ovirt dependencies/sources

# Available from http://resources.ovirt.org/pub/ovirt-3.6/rpm/fc22
OVIRTGA=/usr/share/ovirt-guest-agent-windows

# Available from http://www.microsoft.com/en-us/download/details.aspx?id=5582
# RPM wrapping this available from http://resources.ovirt.org/pub/ovirt-3.6/rpm/fc22
VCREDIST=/usr/share/vcredist-x86/vcredist_x86.exe

# Common definitions for targets
PREFIX=/usr/local
DATAROOT_DIR=$(PREFIX)/share

# install targets
INSTALL_DATA_DIR=$(DATAROOT_DIR)/$(INSTALL_NAME)

all: copy-files iso

copy-files: common-files extra-files

# Note that the installer does not depend here on the copied files,
# so that 'make install-*' will not have to recreate it.
# that's the "lazy" way. The correct way would have been to (automatically)
# add dependencies here per each external file we copy.
# If you do update one of the dependencies (say one of the drivers),
# run 'make clean' before trying again to build.
installer: $(INSTALLER)

$(INSTALLER): win-guest-tools.nsis
	makensis \
		-DVERSION="$(VERSION)" \
		-D"$(MODE)" \
		-DDISPLAYED_VERSION="$(DISPLAYED_VERSION)" \
		win-guest-tools.nsis

common-files: $(VIRTIOWINDRIVERS)
	mkdir -p bin/vdagent_x86 bin/vdagent_x64 drivers/virtio
	$(RSYNC_AH) "$(VDA32BIN)"/vdagent.exe bin/vdagent_x86/
	$(RSYNC_AH) "$(VDA32BIN)"/vdservice.exe bin/vdagent_x86/
	$(RSYNC_AH) "$(VDA64BIN)"/vdagent.exe bin/vdagent_x64/
	$(RSYNC_AH) "$(VDA64BIN)"/vdservice.exe bin/vdagent_x64/
	$(RSYNC_AH) "$(VIRTIOWINDRIVERS)"/* drivers/virtio/

# TODO: Drop this once the drivers are shipped as normal files. See comment above.
$(VIRTIOWINDRIVERS):
	mkdir -p "$(VIRTIOWINDRIVERS)"
	7z -o"$(VIRTIOWINDRIVERS)" x "$(VIRTIOWINISO)"
	# Deduplicate. source iso is already so, but 7z does not support hardlinks.
	# Do not fail on this.
	if [ -x "$(HARDLINK)" ]; then \
		"$(HARDLINK)" -vv "$(VIRTIOWINDRIVERS)"; \
	else \
		echo "Warning: $(HARDLINK) is missing. iso file will have many duplicate files"; \
	fi

# Extra files:

ifeq ($(MODE),SPICE)
extra-files:
	: TODO: Add here spice-specific files if any
else
ifeq ($(MODE),OVIRT)
extra-files:
	$(RSYNC_AH) \
		"$(OVIRTGA)/OVirtGuestService.exe" \
		"$(OVIRTGA)/default.ini" \
		"$(OVIRTGA)/default.ini" \
		"$(OVIRTGA)/default-logger.ini" \
		"$(OVIRTGA)/ovirt-guest-agent.ini" \
		"$(VCREDIST)" \
		bin/
endif
endif

iso: $(ISO_IMAGE)

$(ISO_IMAGE): installer
	mkisofs -J -rational-rock -full-iso9660-filenames -verbose -V "$(ISO_LABEL)" -preparer "$(ISO_P_TEXT)" -publisher "$(ISO_P_TEXT)" -o "$(ISO_IMAGE)" -graft-points bin drivers $(ISO_INSTALLER_NAME)=$(INSTALLER)

install: iso
	mkdir -p "$(DESTDIR)$(INSTALL_DATA_DIR)"
	$(RSYNC_AH) "$(ISO_IMAGE)" "$(DESTDIR)$(INSTALL_DATA_DIR)"
	ln -s "$(ISO_IMAGE)" "$(DESTDIR)$(INSTALL_DATA_DIR)/$(ISO_GENERIC)"

clean:
	rm -rf *.exe bin drivers "$(TEMP_DIR)" "$(ISO_IMAGE)" $(GENERATED)

.SUFFIXES:
.SUFFIXES: .in

.in:
	sed \
	-e "s|@VERSION@|$(VERSION)|g" \
	$< > $@

GENERATED = \
	ovirt-guest-tools-iso.spec \
	$(NULL)

dist: ovirt-guest-tools-iso.spec
	git ls-files | tar --files-from /dev/stdin -jcf "$(ARCHIVE)" --owner=root --group=root --transform 's,^,$(NAME)-$(VERSION)/,' ovirt-guest-tools-iso.spec
