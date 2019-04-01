#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
set -e
TEST_DESCRIPTION="https://github.com/systemd/systemd/issues/3171"
TEST_NO_QEMU=1

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
        dracut_install cat mv stat nc

        # setup the testsuite service
        cat >$initdir/etc/systemd/system/testsuite.service <<EOF
[Unit]
Description=Testsuite service
After=multi-user.target

[Service]
ExecStart=$initdir/test-socket-group.sh
ExecStartPost=/bin/sh -x -c 'echo -e "\nfailed:" > /failed; systemctl --state=failed --no-pager >> /failed; echo -e "\ntestresult:\nOK" > /testok'
Type=oneshot
EOF


        cat >$initdir/test-socket-group.sh <<'EOF'
#!/bin/bash
set -x
set -e
set -o pipefail

U=/run/systemd/system/test.socket
cat <<'EOL' >$U
[Unit]
Description=Test socket
[Socket]
Accept=yes
ListenStream=/run/test.socket
SocketGroup=adm
SocketMode=0660
EOL

cat <<'EOL' > /run/systemd/system/test@.service
[Unit]
Description=Test service
[Service]
StandardInput=socket
ExecStart=/bin/sh -x -c cat
EOL

systemctl start test.socket
systemctl is-active test.socket
[[ "$(stat --format='%G' /run/test.socket)" == adm ]]
echo A | nc -w1 -U /run/test.socket

mv $U ${U}.disabled
systemctl daemon-reload
systemctl is-active test.socket
[[ "$(stat --format='%G' /run/test.socket)" == adm ]]
echo B | nc -w1 -U /run/test.socket && exit 1

mv ${U}.disabled $U
systemctl daemon-reload
systemctl is-active test.socket
echo C | nc -w1 -U /run/test.socket && exit 1
[[ "$(stat --format='%G' /run/test.socket)" == adm ]]

systemctl restart test.socket
systemctl is-active test.socket
echo D | nc -w1 -U /run/test.socket
[[ "$(stat --format='%G' /run/test.socket)" == adm ]]


touch /testok
EOF

        chmod 0755 $initdir/test-socket-group.sh
        for service in testsuite.service; do
            cp $initdir/etc/systemd/system/$service /etc/systemd/system/
        done
        setup_testsuite
    ) || return 1

    setup_nspawn_root
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
