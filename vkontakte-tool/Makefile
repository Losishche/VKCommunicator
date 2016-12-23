# $Id: Makefile,v 1.6 2009/02/23 16:01:35 simba Exp $
#

PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/vkontakte-tool
PROJECT=vkontakte-tool
VERSION=0.6

all:
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE) $(INSTLAYOUT)

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb:
	mkdir -p ${BUILDIR}
	DESTDIR=$(BUILDIR) dpkg-buildpackage -I -rfakeroot
	
buildsrcdeb:
	mkdir -p ${BUILDIR}
	DESTDIR=$(BUILDIR) dpkg-buildpackage -I -S -sa -rfakeroot

clean:
	$(PYTHON) setup.py clean
	$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf build/
	find . -name '*.pyc' -delete
