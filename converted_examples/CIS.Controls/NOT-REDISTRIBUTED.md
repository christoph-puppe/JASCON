# CIS.Controls — measured, not redistributed

The converted bundle and its OSCAL re-export were **removed from this
repository on 2026-11-10**. Rule applied: a converted corpus stays only
where the publisher's own terms clearly allow redistributing an adapted
form; where that is in doubt, the result goes and the code stays.

**Source.** CIS Critical Security Controls v8.1, OSCAL edition — Center for Internet Security (CIS), <https://github.com/CISecurity/CISControls_OSCAL>.

**Why it was removed.** The publisher's terms forbid it. `LICENSE.md` in the source repository ("Terms of Use for Non-Member CIS Products", checked 2026-11-10) places the CIS Controls under CC BY-NC-ND 4.0 — NoDerivatives — and states that a user may not "post any Non-Member CIS Product on any website" nor "create any derivative work based directly on an Non-Member CIS Product or any component thereof". A converted catalogue is a derivative work, and this repository is a website.

**What remains.** The converter (`jascon/scripts/convert_cis_controls.py`) and the coverage
report in this directory — source *paths*, counts and conversion rules; it
reproduces no text of the publication.

**The measurement stands.** 171 Requirements · 34 Sets · 5,493 / 5,493 source paths mapped. It was made on the publisher's file
and is reproducible by anyone entitled to that file: obtain it from the
publisher under the publisher's terms, place it at `sources/CIS Controls.json`,
and run the converter.

**The project's workflow does not run this conversion.** The four shipped
catalogue conversions and the CR26 conversion are run again on every
change from sources pinned by address and digest. A step that would do
the same here, converting the publisher's file and discarding the result,
was built on 2026-11-14 and left out by the author's decision the same
day ("leave it out"; backlog #76). The question the step raised: the
terms quoted above forbid creating a derivative work, and the step would
have made one on every change, if only to discard it.
The converter has changed since the measurement (it takes
`--obligated-party` and `--out`, backlog #74) and was not run by this
project after that change.
