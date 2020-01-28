#!/bin/bash
set -e
TEST_DESCRIPTION="Run unit tests under containers"
RUN_IN_UNPRIVILEGED_CONTAINER=yes

. $TEST_BASE_DIR/test-functions

check_result_nspawn() {
    local _ret=1
    [[ -e $TESTDIR/$1/testok ]] && _ret=0
    if [[ -s $TESTDIR/$1/failed ]]; then
        _ret=$(($_ret+1))
        echo "=== Failed test log ==="
        cat $TESTDIR/$1/failed
    else
        if [[ -s $TESTDIR/$1/skipped ]]; then
            echo "=== Skipped test log =="
            cat $TESTDIR/$1/skipped
        fi
        if [[ -s $TESTDIR/$1/testok ]]; then
            echo "=== Passed tests ==="
            cat $TESTDIR/$1/testok
        fi
    fi
    cp -a $TESTDIR/$1/var/log/journal $TESTDIR
    [[ -n "$TIMED_OUT" ]] && _ret=$(($_ret+1))
    return $_ret
}

test_run() {
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
    [[ -e /testok ]] && _ret=0
    if [[ -s /failed ]]; then
        _ret=$(($_ret+1))
        echo "=== Failed test log ==="
        cat /failed
    else
        if [[ -s /skipped ]]; then
            echo "=== Skipped test log =="
            cat /skipped
        fi
        if [[ -s /testok ]]; then
            echo "=== Passed tests ==="
            cat /testok
        fi
    fi
    [[ -n "$TIMED_OUT" ]] && _ret=$(($_ret+1))
    return $_ret
}

test_setup() {
    mkdir -p $TESTDIR/root
    initdir=$TESTDIR/root
    STRIP_BINARIES=no

    # Create what will eventually be our root filesystem onto an overlay
    (
        LOG_LEVEL=5
        eval $(udevadm info --export --query=env --name=${LOOPDEV}p2)

        for i in getfacl dirname basename capsh cut rev stat mktemp rmdir ionice unshare uname tr awk getent diff xzcat lz4cat; do
            inst_binary $i
        done

        inst /etc/hosts

        setup_basic_environment
        install_keymaps yes
        install_zoneinfo
        # Install nproc to determine # of CPUs for correct parallelization
        inst_binary nproc

        # setup the testsuite service
        cat >/etc/systemd/system/testsuite.service <<EOF
[Unit]
Description=Testsuite service

[Service]
ExecStart=/testsuite.sh
Type=oneshot
EOF
    )
    setup_nspawn_root

    # mask some services that we do not want to run in these tests
    ln -fs /dev/null $initdir/etc/systemd/system/systemd-networkd.service
    ln -fs /dev/null $initdir/etc/systemd/system/systemd-networkd.socket
    ln -fs /dev/null $initdir/etc/systemd/system/systemd-resolved.service
}

do_test "$@"
