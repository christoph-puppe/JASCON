# FedRAMP-CR26 — measured, not redistributed

The converted bundle and its OSCAL re-export were **removed from this
repository on 2026-11-10**. Rule applied: a converted corpus stays only
where the publisher's own terms clearly allow redistributing an adapted
form; where that is in doubt, the result goes and the code stays.

**Source.** *FedRAMP Consolidated Rules for 2026*, version 2026.07.14.01 —
FedRAMP (U.S. General Services Administration),
<https://github.com/FedRAMP/rules>.

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

**What remains.** The converter (`jascon/scripts/convert_cr26.py`) and the
coverage report in this directory — source *paths*, counts and conversion
rules; it reproduces no text of the publication.

**The measurement stands.** 292 Requirements · 373 Mappings · 91 Sets ·
4 Tailorings (+ the Rev 5 ODP overlay) · 7,294 / 7,294 source paths
mapped. Reproducible by anyone: fetch `fedramp-consolidated-rules.json`
from the publisher, place it at
`sources/cr_fedramp-consolidated-rules.json`, and run the converter (it
needs the US.SP800-53 bundle, which ships here).
