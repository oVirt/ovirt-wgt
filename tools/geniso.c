/*
 * Copyright (c) 2012, Red Hat, Inc
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the <organization> nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Christophe Fergeau <cfergeau@redhat.com>
 */
#include <glib.h>
#include <gio/gio.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    const char *x86_path;
    const char *amd64_path;
    const char *file_regex;
} VioDriver;

typedef enum {
    VIO_DRIVER_NETKVM,
    VIO_DRIVER_SERIAL,
    VIO_DRIVER_BALLOON,
    VIO_DRIVER_BLOCK,
    VIO_DRIVER_SCSI,
    VIO_DRIVER_LAST
} VioDriverName;

static const char *vio_driver_names[] = {
    [VIO_DRIVER_NETKVM] = "netkvm",
    [VIO_DRIVER_SERIAL] = "serial",
    [VIO_DRIVER_BALLOON] = "balloon",
    [VIO_DRIVER_BLOCK] = "block",
    [VIO_DRIVER_SCSI] = "scsi"
};

typedef VioDriver VioDriverSet[VIO_DRIVER_LAST];

typedef enum {
    VIO_WINVER_WINXP,
    VIO_WINVER_WIN2003,
    VIO_WINVER_VISTA,
    VIO_WINVER_WIN7,
    VIO_WINVER_WIN2008,
    VIO_WINVER_WIN2008R2,
    VIO_WINVER_WIN8,
    VIO_WINVER_LAST
} VioWinVer;

static const char *win_ver_names[] = {
    [VIO_WINVER_WINXP] = "winxp",
    [VIO_WINVER_WIN2003] = "win2003",
    [VIO_WINVER_VISTA] = "vista",
    [VIO_WINVER_WIN7] = "win7",
    [VIO_WINVER_WIN2008] = "win2008",
    [VIO_WINVER_WIN2008R2] = "win2008r2",
    [VIO_WINVER_WIN8] = "win8"
};

