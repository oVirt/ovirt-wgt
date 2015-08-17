VERSION="3.6.0_master-0.0${release_suffix}"

dist:
	tar -c --transform 's,^\.,ovirt-wgt,' --exclude=.git --exclude=ovirt-wgt-${VERSION}.tar.gz .  | GZIP=$(GZIP_ENV) gzip -c >ovirt-wgt-${VERSION}.tar.gz
