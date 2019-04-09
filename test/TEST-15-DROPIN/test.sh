#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="Dropin tests"
TEST_NO_QEMU=1

export TEST_BASE_DIR=/var/opt/systemd-tests/test
. $TEST_BASE_DIR/test-functions

test_run() {
    ret=1
    systemctl daemon-reload
    systemctl start testsuite.service || return 1
    systemctl status --full testsuite.service
    test -s /failed && ret=$(($ret+1))
    [[ -e /testok ]] && ret=0
    return $ret
}

test_setup() {
        mkdir -p $TESTDIR/root
        initdir=$TESTDIR/root
        STRIP_BINARIES=no

        LOG_LEVEL=5

        # create the basic filesystem layout
        setup_basic_environment

        # mask some services that we do not want to run in these tests
        ln -s /dev/null $initdir/etc/systemd/system/systemd-hwdb-update.service
        ln -s /dev/null $initdir/etc/systemd/system/systemd-journal-catalog-update.service
        ln -s /dev/null $initdir/etc/systemd/system/systemd-networkd.service
        ln -s /dev/null $initdir/etc/systemd/system/systemd-networkd.socket
        ln -s /dev/null $initdir/etc/systemd/system/systemd-resolved.service

        # import the test scripts in the rootfs and plug them in systemd
        cp testsuite.service /etc/systemd/system/
        cp test-dropin.sh    /
        setup_testsuite

        # create dedicated rootfs for nspawn (located in $TESTDIR/nspawn-root)
        setup_nspawn_root
}

test_cleanup() {
    for service in testsuite.service; do
         rm /etc/systemd/system/$service
    done
    rm /test-dropin.sh
    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0
 }

do_test "$@"
