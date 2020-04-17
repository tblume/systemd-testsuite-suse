#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="Journal-related tests"

export TEST_BASE_DIR=/var/opt/systemd-tests/test
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

        # setup the testsuite service
        cat >$initdir/etc/systemd/system/testsuite.service <<EOF
[Unit]
Description=Testsuite service
After=multi-user.target

[Service]
ExecStart=$TESTDIR/nspawn-root/test-journal.sh
ExecStartPost=/bin/sh -x -c 'echo -e "\nfailed:" > /failed; systemctl --state=failed --no-pager >> /failed; echo -e "\ntestresult:\nOK" > /testok'
Type=oneshot
EOF

        cat >$initdir/etc/systemd/system/forever-print-hola.service <<EOF
[Unit]
Description=ForeverPrintHola service

[Service]
Type=simple
ExecStart=/bin/sh -x -c 'while :; do printf "Hola\n" || touch /i-lose-my-logs; sleep 1; done'
EOF

        # copy the units used by this test
        cp test-journal.sh $initdir/
        for service in forever-print-hola.service testsuite.service; do
            cp $initdir/etc/systemd/system/$service /etc/systemd/system/
        done

        setup_testsuite
    ) || return 1

    setup_nspawn_root
    rm -r $TESTDIR/root
}

test_cleanup() {

    for service in forever-print-hola.service testsuite.service; do
         rm /etc/systemd/system/$service
    done
    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0
}



do_test "$@"
