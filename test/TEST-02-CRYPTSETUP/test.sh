#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
TEST_DESCRIPTION="cryptsetup systemd setup"

. $TEST_BASE_DIR/test-functions

check_result_qemu() {
    ret=1
    mkdir -p $TESTDIR/root
    mount ${LOOPDEV}p1 $TESTDIR/root
    [[ -e $TESTDIR/root/testok ]] && ret=0
    [[ -f $TESTDIR/root/failed ]] && cp -a $TESTDIR/root/failed $TESTDIR
    cryptsetup luksOpen ${LOOPDEV}p2 tmpcrypt <$TESTDIR/keyfile
    mount /dev/mapper/tmpcrypt $TESTDIR/root/tmp
    [[ -f $TESTDIR/root/tmp/log/journal ]] && cp -a $TESTDIR/root/tmp/log/journal $TESTDIR
    umount $TESTDIR/root/tmp
    umount $TESTDIR/root
    cryptsetup luksClose /dev/mapper/tmpcrypt
    [[ -f $TESTDIR/failed ]] && cat $TESTDIR/failed
    ls -l $TESTDIR/journal/*/*.journal
    test -s $TESTDIR/failed && ret=$(($ret+1))
    return $ret
}


test_run() {
    if run_qemu; then
        check_result_qemu || return 1
    else
        dwarn "can't run QEMU, skipping"
    fi
    return 0
}

test_setup() {
    create_empty_image
    echo -n test >$TESTDIR/keyfile
    cryptsetup -q luksFormat ${LOOPDEV}p2 $TESTDIR/keyfile
    cryptsetup luksOpen ${LOOPDEV}p2 tmpcrypt <$TESTDIR/keyfile
    mkfs.ext4 -L tmp /dev/mapper/tmpcrypt
    mkdir -p $TESTDIR/root
    mount ${LOOPDEV}p1 $TESTDIR/root
    mkdir -p $TESTDIR/root/tmp
    mount /dev/mapper/tmpcrypt $TESTDIR/root/tmp

    # Create what will eventually be our root filesystem onto an overlay
    (
        LOG_LEVEL=5
        eval $(udevadm info --export --query=env --name=/dev/mapper/tmpcrypt)
        eval $(udevadm info --export --query=env --name=${LOOPDEV}p2)

        setup_basic_environment

        # setup the testsuite service
        cat >$initdir/etc/systemd/system/testsuite.service <<EOF
[Unit]
Description=Testsuite service
After=multi-user.target

[Service]
ExecStart=/bin/sh -x -c 'systemctl --state=failed --no-legend --no-pager > /failed ; echo OK > /testok'
Type=oneshot
EOF

        setup_testsuite

        install_dmevent
        generate_module_dependencies
        cat >$initdir/etc/crypttab <<EOF
$DM_NAME UUID=$ID_FS_UUID /etc/tmpkey
EOF
        echo -n test > $initdir/etc/tmpkey
        cat $initdir/etc/crypttab | ddebug

        cat >>$initdir/etc/fstab <<EOF
/dev/mapper/tmpcrypt    /tmp    ext4    defaults 0 1
EOF
    ) || return 1

    ddebug "umount $TESTDIR/root/tmp"
    umount $TESTDIR/root/tmp
    cryptsetup luksClose /dev/mapper/tmpcrypt
    ddebug "umount $TESTDIR/root"
    umount $TESTDIR/root
}

test_cleanup() {
    umount $TESTDIR/root/tmp 2>/dev/null
    [[ -b /dev/mapper/tmpcrypt ]] && cryptsetup luksClose /dev/mapper/tmpcrypt
    umount $TESTDIR/root 2>/dev/null
    [[ $LOOPDEV ]] && losetup -d $LOOPDEV
    return 0
}

do_test "$@"
