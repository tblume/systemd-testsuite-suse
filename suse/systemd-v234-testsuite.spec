#
# spec file for package systemd
#
# Copyright (c) 2020 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


#
# The git repository used to track all Suse specific changes can be
# found at: https://github.com/openSUSE/systemd.
#

%define bootstrap 0
%define mini %nil
%define min_kernel_version 4.5
%define suse_version +suse.531.g4695ebe0b9

%bcond_with     gnuefi
%if 0%{?bootstrap}
%bcond_with     sysvcompat
%bcond_with     machined
%bcond_with     importd
%bcond_with     networkd
%else
%bcond_without  sysvcompat
%bcond_without  machined
%bcond_without  importd
%ifarch %{ix86} x86_64
%bcond_without  gnuefi
%endif
%if 0%{?is_opensuse}
%bcond_without  networkd
%else
%bcond_with     networkd
%endif
%endif
%bcond_with     journal_remote
%bcond_with     resolved

Name:           systemd
URL:            http://www.freedesktop.org/wiki/Software/systemd
Version:        234
Release:        0
Summary:        A System and Session Manager
License:        LGPL-2.1-or-later
Group:          System/Base
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%if ! 0%{?bootstrap}
BuildRequires:  docbook-xsl-stylesheets
BuildRequires:  kbd
BuildRequires:  libapparmor-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  libxslt-tools
%if %{with networkd}
BuildRequires:  polkit
%endif
# python is only required for generating systemd.directives.xml
BuildRequires:  python3
BuildRequires:  python3-lxml
BuildRequires:  pkgconfig(libcryptsetup) >= 1.6.0
BuildRequires:  pkgconfig(libdw) >= 0.158
BuildRequires:  pkgconfig(liblz4)
BuildRequires:  pkgconfig(liblzma)
BuildRequires:  pkgconfig(libqrencode)
BuildRequires:  pkgconfig(libselinux) >= 2.1.9
%ifarch aarch64 %ix86 x86_64 x32 %arm ppc64le s390x
BuildRequires:  pkgconfig(libseccomp) >= 2.3.1
%endif
%endif
BuildRequires:  fdupes
BuildRequires:  gperf
BuildRequires:  intltool
BuildRequires:  libacl-devel
BuildRequires:  libcap-devel
BuildRequires:  libmount-devel >= 2.27.1
BuildRequires:  libtool
BuildRequires:  pam-devel
# regenerate_initrd_post macro is expanded during build, hence this
# BR. Also this macro was introduced since version 12.4.
BuildRequires:  suse-module-tools >= 12.4
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(blkid) >= 2.26
BuildRequires:  pkgconfig(libkmod) >= 15
BuildRequires:  pkgconfig(libpci) >= 3
BuildRequires:  pkgconfig(libpcre)
%if %{with importd}
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(zlib)
%endif
%if %{with journal_remote}
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libmicrohttpd) >= 0.9.33
%endif
%if %{with gnuefi}
BuildRequires:  gnu-efi
%endif

%if 0%{?bootstrap}
#!BuildIgnore:  dbus-1
Requires:       this-is-only-for-build-envs
Provides:       systemd = %{version}-%{release}
%else
# the buildignore is important for bootstrapping
#!BuildIgnore:  udev
Requires:       dbus-1 >= 1.4.0
Requires:       kbd
Requires:       kmod >= 15
Requires:       netcfg >= 11.5
Requires:       systemd-presets-branding
Requires:       sysvinit-tools
Requires:       udev = %{version}-%{release}
Requires:       util-linux >= 2.27.1
Requires:       group(lock)
Recommends:     %{name}-bash-completion
Requires(post): coreutils
Requires(post): findutils
Requires(post): systemd-presets-branding
Requires(post): pam-config >= 0.79-5
%endif

%if 0%{?bootstrap}
Conflicts:      systemd
Conflicts:      kiwi
%endif
Conflicts:      sysvinit
Conflicts:      filesystem < 11.5
Conflicts:      mkinitrd < 2.7.0
Conflicts:      suse-module-tools < 15.0.1
Obsoletes:      systemd-analyze < 201
Provides:       systemd-analyze = %{version}
Obsoletes:      pm-utils <= 1.4.1
Obsoletes:      suspend <= 1.0
Source0:        systemd-v%{version}%{suse_version}.tar.xz
Source1:        %{name}-rpmlintrc
Source2:        systemd-user
Source3:        systemd-sysv-convert
Source6:        baselibs.conf
Source11:       after-local.service
Source12:       systemd-sysv-install
Source14:       kbd-model-map.legacy

Source100:      scripts-systemd-fix-machines-btrfs-subvol.sh
Source101:      scripts-systemd-upgrade-from-pre-210.sh
Source102:      scripts-systemd-migrate-sysconfig-i18n.sh
Source200:      scripts-udev-convert-lib-udev-path.sh

# Homeless rules sent (and maintained) by the kernel folks (see bsc#1040800)
Source2000:     80-acpi-container-hotplug.rules
Source2001:     99-wakeup-from-idle.rules
Source2002:     80-hotplug-cpu-mem.rules

# Patches listed in here are put in quarantine. Normally all
# changes must go to upstream first and then are cherry-picked in the
# SUSE git repository. But in very few cases, some stuff might be
# broken in upstream and need an urgent fix. Even in this case, the
# patches are temporary and should be removed as soon as a fix is
# merged by upstream.
Patch1:         0001-udev-don-t-create-by-partlabel-primary-and-.-logical.patch
Patch2:         0002-udev-optionally-disable-the-generation-of-the-partla.patch
Patch3:         0001-core-coldplug-possible-nop_job.patch
Patch4:         0001-mount-swap-cryptsetup-introduce-an-option-to-prevent.patch

# Temporary patch due to SLE15-SP2 having a more recent kernel
Patch50:        0001-seccomp-shm-get-at-dt-now-have-their-own-numbers-eve.patch