static const VioDriverSet drivers[] = {
    [VIO_WINVER_WINXP] = {
        [VIO_DRIVER_NETKVM] = { "XP/x86", "XP/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Wxp/x86", "Wnet/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Wxp/x86", "Wnet/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Wxp/x86", "Wnet/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Wnet/x86", "Wnet/amd64", "vioscsi.*" },
    },
    [VIO_WINVER_WIN2003] = {
        [VIO_DRIVER_NETKVM] = { "XP/x86", "XP/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Wnet/x86", "Wnet/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Wnet/x86", "Wnet/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Wnet/x86", "Wnet/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Wnet/x86", "Wnet/amd64", "vioscsi.*" },
    },
    [VIO_WINVER_VISTA] = {
        [VIO_DRIVER_NETKVM] = { "Vista/x86", "Vista/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Wlh/x86", "Wlh/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Wlh/x86", "Wlh/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Wlh/x86", "Wlh/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Wlh/x86", "Wlh/amd64", "vioscsi.*" },
    },
    [VIO_WINVER_WIN7] = {
        [VIO_DRIVER_NETKVM] = { "Win7/x86", "Win7/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Win7/x86", "Win7/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Win7/x86", "Win7/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Win7/x86", "Win7/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Win7/x86", "Win7/amd64", "vioscsi.*" },
    },
    [VIO_WINVER_WIN2008] = {
        [VIO_DRIVER_NETKVM] = { "Vista/x86", "Vista/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Wlh/x86", "Wlh/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Wlh/x86", "Wlh/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Wlh/x86", "Wlh/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Wlh/x86", "Wlh/amd64", "vioscsi.*" },
    },
    [VIO_WINVER_WIN2008R2] = {
        [VIO_DRIVER_NETKVM] = { "Win7/x86", "Win7/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Win7/x86", "Win7/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Win7/x86", "Win7/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Wlh/x86", "Wlh/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Win7/x86", "Win7/amd64", "vioscsi.*" },
    },
    [VIO_WINVER_WIN8] = {
        [VIO_DRIVER_NETKVM] = { "Win7/x86", "Win7/amd64", "(netkvm.*|readme.doc)" },
        [VIO_DRIVER_SERIAL] = { "Win7/x86", "Win7/amd64", "(vioser.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BALLOON] = { "Win7/x86", "Win7/amd64", "(balloon.*|bln.*|wdfcoinstaller.*.dll)" },
        [VIO_DRIVER_BLOCK] = { "Wlh/x86", "Wlh/amd64", "viostor.*" },
        [VIO_DRIVER_SCSI] = { "Win7/x86", "Win7/amd64", "vioscsi.*" },
    }
};

static GHashTable *path_mapping;

static gboolean copy_file(const char *src, const char *dest, GError **error)
{
    GFile *src_file;
    GFile *dest_file;
    gboolean success;

    g_print("Copying %s to %s\n", src, dest);

    src_file = g_file_new_for_path(src);
    dest_file = g_file_new_for_path(dest);
    success = g_file_copy(src_file, dest_file, G_FILE_COPY_NONE, NULL, NULL, NULL, error);
    if (error && *error) {
        if (g_str_has_suffix(src, "wdfcoinstaller01009.dll") && ((*error)->code ==  G_IO_ERROR_EXISTS)) {
            // ignore error, ugly workaround
            g_clear_error(error);
            success = TRUE;
        }
    }
    g_object_unref(src_file);
    g_object_unref(dest_file);

    return success;
}

static gboolean link_file(const char *src, const char *dest, GError **error)
{
    gint status;

    g_print("Hardlinking %s to %s\n", src, dest);

    status = link(src, dest);
    if (status != 0) {
        int errnum = errno;
        if (g_str_has_suffix(src, "wdfcoinstaller01009.dll") && (errnum == EEXIST)) {
            // ignore error, ugly workaround
            return TRUE;
        }
        g_set_error(error, G_FILE_ERROR, g_file_error_from_errno(errnum), "%s", strerror(errnum));
        return FALSE;
    }
    return TRUE;
}
typedef gboolean (*FileForeachCb)(const char *src, const char *dest, GError **error);

static gboolean file_foreach(const char *src, const char *file_pattern, const char *base_dest, const char *rel_dest, FileForeachCb cb)
{
    char *dest = g_build_filename(base_dest, rel_dest, NULL);
    GDir *dir;
    GError *error = NULL;
    const char *name;
    int creation_status;
    GRegex *file_regex;

    creation_status = g_mkdir_with_parents(dest, 0755);
    if (creation_status == -1) {
        g_warning("failed to create %s: %s", dest, strerror(errno));
        return FALSE;
    }

    file_regex = g_regex_new(file_pattern,
                             G_REGEX_CASELESS | G_REGEX_OPTIMIZE,
                             0, &error);
    if (error != NULL) {
        g_warning("error compiling regex %s: %s",
                  file_pattern, error->message);
        g_error_free(error);
        return FALSE;
    }

    dir = g_dir_open(src, 0, &error);
    if (error != NULL) {
        g_warning("error opening %s: %s", src, error->message);
        g_error_free(error);
        g_regex_unref(file_regex);
        return FALSE;
    }

    while ((name = g_dir_read_name(dir))) {
        char *src_filename;
        char *dest_filename;
        gboolean success;

        if (!g_regex_match(file_regex, name, 0, NULL)) {
            continue;
        }
        src_filename = g_build_filename(src, name, NULL);
        dest_filename = g_build_filename(dest, name, NULL);
        success = cb(src_filename, dest_filename, &error);
        if (error != NULL) {
            g_warning("failed to process %s to %s: %s", src_filename, dest_filename, error->message);
            g_error_free(error);
        }
        g_free(src_filename);
        g_free(dest_filename);
        if (!success) {
            g_free(dest);
            g_dir_close(dir);
            g_regex_unref(file_regex);
            return FALSE;
        }
    }

    g_free(dest);
    g_dir_close(dir);
    g_regex_unref(file_regex);

    return TRUE;
}

static gboolean copy_files(const char *src, const char *file_pattern,
                           const char *base_dest, const char *rel_dest)
{
    return file_foreach(src, file_pattern, base_dest, rel_dest, copy_file);
}

static gboolean create_hardlinks(const char *src, const char *file_pattern,
                                 const char *base_dest, const char *rel_dest)
{
    return file_foreach(src, file_pattern, base_dest, rel_dest, link_file);
}

static void copy_driver(const VioDriver *driver, VioWinVer winver, gboolean x86_64,
                        const char *base_src, const char *base_dest)
{
    char *src;
    char *rel_dest;
    const char *arch_path;
    char *rel_src;
    char *link_src;
    char *hash_key;

    if (x86_64) {
        rel_src = g_ascii_strdown(driver->amd64_path, -1);
        arch_path = "amd64";
    } else {
        rel_src = g_ascii_strdown(driver->x86_path, -1);
        arch_path = "x86";
    }
    hash_key = g_build_filename(rel_src, driver->file_regex, NULL);

    rel_dest = g_build_filename(win_ver_names[winver], arch_path, NULL);
    link_src = g_hash_table_lookup(path_mapping, hash_key);
    if (link_src != NULL) {
        src = g_build_filename(base_dest, link_src, NULL);
        create_hardlinks(src, driver->file_regex, base_dest, rel_dest);
    } else {
        gboolean copied;
        src = g_build_filename(base_src, rel_src, NULL);
        copied = copy_files(src, driver->file_regex, base_dest, rel_dest);
        if (copied) {
            g_print("inserted hash key:%s\n", hash_key);
            g_hash_table_insert(path_mapping,
                                g_strdup(hash_key),
                                g_strdup(rel_dest));
        }
    }
    g_free(hash_key);
    g_free(rel_dest);
    g_free(rel_src);
    g_free(src);

}
static void copy_drivers(const VioDriverSet *drivers, const char *base_src, const char *base_dest)
{
    path_mapping = g_hash_table_new_full(g_str_hash, g_str_equal, g_free, g_free);
    for (VioWinVer ver = VIO_WINVER_WINXP; ver != VIO_WINVER_LAST; ver++) {
        g_print("*** %s ***\n", win_ver_names[ver]);
        for (VioDriverName d = VIO_DRIVER_NETKVM; d != VIO_DRIVER_LAST; d++) {
            g_print("\t=== %s ===\n", vio_driver_names[d]);
            copy_driver(&drivers[ver][d], ver, FALSE, base_src, base_dest);
            copy_driver(&drivers[ver][d], ver, TRUE, base_src, base_dest);
            g_print("\n");
        }
        g_print("\n\n");
    }
}

int main(int argc, char **argv)
{
    g_type_init();
#if 0
    for (VioWinVer ver = VIO_WINVER_WINXP; ver != VIO_WINVER_LAST; ver++) {
        printf("%s:\n", win_ver_names[ver]);
        for (VioDriverName driver = VIO_DRIVER_NETKVM; driver != VIO_DRIVER_LAST; driver++) {
            printf("\t%s:\n", vio_driver_names[driver]);
            printf("\t\tx86->%s\n", drivers[ver][driver].x86_path);
            printf("\t\tamd64->%s\n", drivers[ver][driver].amd64_path);
        }
        printf("\n");
    }
#endif
    if (argc != 3) {
        char *base;
        base = g_path_get_basename(argv[0]);
        g_print("Usage: %s src dest\n", base);
        g_free(base);
        return 1;
    }

    copy_drivers(drivers, argv[1], argv[2]);

    return 0;
}
