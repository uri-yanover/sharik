# sharik
 A `shar (1)`-like utility with a programmatic fine-tuned API

# Usage
```
sharik \
    -x \
    --command foo \
    --add "${TMP_PATH_1}" \
    --inline "${K1}=${V1}" --inline "${K2}=${V2}" \
    --clear-glob 'test.txt' \
    -o "${TMP_PATH_2}"/sharik.sh
```

Where:
* `-o <filename>` (required) writes the output into the specified file. You can use `-` for stdout.
* `-x` (optional) toggles if all steps of unpacking are echoed into `stderr` (standard `bash -x` behavior). By default, off.
* `--command <command>` (required): the command that's executed at the end of the unpacking. Needs to be specified explicitly.
* `--add <filename>` (optional, multiple): add the specified file/directory into the archive.
   In case of file, it will be added to the archive root with the file's original name. In case of a directory, all of its files will be added to the archive with the paths relative to the directory root.
* `--inline <key>=<value>` (optional, multiple): add files to the archive that are specified directly through the command line. Useful for passing configurations.
* `--clear-glob <glob>` (optional, multiple): specifies a condition on file names (including paths) that will not be compressed/base64 encoded so that they may be inspected directly.