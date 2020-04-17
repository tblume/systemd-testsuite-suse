#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="https://github.com/systemd/systemd/issues/2730"
TEST_NO_NSPAWN=1

export TEST_BASE_DIR=/var/opt/systemd-tests/test
. $TEST_BASE_DIR/test-functions
FSTYPE=btrfs

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

        # setup the testsuite service
        cat >$initdir/etc/systemd/system/testsuite.service <<EOF
[Unit]
Description=Testsuite service
After=multi-user.target

[Service]
ExecStart=/bin/sh -x -c 'mount -o remount,rw /dev/vda2 && echo -e "\ntestresult:\nOK" > /testok > /testok'
ExecStartPost=/bin/sh -x -c 'echo -e "\nfailed:" > /failed; systemctl --state=failed --no-pager >> /failed'
Type=oneshot
EOF

    rm $initdir/etc/fstab
    cat >$initdir/etc/systemd/system/-.mount <<EOF
[Unit]
Before=local-fs.target

[Mount]
What=/dev/vda2
Where=/
Type=btrfs
Options=errors=remount-ro,noatime

[Install]
WantedBy=local-fs.target
Alias=root.mount
EOF

    cat >$initdir/etc/systemd/system/systemd-remount-fs.service <<EOF
[Unit]
DefaultDependencies=no
Conflicts=shutdown.target
After=systemd-fsck-root.service
Before=local-fs-pre.target local-fs.target shutdown.target
Wants=local-fs-pre.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/systemctl reload /
EOF

        setup_testsuite
    ) || return 1

    # copy the units used by this test
    cp $initdir/etc/systemd/system/testsuite.service /etc/systemd/system/testsuite.service

    ln -s /etc/systemd/system/-.mount $initdir/etc/systemd/system/root.mount
    mkdir -p $initdir/etc/systemd/system/local-fs.target.wants
    ln -s /etc/systemd/system/-.mount $initdir/etc/systemd/system/local-fs.target.wants/-.mount

    # mask some services that we do not want to run in these tests
    ln -s /dev/null $initdir/etc/systemd/system/systemd-hwdb-update.service
    ln -s /dev/null $initdir/etc/systemd/system/systemd-journal-catalog-update.service
    ln -s /dev/null $initdir/etc/systemd/system/systemd-networkd.service
    ln -s /dev/null $initdir/etc/systemd/system/systemd-networkd.socket
    ln -s /dev/null $initdir/etc/systemd/system/systemd-resolved.service
}

test_cleanup() {
    for service in testsuite.service; do
         rm /etc/systemd/system/$service
    done
    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0

}

do_test "$@"
