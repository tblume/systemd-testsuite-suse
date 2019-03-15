#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="https://github.com/systemd/systemd/issues/2467"
TEST_NO_NSPAWN=1

export TEST_BASE_DIR=/var/opt/systemd-tests/test
. $TEST_BASE_DIR/test-functions
SKIP_INITRD=yes

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
        cat >$initdir/etc/systemd/system/testsuite.service <<'EOF'
[Unit]
Description=Testsuite service
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -e -x -c 'rm -f /tmp/nonexistent; systemctl start test.socket; echo a | nc -U /run/test.ctl'
ExecStartPost=/bin/sh -x -c 'echo -e "\nfailed:" > /failed; systemctl status test.socket >> /failed; echo -e "\ntestresult:\nOK" > /testok'
TimeoutStartSec=10s
EOF

	cat  >$initdir/etc/systemd/system/test.socket <<'EOF'
[Socket]
ListenStream=/run/test.ctl
EOF

	cat > $initdir/etc/systemd/system/test.service <<'EOF'
[Unit]
Requires=test.socket
ConditionPathExistsGlob=/tmp/nonexistent

[Service]
ExecStart=/bin/true
EOF

        setup_testsuite
    ) || return 1

    # mask some services that we do not want to run in these tests
    ln -s /dev/null $initdir/etc/systemd/system/systemd-hwdb-update.service
    ln -s /dev/null $initdir/etc/systemd/system/systemd-journal-catalog-update.service
    ln -s /dev/null $initdir/etc/systemd/system/systemd-networkd.service
    ln -s /dev/null $initdir/etc/systemd/system/systemd-networkd.socket
    ln -s /dev/null $initdir/etc/systemd/system/systemd-resolved.service

    # copy the units used by this test
    for unit in test.service test.socket testsuite.service test.socket; do
        cp $initdir/etc/systemd/system/$unit /etc/systemd/system/
    done

}

test_cleanup() {
    for unit in test.service test.socket testsuite.service; do
         rm /etc/systemd/system/$unit
    done
    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0

}

do_test "$@"



    ddebug "umount $TESTDIR/root"
    umount $TESTDIR/root
}

do_test "$@"
