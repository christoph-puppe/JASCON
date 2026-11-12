#!/usr/bin/env python3
"""Rebuilds SKILL_jascon.zip from the files git tracks under jascon/.

    uv run python drafts/cp-advice-1/build_skill_zip.py            # check only
    uv run python drafts/cp-advice-1/build_skill_zip.py --write    # rebuild from HEAD

No build script for the archive is in the repository, so this one first
finds out what the archive IS. It takes the last commit that changed the
archive and compares the archive of that commit, entry by entry, with the
blobs of that commit: every entry must be a tracked file under jascon/
with exactly the blob's bytes, and no tracked file may be missing. Only
then does it accept that rule and, with --write, apply it to HEAD: the
entries in path order, one fixed date, deflated - so the same commit gives
the same archive. If the comparison fails, nothing is written."""
import io, os, subprocess, sys, zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
NAME = "SKILL_jascon.zip"
DATE = (2026, 11, 12, 0, 0, 0)

def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, check=True).stdout

def tracked(rev):
    return sorted(n for n in git("ls-tree", "-r", "--name-only", rev, "jascon/").decode("utf-8").split("\n") if n)

base = git("log", "-1", "--format=%H", "HEAD", "--", NAME).decode().strip()
old = zipfile.ZipFile(io.BytesIO(git("show", f"{base}:{NAME}")))
names = sorted(n for n in old.namelist() if not n.endswith("/"))
want = tracked(base)
only_zip, only_git = sorted(set(names) - set(want)), sorted(set(want) - set(names))
differ = [n for n in names if n in want and old.read(n) != git("show", f"{base}:{n}")]
print(f"archive of {base[:8]}: {len(names)} files; tracked under jascon/ there: {len(want)}")
if only_zip or only_git or differ:
    print(f"  only in the archive: {only_zip}\n  only in git: {only_git}\n  bytes differ: {differ}")
    sys.exit("the archive is NOT 'the tracked files under jascon/ as blobs' at that commit; "
             "nothing rebuilt - the rule that built it is not known here")
print("  the archive is the tracked files under jascon/, as blobs")
head = tracked("HEAD")
stale = [n for n in head if n not in names or old.read(n) != git("show", f"HEAD:{n}")]
gone = [n for n in names if n not in head]
print(f"against HEAD: {len(stale)} file(s) new or changed, {len(gone)} gone")
if "--write" not in sys.argv:
    sys.exit(0)
if git("status", "--porcelain", "--", "jascon/").strip():
    sys.exit("jascon/ has uncommitted changes; commit first - the archive is built from HEAD")
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    for n in head:
        zi = zipfile.ZipInfo(n, DATE)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        z.writestr(zi, git("show", f"HEAD:{n}"))
open(os.path.join(ROOT, NAME), "wb").write(buf.getvalue())
print(f"rebuilt {NAME} from HEAD: {len(head)} files, {len(buf.getvalue()):,} bytes")
