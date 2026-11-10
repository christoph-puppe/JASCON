# CIS.Ubuntu2404 — measured, not redistributed

The converted bundle and its OSCAL re-export were **removed from this
repository on 2026-11-10**. Rule applied: a converted corpus stays only
where the publisher's own terms clearly allow redistributing an adapted
form; where that is in doubt, the result goes and the code stays.

**Source.** CIS Ubuntu Linux 24.04 LTS Benchmark v1.0.0 — Center for Internet Security (CIS).

**Why it was removed.** CIS Benchmarks are CIS products. CIS's "Terms of Use for Non-Member CIS Products" (read in <https://github.com/CISecurity/CISControls_OSCAL>, `LICENSE.md`, checked 2026-11-10) forbid posting a CIS product on any website and creating derivative works from one. The benchmark's own licence page could not be read from the review session; nothing found permits redistributing a converted form.

**What remains.** The converter (`jascon/scripts/convert_cis_benchmark.py`) and the coverage
report in this directory — source *paths*, counts and conversion rules; it
reproduces no text of the publication.

**The measurement stands.** 312 Requirements · 635 Mappings · 79 Sets · 20,698 / 20,698 source paths mapped. It was made on the publisher's file
and is reproducible by anyone entitled to that file: obtain it from the
publisher under the publisher's terms, place it at `sources/CIS Ubuntu Linux 24.04 LTS Benchmark.json`,
and run the converter.
