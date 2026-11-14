# FedRAMP-CR26 — measured, not redistributed

The converted bundle and its OSCAL re-export were **removed from this
repository on 2026-11-10**. Rule applied: a converted corpus stays only
where the publisher's own terms clearly allow redistributing an adapted
form; where that is in doubt, the result goes and the code stays.

**Source.** *FedRAMP Consolidated Rules for 2026* — FedRAMP (U.S. General
Services Administration), <https://github.com/FedRAMP/rules>. The removed
bundle was a conversion of version 2026.07.14.01. The coverage report in
this directory is of version 2026.11.02.01, the publisher's current one on
2026-11-14 (backlog #73).

**Why it was removed — the borderline case.** The publisher's repository
carries **no licence file**, and its README and AGENTS.md say nothing
about copyright or reuse (checked 2026-11-10; fedramp.gov and gsa.gov
could not be reached from the review session). The dataset is a
publication of a U.S. federal program, and works of the U.S. Government
are not subject to copyright *in the United States* (17 U.S.C. § 105).
That is a strong basis, but it is a statute about the U.S., not a
statement by the publisher: NIST's repository adds a CC0 dedication
precisely to cover the rest of the world, and this one does not. This
repository is published from Germany. No publisher statement, so: in
doubt.

**This is the removal most likely to be reversed.** It sits in a commit of
its own. If FedRAMP states a licence (or the author judges the statutory
basis sufficient), reverting that one commit restores the bundle, its
export, the README screenshot and the deep link, byte for byte.

**What remains.** The converter (`jascon/scripts/convert_cr26.py`), its
test (`jascon/scripts/test_convert_cr26.py`), the coverage report and the
conversion ledger in this directory — source *paths*, pointers made of
ids, counts and conversion rules; they reproduce no text of the
publication — and `SOURCES.sha256`, which names the publisher's file and
its digest.

**The measurement, of version 2026.11.02.01.** 291 Requirements ·
652 Mappings · 92 Sets · 5 Tailorings (4 class variants and the Rev 5 ODP
overlay) · the reference validator passes the bundle (measured
2026-11-14). All 7,532 source leaf values stand on a path the path map
knows. What became of each value is the conversion ledger's to say
(`cr26-conversion-ledger.json`, backlog #41; measured 2026-11-14):
4,553 copied, 1,987 transformed by a named rule, none unaccounted, and
992 not carried for a reason declared before the author's rule that real
content is never dropped: the update history of an entry (957) and the
process-flow diagrams (35). Whether those two are content is the author's
to decide; the report lists them. The report of version
2026.07.14.01 is in the history of this directory: 292 Requirements,
373 Mappings, 7,294 / 7,294 leaf values on a mapped path.

**Reproducible by anyone,** and the Validators workflow repeats it on
every change it watches: fetch the file `SOURCES.sha256` names, check its
digest, place it at `sources/cr_fedramp-consolidated-rules.json`, and run
the converter with `--out` and a directory of your own (it needs the
US.SP800-53 bundle, which ships here). The two coverage reports and the
ledger come out byte for byte as they are here, and the reports state the
digest of the bundle's manifest: a run that reproduces them has reproduced
the bundle. Without
`--out` the converter writes the bundle into this directory, where it
must not be committed.
