#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="systemd-nspawn smoke test"
TEST_NO_NSPAWN=1
SKIP_INITRD=yes
. $TEST_BASE_DIR/test-functions

test_run() {
    ret=1
    systemctl daemon-reload
    systemctl start testsuite.service || return 1
    systemctl status --full testsuite.service
    if [ -z "$TEST_NO_NSPAWN" ]; then
        if run_nspawn; then
            check_result_nspawn || return 1
        else
            dwarn "can't run systemd-nspawn, skipping"
        fi
    fi
    test -s /failed && ret=$(($ret+1))
    [[ -e /testok ]] && ret=0
    return $ret
}

test_setup() {
    mkdir -p $TESTDIR/root
    initdir=$TESTDIR/root
    STRIP_BINARIES=no

    # Create what will eventually be our root filesystem onto an overlay
    (
        LOG_LEVEL=5

        setup_basic_environment
        dracut_install busybox chmod rmdir unshare

	cp create-busybox-container /

        /create-busybox-container /nc-container
        initdir="/nc-container" dracut_install nc

        # setup the testsuite service
        cat >$initdir/etc/systemd/system/testsuite.service <<EOF
[Unit]
Description=Testsuite service
After=multi-user.target

[Service]
ExecStart=$initdir/test-nspawn.sh
ExecStartPost=/bin/sh -x -c 'echo -e "\nfailed:" > /failed; systemctl --state=failed --no-pager >> /failed; echo -e "\ntestresult:\nOK" > /testok'
Type=oneshot
EOF

        cat >$initdir/test-nspawn.sh <<'EOF'
#!/bin/bash
set -x
set -e
set -u
set -o pipefail

export SYSTEMD_LOG_LEVEL=debug

# check cgroup-v2
is_v2_supported=no
mkdir -p /tmp/cgroup2
if mount -t cgroup2 cgroup2 /tmp/cgroup2; then
    is_v2_supported=yes
    umount /tmp/cgroup2
fi
rmdir /tmp/cgroup2

# check cgroup namespaces
is_cgns_supported=no
if [[ -f /proc/1/ns/cgroup ]]; then
    is_cgns_supported=yes
fi

is_user_ns_supported=no
if unshare -U sh -c :; then
    is_user_ns_supported=yes
fi

function check_bind_tmp_path {
    # https://github.com/systemd/systemd/issues/4789
    local _root="/var/lib/machines/bind-tmp-path"
    /create-busybox-container "$_root"
    >/tmp/bind
    systemd-nspawn --bind /lib64 --register=no -D "$_root" --bind=/tmp/bind /bin/sh -c 'test -e /tmp/bind'
}

function check_notification_socket {
    # https://github.com/systemd/systemd/issues/4944
    local _cmd='echo a | $(busybox which nc) -U -u -w 1 /run/systemd/nspawn/notify'
    systemd-nspawn --bind /lib64 --register=no -D /nc-container /bin/sh -x -c "$_cmd"
    systemd-nspawn --bind /lib64 --register=no -D /nc-container -U /bin/sh -x -c "$_cmd"
}

function run {
    if [[ "$1" = "yes" && "$is_v2_supported" = "no" ]]; then
        printf "Unified cgroup hierarchy is not supported. Skipping.\n" >&2
        return 0
    fi
    if [[ "$2" = "yes" && "$is_cgns_supported" = "no" ]];  then
        printf "Cgroup namespaces are not supported. Skipping.\n" >&2
        return 0
    fi

    local _root="/var/lib/machines/unified-$1-cgns-$2-api-vfs-writable-$3"
    /create-busybox-container "$_root"
    UNIFIED_CGROUP_HIERARCHY="$1" SYSTEMD_NSPAWN_USE_CGNS="$2" SYSTEMD_NSPAWN_API_VFS_WRITABLE="$3" systemd-nspawn --bind /lib64 --register=no -D "$_root" -b
    UNIFIED_CGROUP_HIERARCHY="$1" SYSTEMD_NSPAWN_USE_CGNS="$2" SYSTEMD_NSPAWN_API_VFS_WRITABLE="$3" systemd-nspawn --bind /lib64 --register=no -D "$_root" --private-network -b

    if UNIFIED_CGROUP_HIERARCHY="$1" SYSTEMD_NSPAWN_USE_CGNS="$2" SYSTEMD_NSPAWN_API_VFS_WRITABLE="$3" systemd-nspawn --bind /lib64 --register=no -D "$_root" -U -b; then
       [[ "$is_user_ns_supported" = "yes" && "$3" = "network" ]] && return 1
    else
       [[ "$is_user_ns_supported" = "no" && "$3" = "network" ]] && return 1
    fi

    if UNIFIED_CGROUP_HIERARCHY="$1" SYSTEMD_NSPAWN_USE_CGNS="$2" SYSTEMD_NSPAWN_API_VFS_WRITABLE="$3" systemd-nspawn --bind /lib64 --register=no -D "$_root" --private-network -U -b; then
       [[ "$is_user_ns_supported" = "yes" && "$3" = "yes" ]] && return 1
    else
       [[ "$is_user_ns_supported" = "no" && "$3" = "yes" ]] && return 1
    fi

    return 0
}

check_bind_tmp_path

check_notification_socket

for api_vfs_writable in yes no network; do
    run no no $api_vfs_writable
    run yes no $api_vfs_writable
    run no yes $api_vfs_writable
    run yes yes $api_vfs_writable
done

touch /testok
EOF

        chmod 0755 $initdir/test-nspawn.sh
        for service in testsuite.service; do
            cp $initdir/etc/systemd/system/$service /etc/systemd/system/
        done
        setup_testsuite
    ) || return 1
}

test_cleanup() {
    for service in testsuite.service; do
         rm /etc/systemd/system/$service
    done
    rm /create-busybox-container
    rm -r /nc-container
    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0

}

do_test "$@"
