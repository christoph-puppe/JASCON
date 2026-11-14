#!/usr/bin/env bash
# Downloads the source files of one conversion as its SOURCES.sha256 pins
# them, and checks their digests.
#
#     .github/scripts/fetch-pinned-sources.sh converted_examples/AU.ISM/SOURCES.sha256
#
# Run from the repository root. The list says, in comment lines:
#     # base: <address every path is read from; a tag or a commit is part of it>
#     # into: <the folder, under the repository root, the converter reads from>
#     # path: <path under the base>              saved under its own file name
#     # path: <path under the base> -> <name>    saved under another name
# and below them, one line per file, what `sha256sum` prints for it. The
# files go to a folder git ignores (sources/). A file that cannot be
# fetched, or whose digest is not the one listed, stops the run: a converter
# is never run on a source nobody pinned.
set -euo pipefail
list=${1:?usage: fetch-pinned-sources.sh <SOURCES.sha256>}
[ -f "$list" ] || { echo "$list: no such list"; exit 1; }
base=$(sed -n 's/^# base: //p' "$list")
into=$(sed -n 's/^# into: //p' "$list")
[ -n "$base" ] || { echo "$list: no '# base:' line"; exit 1; }
[ -n "$into" ] || { echo "$list: no '# into:' line"; exit 1; }
[ "$(sed -n 's/^# path: //p' "$list" | wc -l)" -eq "$(grep -cv -e '^#' -e '^$' "$list")" ] \
  || { echo "$list: the '# path:' lines and the digest lines differ in number"; exit 1; }
mkdir -p "$into"
sed -n 's/^# path: //p' "$list" | while IFS= read -r line; do
  path=${line%% -> *}
  name=${line##* -> }
  [ "$name" != "$line" ] || name=$(basename "$path")
  curl -sSfL --retry 3 -o "$into/$name" "$base$path"
done
case "$list" in /*) ;; *) list=$PWD/$list ;; esac
(cd "$into" && sha256sum -c "$list")
