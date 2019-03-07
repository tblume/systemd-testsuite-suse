#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="https://github.com/systemd/systemd/issues/1981"
TEST_NO_QEMU=1

export TEST_BASE_DIR=/var/opt/systemd-tests/test
. $TEST_BASE_DIR/test-functions

NSPAWN_TIMEOUT=30s

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
ExecStart=$TESTDIR/nspawn-root/test-segfault.sh
ExecStartPost=/bin/sh -x -c 'echo -e "\nfailed:" > /failed; systemctl --state=failed --no-pager >> /failed; echo -e "\ntestresult:\nOK" > /testok'
Type=oneshot
EOF
        # copy the units used by this test
        cp $initdir/etc/systemd/system/testsuite.service /etc/systemd/system/testsuite.service
        cp test-segfault.sh $initdir/

        setup_testsuite
    ) || return 1

    setup_nspawn_root
    rm -r $TESTDIR/root
}

test_cleanup() {
    for file in testsuite.service my.timer.d ; do
         rm -rf /etc/systemd/system/$service
    done
    rm /usr/lib/systemd/system/my.service
    rm /usr/lib/systemd/system/my.timer

    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0

}

do_test "$@"
