/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * load kernel modules
 *
 * Copyright © 2011 ProFUSION embedded systems
 *
 */

#include <errno.h>
#include <libkmod.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

#include "module-util.h"
#include "string-util.h"
#include "udev.h"

static struct kmod_ctx *ctx = NULL;

static int load_module(struct udev *udev, const char *alias) {
        _cleanup_(kmod_module_unref_listp) struct kmod_list *list = NULL;
        struct kmod_list *l;
        int err;

        err = kmod_module_new_from_lookup(ctx, alias, &list);
        if (err < 0)
                return err;

        if (list == NULL)
                log_debug("No module matches '%s'", alias);

        kmod_list_foreach(l, list) {
                _cleanup_(kmod_module_unrefp) struct kmod_module *mod = NULL;

                mod = kmod_module_get_module(l);

                err = kmod_module_probe_insert_module(mod, KMOD_PROBE_APPLY_BLACKLIST, NULL, NULL, NULL, NULL);
                if (err == KMOD_PROBE_APPLY_BLACKLIST)
                        log_debug("Module '%s' is blacklisted", kmod_module_get_name(mod));
                else if (err == 0)
                        log_debug("Inserted '%s'", kmod_module_get_name(mod));
                else
                        log_debug("Failed to insert '%s'", kmod_module_get_name(mod));
        }

        return err;
}

_printf_(6,0) static void udev_kmod_log(void *data, int priority, const char *file, int line, const char *fn, const char *format, va_list args) {
        log_internalv(priority, 0, file, line, fn, format, args);
}

static int builtin_kmod(struct udev_device *dev, int argc, char *argv[], bool test) {
        struct udev *udev = udev_device_get_udev(dev);
        int i;

        if (!ctx)
                return 0;

        if (argc < 3 || !streq(argv[1], "load")) {
                log_error("expect: %s load <module>", argv[0]);
                return EXIT_FAILURE;
        }

        for (i = 2; argv[i]; i++) {
                log_debug("Execute '%s' '%s'", argv[1], argv[i]);
                load_module(udev, argv[i]);
        }

        return EXIT_SUCCESS;
}

/* called at udev startup and reload */
static int builtin_kmod_init(struct udev *udev) {
        if (ctx)
                return 0;

        ctx = kmod_new(NULL, NULL);
        if (!ctx)
                return -ENOMEM;

        log_debug("Load module index");
        kmod_set_log_fn(ctx, udev_kmod_log, udev);
        kmod_load_resources(ctx);
        return 0;
}

/* called on udev shutdown and reload request */
static void builtin_kmod_exit(struct udev *udev) {
        log_debug("Unload module index");
        ctx = kmod_unref(ctx);
}

/* called every couple of seconds during event activity; 'true' if config has changed */
static bool builtin_kmod_validate(struct udev *udev) {
        log_debug("Validate module index");
        if (!ctx)
                return false;
        return (kmod_validate_resources(ctx) != KMOD_RESOURCES_OK);
}

const struct udev_builtin udev_builtin_kmod = {
        .name = "kmod",
        .cmd = builtin_kmod,
        .init = builtin_kmod_init,
        .exit = builtin_kmod_exit,
        .validate = builtin_kmod_validate,
        .help = "Kernel module loader",
        .run_once = false,
};