# jsc#SLE-7743
Patch100:       0001-tests-when-running-a-manager-object-in-a-test-migrat.patch
Patch101:       0002-in-addr-util-be-more-systematic-with-naming-our-func.patch
Patch102:       0003-in-addr-util-prefix-return-parameters-with-ret_.patch
Patch103:       0004-in-addr-util-add-new-helper-call-in_addr_prefix_from.patch
Patch104:       0005-build-sys-add-new-kernel-bpf.h-drop-in.patch
Patch105:       0006-Add-abstraction-model-for-BPF-programs.patch
Patch106:       0007-Add-IP-address-address-ACL-representation-and-parser.patch
Patch107:       0008-cgroup-add-fields-to-accommodate-eBPF-related-detail.patch
Patch108:       0009-Add-firewall-eBPF-compiler.patch
Patch109:       0010-cgroup-unit-fragment-parser-make-use-of-new-firewall.patch
Patch110:       0011-manager-hook-up-IP-accounting-defaults.patch
Patch111:       0012-systemctl-report-accounted-network-traffic-in-system.patch
Patch112:       0013-man-document-the-new-ip-accounting-and-filting-direc.patch
Patch113:       0014-cgroup-dump-the-newly-added-IP-settings-in-the-cgrou.patch
Patch114:       0015-core-support-IP-firewalling-to-be-configured-for-tra.patch
Patch115:       0016-ip-address-access-minimize-IP-address-lists.patch
Patch116:       0017-Add-test-for-eBPF-firewall-code.patch
Patch117:       0018-core-warn-loudly-if-IP-firewalling-is-configured-but.patch
Patch118:       0019-socket-label-let-s-use-IN_SET-so-that-we-have-to-cal.patch
Patch119:       0020-core-when-creating-the-socket-fds-for-a-socket-unit-.patch
Patch120:       0021-core-serialize-deserialize-IP-accounting-across-daem.patch
Patch121:       0022-core-when-coming-back-from-reload-reexec-reapply-all.patch
Patch122:       0023-cgroup-refuse-to-return-accounting-data-if-accountin.patch
Patch123:       0024-bpf-set-BPF_F_ALLOW_OVERRIDE-when-attaching-a-cgroup.patch
Patch124:       0025-fix-compile-error-on-musl.patch
Patch125:       0026-bpf-firewall-properly-handle-kernels-where-BPF-cgrou.patch
Patch126:       0027-core-improve-dbus-cgroup-error-message.patch
Patch127:       0028-run-also-show-IP-traffic-accounting-data-on-systemd-.patch
Patch128:       0029-core-only-warn-about-BPF-cgroup-missing-once-per-run.patch
Patch129:       0030-cgroup-drop-unused-parameter-from-function.patch
Patch130:       0031-bpf-firewall-actually-invoke-BPF_PROG_ATTACH-to-chec.patch
Patch131:       0032-ip-address-access-let-s-exit-the-loop-after-invalida.patch
Patch132:       0033-bpf-firewall-fix-warning-text.patch
Patch133:       0034-bpf-add-new-bpf.h-header-copy-from-4.15-kernel.patch
Patch134:       0035-bpf-beef-up-bpf-detection-check-if-BPF_F_ALLOW_MULTI.patch
Patch135:       0036-bpf-program-optionally-take-fd-of-program-to-detach.patch
Patch136:       0037-bpf-use-BPF_F_ALLOW_MULTI-flag-if-it-is-available.patch
Patch137:       0038-bpf-program-make-bpf_program_load_kernel-idempotent.patch
Patch138:       0039-bpf-rework-how-we-keep-track-and-attach-cgroup-bpf-p.patch
Patch139:       0040-bpf-reset-extra-IP-accounting-counters-when-turning-.patch
Patch140:       0041-Fix-three-uses-of-bogus-errno-value-in-logs-and-retu.patch
Patch141:       0042-tree-wide-avoid-assignment-of-r-just-to-use-in-a-com.patch
Patch142:       0043-core-fix-the-check-if-CONFIG_CGROUP_BPF-is-on.patch
Patch143:       0044-bpf-firewall-always-use-log_unit_xyz-insteadof-log_x.patch
Patch144:       0045-main-bump-RLIMIT_MEMLOCK-for-the-root-user-substanti.patch
Patch145:       0046-cgroup-always-invalidate-cpu-and-cpuacct-together.patch
Patch146:       0047-unit-initialize-bpf-cgroup-realization-state-properl.patch
Patch147:       0048-cgroup-improve-cg_mask_to_string-a-bit-and-add-tests.patch
Patch148:       0049-core-rename-cgroup_queue-cgroup_realize_queue.patch
Patch149:       0050-core-refactor-bpf-firewall-support-into-a-pseudo-con.patch
Patch150:       0051-Move-warning-about-unsupported-BPF-firewall-right-be.patch
Patch151:       0052-core-bump-mlock-ulimit-to-64Mb.patch
Patch152:       0053-def-add-a-high-limit-for-RLIMIT_NOFILE.patch
Patch153:       0054-main-introduce-a-define-HIGH_RLIMIT_MEMLOCK-similar-.patch
Patch154:       0055-main-when-bumping-RLIMIT_MEMLOCK-save-the-previous-v.patch

# A bunch of upstream commits that allow to configure user slices
# using dash-truncated dropins. The new mechanism is used (since v239)
# to replace UserTasksMax= option in logind.conf. This allows to start
# deprecating UserTasksMax usage which could hopefully be removed from
# the next major version of SLE.
Patch200:       0001-shared-dropin-improve-error-message.patch
Patch201:       0002-tests-skip-tests-when-cg_pid_get_path-fails-7033.patch
Patch202:       0003-unit-name-add-new-unit_name_build_from_type-helper.patch
Patch203:       0004-systemctl-fix-indentation-in-output-of-systemcl-stat.patch
Patch204:       0005-dropin-when-looking-for-dropins-for-a-unit-also-look.patch
Patch205:       0006-test-add-test-for-prefix-unit-loading.patch
Patch206:       0007-man-document-the-new-dash-truncation-drop-in-directo.patch
Patch207:       0008-Use-a-dash-truncated-drop-in-for-user-j.slice-config.patch
Patch208:       0009-login-fix-typo-in-log-message.patch
Patch209:       0010-logind-move-two-functions-to-logind_core-utility-lib.patch
# SUSE specific patch to keep backward compatibility when
# UserTasksMax= is used. In this case it converts at runtime the
# option into a dash-truncated dropin and also warn the user about the
# deprecated option and how to permanently migrate to the new setting.
Patch210:       0011-logind-keep-backward-compatibility-with-UserTasksMax.patch

Patch1000:      0001-polkit-on-async-pk-requests-re-validate-action-detai.patch
Patch1001:      0002-sd-bus-introduce-API-for-re-enqueuing-incoming-messa.patch
Patch1002:      0003-polkit-when-authorizing-via-PK-let-s-re-resolve-call.patch

%description
Systemd is a system and service manager, compatible with SysV and LSB
init scripts for Linux. systemd provides aggressive parallelization
capabilities, uses socket and D-Bus activation for starting services,
offers on-demand starting of daemons, keeps track of processes using
Linux cgroups, supports snapshotting and restoring of the system state,
maintains mount and automount points and implements an elaborate
transactional dependency-based service control logic. It can work as a
drop-in replacement for sysvinit.

%package devel
Summary:        Development headers for systemd
License:        LGPL-2.1-or-later
Group:          Development/Libraries/C and C++
Requires:       libsystemd0%{?mini} = %{version}-%{release}
Requires:       systemd-rpm-macros
%if 0%{?bootstrap}
Conflicts:      systemd-devel
%endif

%description devel
Development headers and auxiliary files for developing applications for systemd.

%package sysvinit
Summary:        System V init tools
License:        LGPL-2.1-or-later
Group:          System/Base
Requires:       %{name} = %{version}-%{release}
Provides:       sbin_init
Conflicts:      otherproviders(sbin_init)
Provides:       sysvinit:/sbin/init

%description sysvinit
Drop-in replacement of System V init tools.

%package -n libsystemd0%{?mini}
Summary:        Component library for systemd
License:        LGPL-2.1-or-later
Group:          System/Libraries
%if 0%{?bootstrap}
Conflicts:      libsystemd0
Requires:       this-is-only-for-build-envs
%endif

%description -n libsystemd0%{?mini}
This library provides several of the systemd C APIs:

* sd-bus implements an alternative D-Bus client library that is
  relatively easy to use, very efficient and supports both classic
  D-Bus as well as kdbus as transport backend.

* sd-daemon(3): for system services (daemons) to report their status
  to systemd and to make easy use of socket-based activation logic

* sd-event is a generic event loop abstraction that is built around
  Linux epoll, but adds features such as event prioritization or
  efficient timer handling.

* sd-id128(3): generation and processing of 128-bit IDs

* sd-journal(3): API to submit and query journal log entries

* sd-login(3): APIs to introspect and monitor seat, login session and
  user status information on the local system.

%package -n udev%{?mini}
Summary:        A rule-based device node and kernel event manager
License:        GPL-2.0-only
Group:          System/Kernel
URL:            http://www.kernel.org/pub/linux/utils/kernel/hotplug/udev.html
Requires:       system-group-hardware
Requires(pre):  /usr/bin/stat
Requires(post): sed
Requires(post): /usr/bin/systemctl

Requires(post): coreutils
Requires(postun): coreutils

Conflicts:      systemd < 39
Conflicts:      aaa_base < 11.5
Conflicts:      filesystem < 11.5
Conflicts:      mkinitrd < 2.7.0
Conflicts:      dracut < 044.1
Conflicts:      util-linux < 2.16
Conflicts:      ConsoleKit < 0.4.1
Requires:       filesystem
%if 0%{?bootstrap}
Provides:       udev = %{version}
Conflicts:      libudev1
Conflicts:      udev
# avoid kiwi picking it for bootstrap
Requires:       this-is-only-for-build-envs
%endif

