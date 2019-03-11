#!/bin/bash
set -e
TEST_DESCRIPTION="https://github.com/systemd/systemd/issues/2691"
TEST_NO_NSPAWN=1

export TEST_BASE_DIR=/var/opt/systemd-tests/test
. $TEST_BASE_DIR/test-functions

test_run() {
    ret=1
    TESTSUITESTOP=$(sed -n '/testsuite.service: Control process exited, code=dumped, status=11/s/\[ *\([[:digit:]]*\)\..*/\1/p' /shutdown-log.txt) 
    LASTLINE=$(sed -n '$ s/\[ *\([[:digit:]]*\)\..*/\1/p' /shutdown-log.txt)
    [[ $(($LASTLINE-$TESTSUITESTOP)) < 90 ]] && echo -e "OK" > /testok || rm /testok
    systemctl --state=failed --no-pager > /failed
    [[ -e /testok ]] && ret=0 || ret=$(($ret+1))
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

[Service]
Type=oneshot
ExecStart=/bin/sh -c '>/testok'
RemainAfterExit=yes
ExecStop=/bin/sh -c 'kill -SEGV $$$$'
TimeoutStopSec=270s
EOF
        cat >$initdir/etc/systemd/system/end.service <<'EOF'
[Unit]
Description=Record status after stopping the test
DefaultDependencies=no
After=shutdown.target
Before=umount.target

[Service]
Type=oneshot
ExecStart=/bin/sh -x -c 'systemctl status testsuite.service > /failed'
TimeoutStartSec=5m
EOF


        setup_testsuite
    )

    # mask some services that we do not want to run in these tests
    [[ -f /etc/systemd/system/systemd-hwdb-update.service ]] && ln -fs /dev/null /etc/systemd/system/systemd-hwdb-update.service
    [[ -f /etc/systemd/system/systemd-journal-catalog-update.service ]] && ln -fs /dev/null /etc/systemd/system/systemd-journal-catalog-update.service
    [[ -f /etc/systemd/system/systemd-networkd.service ]] && ln -fs /dev/null /etc/systemd/system/systemd-networkd.service
    [[ -f /etc/systemd/system/systemd-networkd.socket ]] && ln -fs /dev/null /etc/systemd/system/systemd-networkd.socket
    [[ -f /etc/systemd/system/systemd-resolved.service ]] && ln -fs /dev/null /etc/systemd/system/systemd-resolved.service
    [[ -f /etc/systemd/system/systemd-machined.service ]] && ln -fs /dev/null /etc/systemd/system/systemd-machined.service

    # copy the units used by this test
    cp $initdir/etc/systemd/system/testsuite.service /etc/systemd/system/testsuite.service
    cp $initdir/etc/systemd/system/end.service /etc/systemd/system/end.service

    [[ -d  /etc/systemd/system/reboot.target.wants ]] || mkdir /etc/systemd/system/reboot.target.wants
    ln -s /etc/systemd/system/end.service /etc/systemd/system/reboot.target.wants/end.service

    systemctl daemon-reload
    systemctl start testsuite.service || return 1

cat > /usr/lib/systemd/system-shutdown/debug.sh  <<'EOF'
#!/bin/sh
mount -o remount,rw /
dmesg > /shutdown-log.txt
mount -o remount,ro /
EOF
   chmod ugo+x /usr/lib/systemd/system-shutdown/debug.sh

   sed -i '/GRUB_CMDLINE_LINUX_DEFAULT.*/s/"$/systemd.log_level=debug systemd.journald.forward_to_kmsg log_buf_len=1M printk.devkmsg=on enforcing=0"/' /etc/default/grub
   grub2-mkconfig -o /boot/grub2/grub.cfg || return 1
}

test_cleanup() {
    for service in end.service testsuite.service; do
         rm -f /etc/systemd/system/$service
    done

    rm -f /usr/lib/systemd/system-shutdown/debug.sh
    rm -rf /etc/systemd/system/reboot.target.wants

    rm /usr/lib/systemd/system-shutdown/debug.sh
    rm /shutdown.log

    [[ -e /testok ]] && rm /testok
    [[ -e /failed ]] && rm /failed
    return 0

}

do_test "$@"
