#!/bin/sh

# set -x
function testsuiteinit {
     SRCREP=$(echo "$PARAMS" | sed 's/\-\-[[:graph:]]*//g')
     if [ -z "$SRCREP" ]; then
         read -p "Enter repository for systemd source rpm (URL or Name): " SRCREP
     fi

     if [ -n "$SRCREP" ]; then
         [[ "$SRCREP" =~ "http://" ]] && zypper ar $SRCREP systemd-source
         zypper mr -e $SRCREP
     else
         echo "Warning: No systemd source repository found"
         exit 1
     fi

     zypper ref

     BUILDTOOLS="make cryptsetup dhcp-client qemu "

     grep -qi "SUSE Linux Enterprise" /etc/os-release && SLE=1
     if [ $SLE ]; then
         echo "Please make sure that the SDK is installed"
         if [[ $(uname -i) =~ "s390" ]] || [[ $(uname -i) =~ "ppc64" ]]; then
                 BUILDTOOLS="binutils-devel python-lxml python3-lxml "
         else
                 BUILDTOOLS="binutils-gold gnu-efi python-lxml "
         fi
         BUILDTOOLS+="rpm-devel rpm-build libseccomp-devel audit-devel docbook-xsl-stylesheets gobject-introspection-devel \
                      gperf gtk-doc intltool libacl-devel libcap-devel libkmod-devel libsepol-devel pam-devel tcpd-devel \
                      libgcrypt-devel libcryptsetup-devel libkmod-devel libmicrohttpd-devel libapparmor-devel \
                      libselinux-devel libsepol-devel qrencode-devel xz-devel libuuid-devel pciutils-devel libblkid-devel \
                      libcurl-devel libmount-devel "
     else
         BUILDTOOLS+="rpm-build net-tools-deprecated gnu-efi libseccomp-devel audit-devel docbook-xsl-stylesheets gobject-introspection-devel \
                      gperf gtk-doc intltool libacl-devel libcap-devel libkmod-devel libsepol-devel pam-devel tcpd-devel \
                      libgcrypt-devel libcryptsetup-devel libkmod-devel libmicrohttpd-devel libapparmor-devel libselinux-devel libsepol-devel"
     fi

     RUNTOOLS="qemu-x86 "

     echo -e "\nInstalling packages for building and running the test \n"
     # switch back to interactive mode if package installation fails
     for PACKAGE in "$BUILDTOOLS"; do
        zypper -n in --force-resolution $PACKAGE
        if [ $? != 0 ]; then
            zypper in $PACKAGE
	fi
     done
     zypper -n in --from $SRCREP libsystemd0 systemd-devel
     if [ $? != 0 ]; then
         zypper in --from $SRCREP libsystemd0 systemd-devel
     fi
     zypper -n in $RUNTOOLS

     if ! [ -f /usr/src/packages/SPECS/systemd.spec ]; then
         rm -r /usr/src/packages/SOURCES/*
         rm -r /usr/src/packages/BUILD/systemd*
         if ! zypper --gpg-auto-import-keys -n si -r $SRCREP systemd; then
             zypper si -r $SRCREP systemd;
         fi
     fi
}


function testsuiteprepare {
     SPECFILE=$1
     VERSION=$(sed -n '/^Version/s/^Version: *\([[:digit:]]*\).*/\1/p' $SPECFILE)
     echo "Preparing tests for version $VERSION"

     case "$VERSION" in
        234)
             for prog in libcap-progs acl lz4 busybox socat; do
	         zypper -n in "$prog" || zypper in "$prg"
             done
             for id in 1 2 3; do
                 groupadd -g $id systemdtestsuitegroup$id
                 useradd -u $id -g $id systemdtestsuiteuser$id
             done
             useradd systemd-journal-upload
	     useradd systemd-journal-remote
	     groupadd systemd-journal-upload
	     groupadd systemd-journal-remote
	     groupadd mail
	     ;;
        233)
             for prog in libcap-progs acl lz4 busybox socat; do
	         zypper -n in "$prog" || zypper in "$prg"
             done
                 ln -s /usr/include/libseccomp/seccomp.h /usr/include/seccomp.h
             for id in 1 2 3; do
                 groupadd -g $id systemdtestsuitegroup$id
                 useradd -u $id -g $id systemdtestsuiteuser$id
             done
             useradd systemd-journal-upload
	     useradd systemd-journal-remote
	     groupadd systemd-journal-upload
	     groupadd systemd-journal-remote
	     groupadd mail
	     ;;
        232)
             for prog in libcap-progs acl lz4 busybox; do
	         zypper -n in "$prog" || zypper in "$prg"
             done
	     ln -s /usr/include/libseccomp/seccomp.h /usr/include/seccomp.h
             for id in 1 2; do
                 groupadd -g $id systemdtestsuitegroup$id
                 useradd -u $id -g $id systemdtestsuiteuser$id
             done
             useradd systemd-journal-upload
	     ;;
        228)
             zypper -n in python3-lxml || zypper in python3-lxml
             ;;
        210)
             ;;
          *)
             echo "unknown systemd version: $VERSION"
             cleanup
	     exit 1
             ;;
     esac
}