%description -n udev%{?mini}
Udev creates and removes device nodes in /dev for devices discovered or
removed from the system. It receives events via kernel netlink messages
and dispatches them according to rules in /lib/udev/rules.d/. Matching
rules may name a device node, create additional symlinks to the node,
call tools to initialize a device, or load needed kernel modules.

%package -n libudev%{?mini}1
Summary:        Dynamic library to access udev device information
License:        LGPL-2.1-or-later
Group:          System/Libraries
%if 0%{?bootstrap}
Conflicts:      libudev1
Conflicts:      kiwi
# avoid kiwi picking it for bootstrap
Requires:       this-is-only-for-build-envs
%endif

%description -n libudev%{?mini}1
This package contains the dynamic library libudev, which provides
access to udev device information

%package -n libudev%{?mini}-devel
Summary:        Development files for libudev
License:        LGPL-2.1-or-later
Group:          Development/Libraries/Other
Requires:       libudev%{?mini}1 = %{version}-%{release}
%if 0%{?bootstrap}
Provides:       libudev-devel = %{version}
Conflicts:      libudev1 = %{version}
Conflicts:      libudev-devel
%endif

%description -n libudev%{?mini}-devel
This package contains the development files for the library libudev, a
dynamic library, which provides access to udev device information.

%package coredump%{mini}
Summary:        Systemd tools for coredump management
License:        LGPL-2.1-or-later
Group:          System/Base
Requires:       %{name} = %{version}-%{release}
%systemd_requires
Provides:       systemd:%{_bindir}/coredumpctl
%if 0%{?bootstrap}
Conflicts:      systemd-coredump
%endif

%description coredump%{mini}
Systemd tools to store and manage coredumps.

This package contains systemd-coredump, coredumpctl.

%package container%{?mini}
Summary:        Systemd tools for container management
License:        LGPL-2.1-or-later
Group:          System/Base
Requires:       %{name} = %{version}-%{release}
%systemd_requires
Provides:       systemd:%{_bindir}/systemd-nspawn
%if 0%{?bootstrap}
Conflicts:      systemd-container
%endif

%description container%{?mini}
Systemd tools to spawn and manage containers and virtual machines.

This package contains systemd-nspawn, machinectl, systemd-machined,
and systemd-importd.

%if ! 0%{?bootstrap}
%package logger
Summary:        Journal only logging
License:        LGPL-2.1-or-later
Group:          System/Base
Provides:       syslog
Provides:       sysvinit(syslog)
Requires(post): /usr/bin/systemctl
Conflicts:      otherproviders(syslog)

%description logger
This package marks the installation to not use syslog but only the journal.

%package -n nss-systemd
Summary:        Plugin for local virtual host name resolution
License:        LGPL-2.1-or-later
Group:          System/Libraries

%description -n nss-systemd
This package contains a plugin for the Name Service Switch (NSS),
which enables resolution of all dynamically allocated service
users. (See the DynamicUser= setting in unit files.)

To activate this NSS module, you will need to include it in
/etc/nsswitch.conf, see nss-systemd(8) manpage for more details.

%package -n nss-myhostname
Summary:        Plugin for local system host name resolution
License:        LGPL-2.1-or-later
Group:          System/Libraries

%description -n nss-myhostname
This package contains a plug-in module for the Name Service Switch
(NSS), primarly providing hostname resolution for the locally
configured system hostname as returned by gethostname(2). For example,
it resolves the local hostname to locally configured IP addresses, as
well as "localhost" to 127.0.0.1/::1.

To activate this NSS module, you will need to include it in
/etc/nsswitch.conf, see nss-hostname(8) manpage for more details.
%endif

%if %{with resolved}
%package -n nss-resolve
Summary:        Plugin for local hostname resolution via systemd-resolved
License:        LGPL-2.1-or-later
Group:          System/Libraries
Requires:       %{name} = %{version}-%{release}

%description -n nss-resolve
This package contains a plug-in module for the Name Service Switch
(NSS), which enables host name resolutions via the systemd-resolved(8)
local network name resolution service. It replaces the nss-dns plug-in
module that traditionally resolves hostnames via DNS.

To activate this NSS module, you will need to include it in
/etc/nsswitch.conf, see nss-resolve(8) manpage for more details.
%endif

%if %{with machined}
%package -n nss-mymachines
Summary:        Plugin for local virtual host name resolution
License:        LGPL-2.1-or-later
Group:          System/Libraries

%description -n nss-mymachines
This package contains a plugin for the Name Service Switch (NSS),
providing host name resolution for all local containers and virtual
machines registered with systemd-machined to their respective IP
addresses. It also maps UID/GIDs ranges used by containers to useful
names.

To activate this NSS module, you will need to include it in
/etc/nsswitch.conf, see nss-mymachines(8) manpage for more details.
%endif

%if %{with journal_remote}
%package journal-remote
Summary:        Gateway for serving journal events over the network using HTTP
License:        LGPL-2.1-or-later
Group:          System/Base
Requires:       %{name} = %{version}-%{release}
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description journal-remote
This extends the journal functionality to keep a copy of logs on a
remote server by providing programs to forward journal entries over
the network, using encrypted HTTP, and to write journal files from
serialized journal contents.

This package contains systemd-journal-gatewayd,
systemd-journal-remote, and systemd-journal-upload.
%endif

%package bash-completion
Summary:        Bash completion support for systemd
License:        LGPL-2.1-or-later
Group:          System/Base
Requires:       bash-completion
BuildArch:      noarch
%if 0%{?bootstrap}
Conflicts:      systemd-bash-completion
%endif

%description bash-completion
Some systemd commands offer bash completion, but it is an optional dependency.

%prep
%setup -q -n systemd-v%{version}%{suse_version}
%autopatch -p1

%build
%if 0%{?is_opensuse}
ntp_servers=({0..3}.opensuse.pool.ntp.org)
%else
ntp_servers=({0..3}.suse.pool.ntp.org)
%endif

./autogen.sh

# keep split-usr until all packages have moved their systemd rules to /usr
%configure \
        --docdir=%{_docdir}/systemd \
        --with-pamlibdir=/%{_lib}/security \
        --with-dbuspolicydir=%{_sysconfdir}/dbus-1/system.d \
        --with-dbussessionservicedir=%{_datadir}/dbus-1/services \
        --with-dbussystemservicedir=%{_datadir}/dbus-1/system-services \
        --with-certificate-root=%{_sysconfdir}/pki/systemd \
        --with-ntp-servers="${ntp_servers[*]}" \
%if 0%{?bootstrap}
        --disable-myhostname \
        --disable-manpages \
%endif
        --enable-split-usr \
        --disable-static \
        --disable-lto \
        --disable-tests \
        --without-kill-user-processes \
        --with-default-hierarchy=hybrid \
        --with-rc-local-script-path-start=/etc/init.d/boot.local \
        --with-rc-local-script-path-stop=/etc/init.d/halt.local \
        --with-debug-shell=/bin/bash \
        --disable-smack \
        --disable-ima \
        --disable-adm-group \
        --disable-wheel-group \
        --disable-ldconfig \
        --disable-gshadow \
%if %{without networkd}
        --disable-networkd \
%endif
%if %{without machined}
        --disable-machined \
%endif
%if %{without sysvcompat}
        --with-sysvinit-path= \
        --with-sysvrcnd-path= \
%endif
%if %{without resolved}
        --disable-resolved \
%endif
        --disable-kdbus

%make_build V=e

%install
%make_install
find %{buildroot} -type f -name '*.la' -delete

