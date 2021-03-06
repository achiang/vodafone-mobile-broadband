SHELL = /bin/bash

VERSION := $(shell python -c 'from gui.consts import APP_VERSION; print APP_VERSION')
SOURCES := $(shell rpmbuild --eval '%{_topdir}' 2>/dev/null)/SOURCES

all:
	@echo Usage: make deb \[TARGET=ubuntu-lucid\] \| rpm

rpm:
	@if [ ! -d $(SOURCES) ] ;\
	then\
		echo 'SOURCES does not exist, are you running on a non RPM based system?';\
		exit 1;\
	fi

	tar -jcvf $(SOURCES)/vodafone-mobile-broadband-$(VERSION).tar.bz2 --exclude=.git --transform="s/^\./vodafone-mobile-broadband-$(VERSION)/" .
	rpmbuild -ba resources/rpm/vodafone-mobile-broadband.spec

deb:
	@if [ ! -d /var/lib/dpkg ] ;\
	then\
		echo 'Debian package directory does not exist, are you running on a non Debian based system?';\
		exit 1;\
	fi

	@if [ -d packaging/debian/$(TARGET)/debian ] ;\
	then\
		PKGSOURCE=$(TARGET);\
	else\
		PKGSOURCE=generic;\
	fi;\
	tar -C packaging/debian/$$PKGSOURCE -cf - debian | tar -xf -

	@if ! head -1 debian/changelog | grep -q $(VERSION) ;\
	then\
		echo Changelog and package version are different;\
		exit 1;\
	fi

	dpkg-buildpackage -rfakeroot