function cleanup {
[ -f /boot/initrd-$(uname -r).saved ] && mv /boot/initrd-$(uname -r).saved /boot/initrd-$(uname -r)
[ -f $WORKDIR/testsuite-v$VERSION-suse.patch ] && rm $WORKDIR/testsuite-v$VERSION-suse.patch

for id in 1 2 3; do
   userdel systemdtestsuiteuser$id
   groupdel systemdtestsuitegroup$id
done
groupdel mail
userdel systemd-journal-upload

rm -r /systemd-testsuite/
rm -r /usr/src/packages/SOURCES/testsuite-v*-suse.patch
rm -r /usr/src/packages/SOURCES/systemd*
rm -r /usr/src/packages/BUILD/systemd*
rm /usr/src/packages/SPECS/systemd.spec
exit
}

WORKDIR=$(pwd)
PARAMS=$@
SPECFILE=/usr/src/packages/SPECS/systemd.spec

for param in $PARAMS; do
	[[ "$param" == "--help" ]] && echo -e "Usage: run-systemd-testsuite.sh [--init] [--rootfs=ROOTFS] [SOURCEREPO]\n\
        --init               compile and prepare testsuite\n\
        --rootfs=ROOTFS      file system to be used in test vm (default btrfs)\n\
	--cleanup            remove previous testsuite setup\n\
        SOURCEREPO           repository of source rpm  (URL or Name)" && exit 0
	[[ "$param" =~ "--init" ]] && (testsuiteinit && testsuiteprepare $SPECFILE)
        [[ "$param" =~ "--rootfs=" ]] && ROOTFS=${param##--rootfs=}
	[[ "$param" == "--cleanup" ]] && cleanup
done

[[ -f $SPECFILE ]] || ( echo "error: no specfile found, please use --init"; exit 1 )
[[ -z $VERSION ]] && VERSION=$(sed -n '/^Version/s/^Version: *\([[:digit:]]*\).*/\1/p' $SPECFILE)
RELEASE=$(sed -n '/^Release/s/Release: *//p' $SPECFILE)

#add SUSE customizations
cd /usr/src/packages/SOURCES

[ -f testsuite-v$VERSION-suse.patch ] ||\
    wget http://beta.suse.com/private/tblume/systemd-testsuite/testsuite-v$VERSION-suse.patch

[ -d /systemd-testsuite/src ] || mkdir -p /systemd-testsuite/src
cp -avr /usr/src/packages/SOURCES/* /systemd-testsuite/src
cd /systemd-testsuite/src
cat $SPECFILE | sed -e '/^%install$/,$d' -e '/--disable-tests/d' > systemd-test.spec
sed -i '0,/^%define.*/s/^%define.*/%global _enable_debug_package 0\n&/' systemd-test.spec
sed -i '0,/^%global.*/s/^%global.*/%global debug_package %{nil}\n&/' systemd-test.spec
sed -i '0,/^%global.*/s/^%global.*/%global __os_install_post \/usr\/lib\/rpm\/brp-compress %{nil}\n&/' systemd-test.spec

if [ -n "$ROOTFS" ]; then
    sed -i "s/btrfs/$ROOTFS/" testsuite-v$VERSION-suse.patch
    lsinitrd | grep $ROOTFS.ko || mv /boot/initrd-$(uname -r) /boot/initrd-$(uname -r).saved\
    ; /usr/bin/dracut --force --add-drivers $ROOTFS /boot/initrd-$(uname -r) $(uname -r)
fi

sed -i "0,/%description.*/s/^%description/Patch0:          testsuite-v$VERSION-suse.patch\n\n&/" systemd-test.spec
#add custom patch if necessary
#sed -i "0,/%description.*/s/^%description/Patch0:          0001-patch-test-functions-script-to-work-with-SUSE-out-of.patch\n\n&/" systemd-test.spec

AUTOPATCH=$(sed -n '/autopatch/p' systemd-test.spec)
[[ -n "$AUTOPATCH" ]] || sed -i '0,/^%build.*/s/^%build.*/%patch0 -p1\n\n&/' systemd-test.spec

/usr/bin/rpmbuild -bc systemd-test.spec

[ -d /systemd-testsuite/run ] && rm -r /systemd-testsuite/run
if [ ! -d /usr/src/packages/BUILD/systemd* ]; then
    echo "systemd-testuite not installed, please run --init and make sure that the SDK repo is available"
    exit 1
else
    echo -e "\nrunning testsuite for systemd sourcepackage: systemd-$VERSION-$RELEASE \n"
    sleep 5
fi

ln -sf /usr/src/packages/BUILD/systemd* /systemd-testsuite/run
cd /systemd-testsuite/run

for i in $(find -name test.sh); do
    chmod ugo+x $i
done

#start tests
echo -e "\nExecuting basic tests \n"
make check

echo -e "\nStarting extended testsuite \n"
cd /systemd-testsuite/run/test
if [[ $((VERSION)) -ge 232 ]]; then
    rm -r /systemd-testsuite/run/test/TEST-06-SELINUX
    sed -i '/SKIP_INITRD=yes/d' /systemd-testsuite/run/test/TEST-*/test.sh
fi

make clean check

read -p "clean testfiles? (y/n)"
[[ $REPLY = "y" ]] && cleanup