# move to %{_lib}
%if ! 0%{?bootstrap}
mv %{buildroot}%{_libdir}/libnss_myhostname.so.2 %{buildroot}/%{_lib}
%else
rm %{buildroot}%{_libdir}/libnss_systemd.so*
%endif

# FIXME: these symlinks should die.
mkdir -p %{buildroot}/{sbin,lib,bin}
ln -sf %{_bindir}/udevadm %{buildroot}/sbin/udevadm
ln -sf %{_bindir}/systemd-ask-password %{buildroot}/bin/systemd-ask-password
ln -sf %{_bindir}/systemctl %{buildroot}/bin/systemctl
ln -sf %{_prefix}/lib/systemd/systemd-udevd %{buildroot}/sbin/udevd

install -m644 -D %{S:2000} %{buildroot}/%{_prefix}/lib/udev/rules.d/80-acpi-container-hotplug.rules
install -m644 -D %{S:2001} %{buildroot}/%{_prefix}/lib/udev/rules.d/99-wakeup-from-idle.rules
install -m644 -D %{S:2002} %{buildroot}/%{_prefix}/lib/udev/rules.d/80-hotplug-cpu-mem.rules

mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/sysv-convert
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/migrated

install -m0755 -D %{S:3}  %{buildroot}/%{_sbindir}/systemd-sysv-convert
install -m0755 -D %{S:12} %{buildroot}/%{_prefix}/lib/systemd/systemd-sysv-install

# Package the scripts used to fix all packaging issues. Also drop the
# "scripts-{systemd/udev}" prefix which is used because osc doesn't
# allow directory structure...
for s in %{S:100} %{S:101} %{S:102}; do
	install -m0755 -D $s %{buildroot}%{_prefix}/lib/systemd/scripts/${s#*/scripts-systemd-}
done
for s in %{S:200}; do
	install -m0755 -D $s %{buildroot}%{_prefix}/lib/udev/scripts/${s#*/scripts-udev-}
done

ln -s ../usr/lib/systemd/systemd %{buildroot}/bin/systemd
ln -s ../usr/lib/systemd/systemd %{buildroot}/sbin/init
ln -s ../usr/bin/systemctl %{buildroot}/sbin/reboot
ln -s ../usr/bin/systemctl %{buildroot}/sbin/halt
ln -s ../usr/bin/systemctl %{buildroot}/sbin/shutdown
ln -s ../usr/bin/systemctl %{buildroot}/sbin/poweroff
ln -s ../usr/bin/systemctl %{buildroot}/sbin/telinit
ln -s ../usr/bin/systemctl %{buildroot}/sbin/runlevel
rm -rf %{buildroot}/etc/systemd/system/*.target.wants

# Make sure we don't ship static enablement symlinks in /etc during
# installation, presets should be honoured instead.
rm -rf %{buildroot}/etc/systemd/system/*.target.{requires,wants}
rm -f %{buildroot}/etc/systemd/system/default.target

# Overwrite /etc/pam.d/systemd-user shipped by upstream with one
# customized for openSUSE distros.
install -m0644 %{S:2} %{buildroot}%{_sysconfdir}/pam.d/

# Remove tmp.mount from the unit search path as /tmp doesn't use tmpfs
# by default on SUSE distros. We still keep a copy in /var for those
# who want to switch to tmpfs: it's still can be copied in /etc.
rm %{buildroot}/%{_prefix}/lib/systemd/system/local-fs.target.wants/tmp.mount
mv %{buildroot}/%{_prefix}/lib/systemd/system/tmp.mount %{buildroot}/%{_datadir}/systemd/

# don't enable wall ask password service, it spams every console (bnc#747783)
rm %{buildroot}%{_prefix}/lib/systemd/system/multi-user.target.wants/systemd-ask-password-wall.path

# Remove .so file for the shared library, it's not supposed to be
# used.
rm %{buildroot}%{_libexecdir}/systemd/libsystemd-shared.so

# do not ship sysctl defaults in systemd package, will be part of
# aaa_base (in procps for now)
rm -f %{buildroot}%{_prefix}/lib/sysctl.d/50-default.conf

# since v207 /etc/sysctl.conf is no longer parsed (commit
# 04bf3c1a60d82791), however backward compatibility is provided by
# /usr/lib/sysctl.d/99-sysctl.conf.
ln -s ../../../etc/sysctl.conf %{buildroot}%{_sysctldir}/99-sysctl.conf

# The definition of the basic users/groups are defined by system-user
# on SUSE (bsc#1006978).
rm -f %{buildroot}%{_prefix}/lib/sysusers.d/basic.conf

# Remove README file in init.d as (SUSE) rpm requires executable files
# in this directory... oh well.
rm -f %{buildroot}/etc/init.d/README

# journal-upload is built if libcurl is installed which can happen
# when importd is enabled (whereas journal_remote is not).
%if ! %{with journal_remote}
rm -f %{buildroot}%{_sysconfdir}/systemd/journal-upload.conf
rm -f %{buildroot}%{_prefix}/lib/systemd/systemd-journal-upload
rm -f %{buildroot}%{_prefix}/lib/systemd/system/systemd-journal-upload.*
%endif

# legacy link
ln -s /usr/lib/udev %{buildroot}/lib/udev

# Create the /var/log/journal directory to change the volatile journal
# to a persistent one
mkdir -p %{buildroot}%{_localstatedir}/log/journal/

# This dir must be owned (and thus created) by systemd otherwise the
# build system will complain. This is odd since we simply own a ghost
# file in it...
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d

# Make sure directories in /var exist
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/coredump
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/catalog
# Create ghost databases
touch %{buildroot}%{_localstatedir}/lib/systemd/catalog/database
touch %{buildroot}%{_sysconfdir}/udev/hwdb.bin

# Make sure the NTP units dir exists
mkdir -p %{buildroot}%{_prefix}/lib/systemd/ntp-units.d/

# Make sure the shutdown/sleep drop-in dirs exist
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-shutdown/
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-sleep/

# Make sure these directories are properly owned
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/basic.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/default.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/dbus.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/halt.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/kexec.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/poweroff.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/reboot.target.wants
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/shutdown.target.wants

# Make sure the generator directories are created and properly owned.
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-generators
mkdir -p %{buildroot}%{_prefix}/lib/systemd/user-generators
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset
mkdir -p %{buildroot}%{_prefix}/lib/systemd/user-preset

# create drop-in to prevent tty1 to be cleared (bnc#804158)
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/getty@tty1.service.d/
cat << EOF > %{buildroot}%{_prefix}/lib/systemd/system/getty@tty1.service.d/noclear.conf
[Service]
# ensure tty1 isn't cleared (bnc#804158)
TTYVTDisallocate=no
EOF

# create drop-in to prevent delegate=yes for root user (bsc#954765,
# bnc#953241, fate#320421)
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/user@0.service.d/
cat >%{buildroot}%{_prefix}/lib/systemd/system/user@0.service.d/nodelagate.conf <<EOF
[Service]
Delegate=no
EOF

# Remove TasksMax limit for both system services and users (jsc#SLE-10123)
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system.conf.d
cat >%{buildroot}%{_prefix}/lib/systemd/system.conf.d/20-suse-defaults.conf <<EOF
[Manager]
DefaultTasksMax=infinity
EOF

mkdir -p %{buildroot}%{_prefix}/lib/systemd/system/user-.slice.d
cat >%{buildroot}%{_prefix}/lib/systemd/system/user-.slice.d/20-suse-defaults.conf <<EOF
[Slice]
TasksMax=infinity
EOF

# ensure after.local wrapper is called
install -m 644 %{S:11} %{buildroot}/%{_prefix}/lib/systemd/system/
ln -s ../after-local.service %{buildroot}/%{_prefix}/lib/systemd/system/multi-user.target.wants/

mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/backlight
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/random-seed

%fdupes -s %{buildroot}%{_mandir}

# packaged in systemd-rpm-macros
rm -f %{buildroot}/%{_prefix}/lib/rpm/macros.d/macros.systemd

# Make sure to disable all services by default. The Suse branding
# presets package takes care of defining the right policies.
rm -f %{buildroot}%{_prefix}/lib/systemd/system-preset/*.preset
echo 'disable *' >%{buildroot}%{_prefix}/lib/systemd/system-preset/99-default.preset
echo 'disable *' >%{buildroot}%{_prefix}/lib/systemd/user-preset/99-default.preset

# Add entries for xkeyboard-config converted keymaps; mappings, which
# already exist in original systemd mapping table are being ignored
# though, i.e. not overwritten; needed as long as YaST uses console
# keymaps internally and calls localectl to convert from vconsole to
# X11 keymaps. Ideally YaST should switch to X11 layout names (the
# mapping table wouldn't be needed since each X11 keymap has a
# generated xkbd keymap) and let localectl initialize
# /etc/vconsole.conf and /etc/X11/xorg.conf.d/00-keyboard.conf
# (FATE#319454).
if [ -f /usr/share/systemd/kbd-model-map.xkb-generated ]; then
        cat /usr/share/systemd/kbd-model-map.xkb-generated \
                >>%{buildroot}%{_datarootdir}/systemd/kbd-model-map
fi

# kbd-model-map.legacy is used to provide mapping for legacy keymaps,
# which may still be used by yast.
cat %{S:14} >>%{buildroot}%{_datarootdir}/systemd/kbd-model-map

%find_lang systemd

%pre
# Build of installation images uses an hard coded list of some
# packages with a %pre that needs to be run during the
# build. Unfortunately, systemd in one of them so we need to keep this
# section even if it's empty.
if [ $1 -gt 1 ] ; then
        case "$(systemctl show -pFragmentPath tmp.mount)" in
        FragmentPath=/usr/lib/systemd/system/tmp.mount)
                ln -sf %{_datadir}/systemd/tmp.mount /etc/systemd/system/ || :
        esac
fi

%post
# Make /etc/machine-id an empty file during package installation. On
# the first boot, machine-id is initialized and either committed (if
# /etc/ is writable) or the system/image runs with a transient machine
# ID, that changes on each boot (if the image is read-only). This is
# especially important for appliance builds to avoid an identical
# machine ID in all images.
if [ $1 -eq 1 ]; then
	touch     %{_sysconfdir}/machine-id
	chmod 444 %{_sysconfdir}/machine-id
fi

# /etc/machine-id might have been created writeable incorrectly
# (boo#1092269).
if [ "$(stat -c%a %{_sysconfdir}/machine-id)" != 444 ]; then
        echo "Incorrect file mode bits for /etc/machine-id which should be 0444, fixing..."
        chmod 444 %{_sysconfdir}/machine-id
fi

%sysusers_create /usr/lib/sysusers.d/systemd.conf
%if ! 0%{?bootstrap}
pam-config -a --systemd || :
%endif
[ -e %{_localstatedir}/lib/random-seed ] && mv %{_localstatedir}/lib/random-seed %{_localstatedir}/lib/systemd/ || :
/usr/lib/systemd/systemd-random-seed save || :

if [ $1 -gt 1 ]; then
        systemctl daemon-reexec || :
fi

%journal_catalog_update
%tmpfiles_create

# Create default config in /etc at first install.
# Later package updates should not overwrite these settings.
if [ $1 -eq 1 ]; then
        # Enable systemd services according to the distro defaults.
        # Note: systemctl might abort prematurely if it fails on one
        # unit.
        systemctl preset machines.target  || :
        systemctl preset remote-fs.target || :
        systemctl preset remote-cryptsetup.target || :
        systemctl preset getty@.service   || :
        systemctl preset systemd-timesyncd.service || :
%if %{with networkd}
        systemctl preset systemd-networkd.service || :
        systemctl preset systemd-networkd-wait-online.service || :
%endif
%if %{with resolved}
        systemctl preset systemd-resolved.service  || :
%endif
fi >/dev/null

# v228 wrongly set world writable suid root permissions on timestamp
# files used by permanent timers. Fix the timestamps that might have
# been created by the affected versions of systemd (bsc#1020601).
for stamp in $(ls /var/lib/systemd/timers/stamp-*.timer 2>/dev/null); do
        chmod 0644 $stamp
done

# Same for user lingering created by logind.
for username in $(ls /var/lib/systemd/linger/* 2>/dev/null); do
        chmod 0644 $username
done

# This includes all hacks needed when upgrading from SysV.
%{_prefix}/lib/systemd/scripts/upgrade-from-pre-210.sh || :

# Migrate the i18n settings that could be previously configured in
# /etc/sysconfig but now defined in the systemd official places
# (/etc/locale.conf, /etc/vconsole.conf, etc...). This is done only
# once during either installation or update. It's done during package
# installation because of migration from SLE11.
test -e %{_prefix}/lib/systemd/scripts/.migrate-sysconfig-i18n.sh~done || {
        %{_prefix}/lib/systemd/scripts/migrate-sysconfig-i18n.sh &&
        touch %{_prefix}/lib/systemd/scripts/.migrate-sysconfig-i18n.sh~done || :
}

%postun
%systemd_postun
# Avoid restarting logind until fixed upstream (issue #1163)
%systemd_postun_with_restart systemd-journald.service
%systemd_postun_with_restart systemd-timesyncd.service
%if %{with networkd}
%systemd_postun_with_restart systemd-networkd.service
%endif
%if %{with resolved}
%systemd_postun_with_restart systemd-resolved.service
%endif

%pre -n udev%{?mini}
# New installations uses the last compat symlink generation number
# (currently at 2), which basically disables all compat symlinks. On
# old systems, the file doesn't exist. This is equivalent to
# generation #1, which enables the creation of all compat symlinks.
if [ $1 -eq 1 ]; then
	echo "COMPAT_SYMLINK_GENERATION=2">/usr/lib/udev/compat-symlink-generation
fi

%post -n udev%{?mini}
%regenerate_initrd_post
%udev_hwdb_update

# add KERNEL name match to existing persistent net rules
sed -ri '/KERNEL/ ! { s/NAME="(eth|wlan|ath)([0-9]+)"/KERNEL=="\1*", NAME="\1\2"/}' \
    /etc/udev/rules.d/70-persistent-net.rules 2>/dev/null || :

# cleanup old stuff
rm -f /etc/sysconfig/udev
rm -f /etc/udev/rules.d/{20,55,65}-cdrom.rules

%postun -n udev%{?mini}
%regenerate_initrd_post
systemctl daemon-reload || :
# On package update: the restart of the socket units will probably
# fail as the daemon is most likely running. It's not really an issue
# since we restart systemd-udevd right after and that will pull in the
# socket units again. We should be informed at that time if something
# really went wrong the first time we started the socket units.
%systemd_postun_with_restart systemd-udevd-{control,kernel}.socket 2>/dev/null
%systemd_postun_with_restart systemd-udevd.service

%posttrans -n udev%{?mini}
%regenerate_initrd_posttrans
%{_prefix}/lib/udev/scripts/convert-lib-udev-path.sh || :

%post -n libudev%{?mini}1 -p /sbin/ldconfig
%post -n libsystemd0%{?mini} -p /sbin/ldconfig

%postun -n libudev%{?mini}1 -p /sbin/ldconfig
%postun -n libsystemd0%{?mini} -p /sbin/ldconfig

%post container%{?mini}
%tmpfiles_create systemd-nspawn.conf
if [ $1 -gt 1 ]; then
	# Convert /var/lib/machines subvolume to make it suitable for
	# rollbacks, if needed. See bsc#992573. The installer has been fixed
	# to create it at installation time.
	#
	# The convertion might only be problematic for openSUSE distros
	# (TW/Factory) where previous versions had already created the
	# subvolume at the wrong place (via tmpfiles for example) and user
	# started to populate and use it. In this case we'll let the user fix
	# it manually.
	#
	# For SLE12 this subvolume was only introduced during the upgrade from
	# v210 to v228 when we added this workaround. Note that the subvolume
	# is still created at the wrong place due to the call to
	# tmpfiles_create macro previously however it's empty so there
	# shouldn't be any issues.
	%{_prefix}/lib/systemd/scripts/fix-machines-btrfs-subvol.sh || :
fi

%if ! 0%{?bootstrap}
%post logger
%tmpfiles_create -- --prefix=%{_localstatedir}/log/journal/
if [ "$1" -eq 1 ]; then
        # tell journal to start logging on disk if directory didn't exist before
        systemctl --no-block restart systemd-journal-flush.service >/dev/null || :
fi

%post   -n nss-myhostname -p /sbin/ldconfig
%postun -n nss-myhostname -p /sbin/ldconfig

%post   -n nss-systemd -p /sbin/ldconfig
%postun -n nss-systemd -p /sbin/ldconfig
%endif

%if %{with resolved}
%post   -n nss-resolve -p /sbin/ldconfig
%postun -n nss-resolve -p /sbin/ldconfig
%endif

%if %{with machined}
%post   -n nss-mymachines -p /sbin/ldconfig
%postun -n nss-mymachines -p /sbin/ldconfig
%endif

%if %{with journal_remote}
%pre journal-remote
%service_add_pre systemd-journal-gatewayd.socket systemd-journal-gatewayd.service
%service_add_pre systemd-journal-remote.socket systemd-journal-remote.service
%service_add_pre systemd-journal-upload.service

%post journal-remote
%sysusers_create %{_libexecdir}/sysusers.d/systemd-remote.conf
%tmpfiles_create %{_libexecdir}/tmpfiles.d/systemd-remote.conf
%service_add_post systemd-journal-gatewayd.socket systemd-journal-gatewayd.service
%service_add_post systemd-journal-remote.socket systemd-journal-remote.service
%service_add_post systemd-journal-upload.service

%preun  journal-remote
%service_del_preun systemd-journal-gatewayd.socket systemd-journal-gatewayd.service
%service_del_preun systemd-journal-remote.socket systemd-journal-remote.service
%service_del_preun systemd-journal-upload.service

%postun journal-remote
%service_del_postun systemd-journal-gatewayd.socket systemd-journal-gatewayd.service
%service_del_postun systemd-journal-remote.socket systemd-journal-remote.service
%service_del_postun systemd-journal-upload.service
%endif

%clean

%files -f systemd.lang
%defattr(-,root,root)
/bin/systemd
/bin/systemd-ask-password
/bin/systemctl
%if %{with networkd}
%{_bindir}/networkctl
%endif
%{_bindir}/busctl
%{_bindir}/bootctl
%{_bindir}/kernel-install
%{_bindir}/hostnamectl
%{_bindir}/localectl
%{_bindir}/systemctl
%{_bindir}/systemd-analyze
%{_bindir}/systemd-delta
%{_bindir}/systemd-escape
%{_bindir}/systemd-firstboot
%{_bindir}/systemd-path
%{_bindir}/systemd-sysusers
%{_bindir}/systemd-mount
%{_bindir}/systemd-umount
%{_bindir}/systemd-notify
%{_bindir}/systemd-run
%{_bindir}/journalctl
%{_bindir}/systemd-ask-password
%{_bindir}/loginctl
%{_bindir}/systemd-inhibit
%{_bindir}/systemd-tty-ask-password-agent
%{_bindir}/systemd-tmpfiles
%{_bindir}/systemd-machine-id-setup
%if %{with resolved}
%{_bindir}/systemd-resolve
%endif
%{_bindir}/systemd-socket-activate
%{_bindir}/systemd-stdio-bridge
%{_bindir}/systemd-detect-virt
%{_bindir}/timedatectl
%{_sbindir}/systemd-sysv-convert
%{_bindir}/systemd-cgls
%{_bindir}/systemd-cgtop
%{_bindir}/systemd-cat
%dir %{_prefix}/lib/kernel
%dir %{_prefix}/lib/kernel/install.d
%{_prefix}/lib/kernel/install.d/50-depmod.install
%{_prefix}/lib/kernel/install.d/90-loaderentry.install
%dir %{_prefix}/lib/systemd
%dir %{_prefix}/lib/systemd/user
%dir %{_prefix}/lib/systemd/system
%if %{with journal_remote}
%exclude %{_prefix}/lib/systemd/systemd-journal-gatewayd
%exclude %{_prefix}/lib/systemd/systemd-journal-remote
%exclude %{_prefix}/lib/systemd/systemd-journal-upload
%exclude %{_prefix}/lib/systemd/system/systemd-journal-gatewayd.*
%exclude %{_prefix}/lib/systemd/system/systemd-journal-remote.*
%exclude %{_prefix}/lib/systemd/system/systemd-journal-upload.*
%endif
%exclude %{_prefix}/lib/systemd/systemd-coredump
%exclude %{_prefix}/lib/systemd/systemd-udevd
%exclude %{_prefix}/lib/systemd/system/systemd-udev*.*
%exclude %{_prefix}/lib/systemd/system/*.target.wants/systemd-udev*.*
%exclude %{_prefix}/lib/systemd/system/initrd-udevadm-cleanup-db.service
%exclude %{_unitdir}/systemd-nspawn@.service
%exclude %{_unitdir}/systemd-coredump*
%exclude %{_unitdir}/sockets.target.wants/systemd-coredump.socket
%if %{with machined}
%exclude %{_prefix}/lib/systemd/systemd-machined
%exclude %{_unitdir}/systemd-machined.service
%exclude %{_unitdir}/dbus-org.freedesktop.machine1.service
%exclude %{_unitdir}/var-lib-machines.mount
%exclude %{_unitdir}/machine.slice
%exclude %{_unitdir}/machines.target.wants
%exclude %{_unitdir}/*.target.wants/var-lib-machines.mount
%endif
%if %{with importd}
%exclude %{_prefix}/lib/systemd/systemd-import*
%exclude %{_prefix}/lib/systemd/systemd-pull
%exclude %{_prefix}/lib/systemd/import-pubring.gpg
%exclude %{_unitdir}/systemd-importd.service
%exclude %{_unitdir}/dbus-org.freedesktop.import1.service
%endif

%{_prefix}/lib/systemd/system.conf.d
%{_prefix}/lib/systemd/system/*.automount
%{_prefix}/lib/systemd/system/*.service
%{_prefix}/lib/systemd/system/*.slice
%{_prefix}/lib/systemd/system/*.target
%{_prefix}/lib/systemd/system/*.mount
%{_prefix}/lib/systemd/system/*.timer
%{_prefix}/lib/systemd/system/*.socket
%{_prefix}/lib/systemd/system/*.wants
%{_prefix}/lib/systemd/system/*.path
%{_prefix}/lib/systemd/system/user-.slice.d/
%{_prefix}/lib/systemd/user/*.target
%{_prefix}/lib/systemd/user/*.service
%{_prefix}/lib/systemd/systemd-*
%{_prefix}/lib/systemd/systemd
%{_prefix}/lib/systemd/libsystemd-shared-*.so
%if %{with resolved}
%{_prefix}/lib/systemd/resolv.conf
%endif
%{_prefix}/lib/systemd/scripts
%exclude %{_prefix}/lib/systemd/scripts/fix-machines-btrfs-subvol.sh
%dir %{_prefix}/lib/systemd/catalog
%{_prefix}/lib/systemd/catalog/systemd.catalog
%{_prefix}/lib/systemd/catalog/systemd.*.catalog
%{_prefix}/lib/systemd/system-preset
%{_prefix}/lib/systemd/user-preset
%{_prefix}/lib/systemd/system-generators
%{_prefix}/lib/systemd/user-generators
%{_prefix}/lib/systemd/user-environment-generators
%dir %{_prefix}/lib/systemd/ntp-units.d/
%dir %{_prefix}/lib/systemd/system-shutdown/
%dir %{_prefix}/lib/systemd/system-sleep/
%dir %{_prefix}/lib/systemd/system/getty@tty1.service.d
%dir %{_prefix}/lib/systemd/system/user@0.service.d
%{_prefix}/lib/systemd/system/getty@tty1.service.d/noclear.conf
%{_prefix}/lib/systemd/system/user@0.service.d/nodelagate.conf
/%{_lib}/security/pam_systemd.so

%if %{with gnuefi}
%dir %{_prefix}/lib/systemd/boot
%dir %{_prefix}/lib/systemd/boot/efi
%{_prefix}/lib/systemd/boot/efi/*.efi
%{_prefix}/lib/systemd/boot/efi/*.stub
%endif

%dir %{_libexecdir}/modules-load.d
%dir %{_sysconfdir}/modules-load.d

%{_libexecdir}/sysusers.d/
%exclude %{_libexecdir}/sysusers.d/systemd-remote.conf

%dir %{_sysconfdir}/tmpfiles.d
%{_libexecdir}/tmpfiles.d/
%exclude %{_libexecdir}/tmpfiles.d/systemd-remote.conf
%exclude %{_libexecdir}/tmpfiles.d/systemd-nspawn.conf

%{_libexecdir}/environment.d/

%dir %{_libexecdir}/binfmt.d
%dir %{_sysconfdir}/binfmt.d

%dir %{_libexecdir}/sysctl.d
%dir %{_sysconfdir}/sysctl.d
%{_sysctldir}/99-sysctl.conf

%dir %{_sysconfdir}/systemd/network
%{_prefix}/lib/systemd/network/80-container-host0.network

%dir %{_sysconfdir}/X11/xinit
%dir %{_sysconfdir}/X11/xinit/xinitrc.d
%dir %{_sysconfdir}/X11/xorg.conf.d
%dir %{_sysconfdir}/dbus-1
%dir %{_sysconfdir}/dbus-1/system.d
%dir %{_sysconfdir}/systemd
%dir %{_sysconfdir}/systemd/network
%dir %{_sysconfdir}/systemd/system
%dir %{_sysconfdir}/systemd/user
%dir %{_sysconfdir}/xdg/systemd
%{_sysconfdir}/xdg/systemd/user
%{_sysconfdir}/X11/xinit/xinitrc.d/50-systemd-user.sh

%config(noreplace) %{_sysconfdir}/pam.d/systemd-user
%config(noreplace) %{_sysconfdir}/systemd/timesyncd.conf
%config(noreplace) %{_sysconfdir}/systemd/system.conf
%config(noreplace) %{_sysconfdir}/systemd/logind.conf
%config(noreplace) %{_sysconfdir}/systemd/journald.conf
%config(noreplace) %{_sysconfdir}/systemd/user.conf
%if %{with resolved}
%config(noreplace) %{_sysconfdir}/systemd/resolved.conf
%endif
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.locale1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.login1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.systemd1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.hostname1.conf
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.timedate1.conf
%if %{with networkd}
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.network1.conf
%endif
%if %{with resolved}
%{_sysconfdir}/systemd/system/dbus-org.freedesktop.resolve1.service
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.freedesktop.resolve1.conf
%endif

# Some files created by us.
%ghost %config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/00-keyboard.conf
%ghost %config(noreplace) %{_sysconfdir}/vconsole.conf
%ghost %config(noreplace) %{_sysconfdir}/locale.conf
%ghost %config(noreplace) %{_sysconfdir}/machine-id
%ghost %config(noreplace) %{_sysconfdir}/machine-info
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel2.target
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel3.target
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel4.target
%ghost %config(noreplace) %{_sysconfdir}/systemd/system/runlevel5.target

%{_datadir}/systemd
%{_datadir}/factory

%if %{with journal_remote}
%exclude %{_datadir}/systemd/gatewayd
%endif

%dir %{_datadir}/dbus-1
%dir %{_datadir}/dbus-1/services
%dir %{_datadir}/dbus-1/system-services
%{_datadir}/dbus-1/services/org.freedesktop.systemd1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.systemd1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.locale1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.login1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.hostname1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.timedate1.service
%if %{with networkd}
%{_datadir}/dbus-1/system-services/org.freedesktop.network1.service
%endif
%if %{with resolved}
%{_datadir}/dbus-1/system-services/org.freedesktop.resolve1.service
%endif

%dir %{_datadir}/polkit-1
%dir %{_datadir}/polkit-1/actions
%{_datadir}/polkit-1/actions/org.freedesktop.systemd1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.hostname1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.locale1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.timedate1.policy
%{_datadir}/polkit-1/actions/org.freedesktop.login1.policy
%if %{with networkd}
%{_datadir}/polkit-1/rules.d/systemd-networkd.rules
%endif

%if ! 0%{?bootstrap}
%{_mandir}/man1/[a-rt-z]*ctl.1*
%{_mandir}/man1/systemc*.1*
%{_mandir}/man1/systemd*.1*
%{_mandir}/man5/[a-tv-z]*
%{_mandir}/man5/user*
%{_mandir}/man7/[bdfks]*
%{_mandir}/man8/kern*
%{_mandir}/man8/pam_*
%{_mandir}/man8/systemd-[a-gik-tv]*
%{_mandir}/man8/systemd-h[aioy]*
%{_mandir}/man8/systemd-journald*
%{_mandir}/man8/systemd-u[ps]*
%{_mandir}/man8/30-systemd-environment-d-generator.*
%exclude %{_mandir}/man1/coredumpctl*
%exclude %{_mandir}/man5/coredump.conf*
%exclude %{_mandir}/man8/systemd-coredump*
%exclude %{_mandir}/man*/*nspawn*
%if %{with machined}
%exclude %{_mandir}/man*/machinectl*
%exclude %{_mandir}/man*/systemd-machined*
%endif
%if %{with importd}
%exclude %{_mandir}/man*/systemd-importd*
%endif
%endif
%{_docdir}/systemd

%{_prefix}/lib/udev/rules.d/70-uaccess.rules
%{_prefix}/lib/udev/rules.d/71-seat.rules
%{_prefix}/lib/udev/rules.d/73-seat-late.rules
%{_prefix}/lib/udev/rules.d/99-systemd.rules
%dir %{_localstatedir}/lib/systemd
%dir %{_localstatedir}/lib/systemd/sysv-convert
%dir %{_localstatedir}/lib/systemd/migrated
%dir %{_localstatedir}/lib/systemd/catalog
%ghost %{_localstatedir}/lib/systemd/catalog/database
%ghost %{_localstatedir}/lib/systemd/backlight
%ghost %{_localstatedir}/lib/systemd/random-seed
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/*
%{_datadir}/pkgconfig/systemd.pc

%files devel
%defattr(-,root,root,-)
%{_libdir}/libsystemd.so
%{_libdir}/pkgconfig/libsystemd.pc
%{_includedir}/systemd/
%if ! 0%{?bootstrap}
%{_mandir}/man3/SD*.3*
%{_mandir}/man3/sd*.3*
%endif

%files sysvinit
%defattr(-,root,root,-)
/sbin/init
/sbin/reboot
/sbin/halt
/sbin/shutdown
/sbin/poweroff
/sbin/telinit
/sbin/runlevel
%if ! 0%{?bootstrap}
%{_mandir}/man1/init.1*
%{_mandir}/man8/halt.8*
%{_mandir}/man8/reboot.8*
%{_mandir}/man8/shutdown.8*
%{_mandir}/man8/poweroff.8*
%{_mandir}/man8/telinit.8*
%{_mandir}/man8/runlevel.8*
%endif

%files -n udev%{?mini}
%defattr(-,root,root)
/sbin/udevd
/sbin/udevadm
# keep for compatibility
%ghost /lib/udev
%{_bindir}/udevadm
%{_bindir}/systemd-hwdb
%dir %{_prefix}/lib/udev/
%{_prefix}/lib/udev/ata_id
%{_prefix}/lib/udev/path_id_compat
%{_prefix}/lib/udev/cdrom_id
%{_prefix}/lib/udev/collect
%{_prefix}/lib/udev/mtd_probe
%{_prefix}/lib/udev/scsi_id
%{_prefix}/lib/udev/v4l_id
%ghost %{_prefix}/lib/udev/compat-symlink-generation
%{_prefix}/lib/udev/rule_generator.functions
%{_prefix}/lib/udev/write_net_rules
%dir %{_prefix}/lib/udev/rules.d/
%exclude %{_prefix}/lib/udev/rules.d/70-uaccess.rules
%exclude %{_prefix}/lib/udev/rules.d/71-seat.rules
%exclude %{_prefix}/lib/udev/rules.d/73-seat-late.rules
%exclude %{_prefix}/lib/udev/rules.d/99-systemd.rules
%{_prefix}/lib/udev/rules.d/*.rules
%{_prefix}/lib/udev/hwdb.d/
%{_prefix}/lib/udev/scripts/
%dir %{_sysconfdir}/udev/
%dir %{_sysconfdir}/udev/rules.d/
%ghost %{_sysconfdir}/udev/hwdb.bin
%config(noreplace) %{_sysconfdir}/udev/udev.conf
%if ! 0%{?bootstrap}
%{_mandir}/man5/udev*
%{_mandir}/man7/hwdb*
%{_mandir}/man7/udev*
%{_mandir}/man8/systemd-hwdb*
%{_mandir}/man8/systemd-udev*
%{_mandir}/man8/udev*
%endif
%dir %{_prefix}/lib/systemd/system
%{_prefix}/lib/systemd/systemd-udevd
%{_prefix}/lib/systemd/system/systemd-udev*.service
%{_prefix}/lib/systemd/system/systemd-udevd*.socket
%{_prefix}/lib/systemd/system/initrd-udevadm-cleanup-db.service
%dir %{_prefix}/lib/systemd/system/sysinit.target.wants
%{_prefix}/lib/systemd/system/sysinit.target.wants/systemd-udev*.service
%dir %{_prefix}/lib/systemd/system/sockets.target.wants
%{_prefix}/lib/systemd/system/sockets.target.wants/systemd-udev*.socket
%dir %{_prefix}/lib/systemd/network
%{_prefix}/lib/systemd/network/99-default.link
%{_datadir}/pkgconfig/udev.pc

%files -n libsystemd0%{?mini}
%defattr(-,root,root)
%{_libdir}/libsystemd.so.*

%files -n libudev%{?mini}1
%defattr(-,root,root)
%{_libdir}/libudev.so.*

%files -n libudev%{?mini}-devel
%defattr(-,root,root)
%{_includedir}/libudev.h
%{_libdir}/libudev.so
%{_libdir}/pkgconfig/libudev.pc
%if ! 0%{?bootstrap}
%{_mandir}/man3/*udev*.3*
%endif

%files coredump%{?mini}
%defattr(-,root,root)
%{_bindir}/coredumpctl
%{_prefix}/lib/systemd/systemd-coredump
%{_unitdir}/systemd-coredump*
%{_unitdir}/sockets.target.wants/systemd-coredump.socket
%{_sysctldir}/50-coredump.conf
%config(noreplace) %{_sysconfdir}/systemd/coredump.conf
%dir %{_localstatedir}/lib/systemd/coredump
%if ! 0%{?bootstrap}
%{_mandir}/man1/coredumpctl*
%{_mandir}/man5/coredump.conf*
%{_mandir}/man8/systemd-coredump*
%endif

%files container%{?mini}
%defattr(-,root,root)
%{_bindir}/systemd-nspawn
%{_unitdir}/systemd-nspawn@.service
%{_tmpfilesdir}/systemd-nspawn.conf
%{_prefix}/lib/systemd/network/80-container-ve.network
%{_prefix}/lib/systemd/network/80-container-vz.network
%if %{with machined}
%{_bindir}/machinectl
%{_prefix}/lib/systemd/systemd-machined
%{_unitdir}/systemd-machined.service
%{_unitdir}/dbus-org.freedesktop.machine1.service
%{_unitdir}/var-lib-machines.mount
%{_unitdir}/machine.slice
%{_unitdir}/machines.target.wants
%{_unitdir}/*.target.wants/var-lib-machines.mount
%{_prefix}/lib/systemd/scripts/fix-machines-btrfs-subvol.sh
%{_datadir}/dbus-1/system-services/org.freedesktop.machine1.service
%{_datadir}/polkit-1/actions/org.freedesktop.machine1.policy
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.machine1.conf
%endif
%if %{with importd}
%{_prefix}/lib/systemd/systemd-import*
%{_prefix}/lib/systemd/systemd-pull
%{_prefix}/lib/systemd/import-pubring.gpg
%{_unitdir}/systemd-importd.service
%{_unitdir}/dbus-org.freedesktop.import1.service
%{_datadir}/dbus-1/system-services/org.freedesktop.import1.service
%{_datadir}/polkit-1/actions/org.freedesktop.import1.policy
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.import1.conf
%endif
%if ! 0%{?bootstrap}
%{_mandir}/man*/*nspawn*
%if %{with machined}
%{_mandir}/man*/machinectl*
%{_mandir}/man*/systemd-machined*
%endif
%if %{with importd}
%{_mandir}/man*/systemd-importd*
%endif

%files logger
%defattr(-,root,root)
%dir %attr(2755,root,systemd-journal) %{_localstatedir}/log/journal/
%doc %{_localstatedir}/log/README

%files -n nss-myhostname
%defattr(-, root, root)
/%{_lib}/*nss_myhostname*
%{_mandir}/man8/libnss_myhostname.*
%{_mandir}/man8/nss-myhostname.*

%files -n nss-systemd
%defattr(-, root, root)
%{_libdir}/libnss_systemd.so*
%{_mandir}/man8/libnss_systemd.so.*
%{_mandir}/man8/nss-systemd.*
%endif

%if %{with resolved}
%files -n nss-resolve
%defattr(-, root, root)
%{_libdir}/libnss_resolve.so.2
%{_mandir}/man8/libnss_resolve.*
%{_mandir}/man8/nss-resolve.*
%endif

%if %{with machined}
%files -n nss-mymachines
%defattr(-,root,root)
%{_libdir}/libnss_mymachines.so*
%{_mandir}/man8/libnss_mymachines.*
%{_mandir}/man8/nss-mymachines.*
%endif

%if %{with journal_remote}
%files journal-remote
%defattr(-, root, root)
%config(noreplace) %{_sysconfdir}/systemd/journal-remote.conf
%config(noreplace) %{_sysconfdir}/systemd/journal-upload.conf
%{_prefix}/lib/systemd/system/systemd-journal-gatewayd.*
%{_prefix}/lib/systemd/system/systemd-journal-remote.*
%{_prefix}/lib/systemd/system/systemd-journal-upload.*
%{_prefix}/lib/systemd/systemd-journal-gatewayd
%{_prefix}/lib/systemd/systemd-journal-remote
%{_prefix}/lib/systemd/systemd-journal-upload
%{_libexecdir}/sysusers.d/systemd-remote.conf
%{_libexecdir}/tmpfiles.d/systemd-remote.conf
%{_mandir}/man8/systemd-journal-gatewayd.*
%{_mandir}/man8/systemd-journal-remote.*
%{_mandir}/man8/systemd-journal-upload.*
%{_datadir}/systemd/gatewayd
%endif

%files bash-completion
%defattr(-,root,root,-)
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/*

%changelog
