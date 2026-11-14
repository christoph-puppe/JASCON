<#
JASCON - second-language reference validator (gate 4: the
weekend-validator acceptance test). PowerShell 5.1, ZERO installs - runs
on a stock Windows box, the auditor's machine.

Ported from the NORMATIVE sources (specification + appendices A-C + the
conformance corpus as oracle), matching validate_core.py behavior:
canonicalization (RFC 8785 member ordering, UTF-16 code units), both
digests, shape-disjoint type inference against the kernel JSON Schema
(consumed via a documented schema-subset interpreter), parameter law,
modality lattice, reference closure, facet enforcement (fail-closed),
tier derivation (Set-member resolution + DSSE verification mode with a
dependency-free Ed25519 over System.Numerics.BigInteger), op-law duties,
D3.5 composition, B.1.8 conditional-apply, and all 18 vector families.

Kernel 2.0.0 (CP-RISK-1): Risk is the tenth kernel type - typed by the
schema (RISK-1..6 are schema conditionals, named on failure by
Risk-Rule-Violations), closure RISK-7/8, typed Risk edges RISK-12, the
B.1.9 risk-coverage primitive (live risks only; a predicate select leaves
the selection open), RISK-9/10 notes, RISK-11.

PORT STATUS (2026-11-11): the 2.0.0 additions (CP-RISK-1 and its rc.1
review fixes, the kernel-version pin, scale definitions and the matrix,
the D26 pin rule) were ported on 2026-11-10 without a PowerShell runtime
and first EXECUTED on 2026-11-11 on Windows PowerShell 5.1: all 258
vectors in 15 families pass, the same counts as validate_core.py; the
port guards are removed. Fixed on that run: the example folder is read
flat, as validate_examples() reads it (its Attestation was skipped, an
unlisted file went unnoticed); every Attestation's envelope is checked
in a bundle (a broken one failed only if a tier derivation used it);
every map is keyed ordinally (#45: ids differing only in case collided).

Kernel 2.0.0 (CP-CHECK-1, PROPOSED; backlog #56, ported and run on
2026-11-11): Check is the eleventh kernel type. The schema subset gained
oneOf, not and else. Here: the I-Regexp engine (RFC 9485 ABNF, parsed and
run as a state-set simulation, never handed to .NET Regex), check-verdict
(B.1.10), CHECK-1..15 with every recorded verdict recomputed and the
evidence chain verified in the store beside the manifest. 415 vectors in
16 families pass (check: 156), the same counts as validate_core.py.
EXECUTED 2026-11-12 on Windows PowerShell 5.1: the twelfth comparator
`not-equals`, the per-resource counts of B.1.10 step 5 (Check-Each,
Ck-Percent, the `expected-resources` of the verdict vectors) and the
refusal of surrogate code points in a pattern (RFC 9485 as published;
`pattern-codepoints` in the regex vectors) had been ported without a
PowerShell runtime. They ran with the advice-pack proposal in the tree:
518 vectors in 17 families (check: 188), the five bundles, the worked
pack and the example folder, the same counts as validate_core.py
(drafts/CP-ADVICE-1.md, 13.4). Backlog #60 is closed by that run.
EXECUTED 2026-11-12, later the same day, on Windows PowerShell 5.1 (a
hosted Windows runner of GitHub Actions, .github/workflows/validators.yml):
the author's decisions on advice packs and on two date fields had been
ported without a PowerShell runtime - KERNEL-1 for a Component with
product-version, Date-Rule-Violations (DATE-1, DATE-2) and the
shape-vectors of kernel-vectors.json. The schema changes themselves
(product-version, the typed due and opened) need no code here: this file
reads the kernel schema. 537 vectors in 17 families (kernel: 25, advice:
74), the five bundles, the worked pack and the example folder, the same
counts as validate_core.py. Backlog #63 is closed by that run, and the
workflow repeats it on every change.
CHANGED 2026-11-13 (backlog #45 and #58): no PowerShell operator compares
two strings any more. 354 comparisons made with -eq, -ne, -ceq, -cne,
-contains and their relatives became ordinal ones (the note at Str-Eq says
how and why); the lookup tables keyed by data are ordinal maps; the type
names of a schema are no longer matched by a `switch`; a choice value is
compared as validate_core.py compares it. .github/scripts/lint-twin.ps1
reads this file with PowerShell's own parser and fails the build when an
operator could meet two strings again. Six vectors came with the change,
574 in all (reference: 18, tier: 10). Before it, three of the six failed
here and passed in validate_core.py: an operation addressing statement
`s1` + U+00AD, one addressing a statement id in another normal form, and
a Tailoring whose id differs from its content's origin by one U+00AD,
which this file read as the authority's own.
EXECUTED 2026-11-13 on Windows PowerShell 5.1 (the workflow, commit
c0fe8082): the lint, then 574 vectors in 17 families, the five bundles,
the worked pack and the example folder, the same counts as
validate_core.py, ALL GREEN in 159 s.
KNOWN LIMITS of this port: a general category (\p{..}) is read from the
HOST's Unicode database, .NET here and unicodedata there, so a code point
assigned after either database was built can match differently; an
integer fact beyond 64 bits is not read as an integer.

Kernel 2.0.0 (CP-ADVICE-1, PROPOSED; ported and run on 2026-11-12): advice
packs. A manifest may carry a pack header; a capability may name clauses
(statement-ids); capability-ref has a grammar. ADVICE-1..11: what a pack
may hold, capabilities and the edges that cite them, the vendor's manifest
a set keeps under packs/sha256/, and what an import may touch
(Compose-Advice). Publisher claimed or proven uses the envelope check of
the Tailoring tier. NOT ported: the --import-advice dry run of
validate_core.py (the rule it prints, ADVICE-11, is here and in the
vectors).

SPEED (2026-11-11): type inference took four fifths of a bundle run. The
schema interpreter now reads a schema node once into a plan, tests the
cheap keywords first and remembers a $ref verdict for the object under
inference; JSON is read from the .NET parser's own dictionaries instead
of ConvertFrom-Json's PSCustomObjects; the canonical form is written into
one StringBuilder. Measured on one machine: the default run 1452 s ->
219 s, the vectors 72 s -> 19 s, the output of the run unchanged line for
line. 700 mutated objects get the same types, digests and optional-empty
findings from this file and from validate_core.py - among them objects
with members that differ only in case or have an empty name, which
ConvertFrom-Json could not read at all.

Kernel 2.0.0 (CP-AUTHOR-1, specification 2.0.0-rc.4 D26; backlog #65 and
#66, ported on 2026-11-13): who decided, and when. `provenance`
{author-ref, date} on a Tailoring and its selects, excludes and
operations, on a Risk and its ratings, on an Implementation and a Finding;
`decided` and `review-due` on a Deviation; `date` on an authorization. The
shapes need no code here: this file reads the kernel schema. Ported:
KERNEL-1 for the new fields, the names DATE-3..5 (and `decided` under
DATE-1), the two reports AUTHOR-1..4 (Author-Report) and REVIEW-1
(Review-Report), the vector family `author`. REVIEW-1 is the one place
where this file reads a clock, and nothing fails by it. Both reports name
their objects in the order of the UTF-16 code units of the ids.
EXECUTED 2026-11-13 on Windows PowerShell 5.1 (the workflow, commit
e4031a84): the lint, then 637 vectors in 18 families (kernel: 54, author:
34), the five bundles, the worked pack and the example folder, the same
counts and the same AUTHOR and REVIEW lines as validate_core.py, ALL GREEN
in 218 s. Six vectors came after that run, 643 in all (author: 40): a
duration in seconds, one in minutes, one that ends within a day and the
same one on the day it ends, and the order of each report. This file
passes them unchanged under PowerShell 7.4 on Linux, with a stand-in for
the JSON parser of the .NET Framework; the workflow runs them on Windows
PowerShell 5.1 with the commit that brought them.
CHANGED 2026-11-13 (backlog #68, decided by the author: refuse): a value
that ends in a line break is not the value without it. A schema `pattern`
is read as ECMA-262 reads it, which is what JSON Schema says it is
(Ecma-Pattern: `$` is the end of the value, `.` matches no line
terminator), and this file's own expressions end in \z. A pin version is
written in the digits 0-9. Twenty-two vectors came with the change, 665 in
all (kernel: 71, parameter: 22, check: 205, composition: 9). Before it,
fifteen of them failed here and in validate_core.py alike - a date, a
date-time, a digest, a language tag, a facet id, a fact name, a decimal
and an evidence ref with a line break at the end were accepted - and a
pin version in the digits of another script stopped this file with a
conversion error. Run under PowerShell 7.4 on Linux; the workflow runs it
on Windows PowerShell 5.1.
CHANGED 2026-11-14 (backlog #46): an Attestation read with a bundle is
held to what it binds (Appendix B.1.7). Ported from validate_core.py:
Attestation-Binds (every subject is match, differs or absent against the
objects the manifest lists; the manifest bound is this one, a pack manifest
the bundle keeps, or another; Full Match, Semantic Match or fail),
Binds-Report (one line per Attestation; a `fail` verdict fails the bundle
while the Attestation's lifecycle is `active` and is reported otherwise)
and the `binds-vectors` of attestation-vectors.json. Attestations beside a
manifest are read with every bundle and no longer for a pack only
(Beside-Attestation-Files): typed, counted, held to their envelope, and
handed to the tier derivation, the op-law duties, the risk coverage and the
author report. The example folder is held to its envelopes as a bundle is:
a missing one was a note here and is a failure now, as in validate_core.py.
Nineteen vectors came with the change, 684 in all (attestation: 24); the
IFA bundle counts 18 again and the worked pack 3. Before the change this
file passed the five older vectors, counted 17 and 2 and printed no line
about a binding.
Run under PowerShell 7.4 on Linux, with a stand-in for the JSON parser of
the .NET Framework: the lint, then the 684 vectors in 18 families, the five
bundles, the worked pack and the example folder, in structural and in
verification mode (conformance/fixture-trusted-keys.json) - the same counts
and the same dsse and binds lines as validate_core.py, ALL GREEN. Run the
same way on bundles made for the purpose and not kept in the repository:
23 copies of the IFA bundle, all but one changed in one respect each, a
bundle whose Tailoring only the Attestation beside the manifest makes
authority-proven, and two changed example folders, one of them with the
example Attestation as it was shipped before 2026-11-14, which fails twice
here as it does in validate_core.py (the envelope, the binding). There the
counts, the dsse and binds lines and the list of failures were the same as
those of validate_core.py, in both modes. Not run on Windows PowerShell 5.1
when this was written; the workflow runs it there.
NOT EXERCISED by a vector or a bundle of the repository: the lines for a
Semantic Match and for an Attestation that does not bind, and the failure
(every bundle here is a Full Match; the vectors hold the verdict, not the
words); an Attestation without a subject (the schema asks for one, so only
the vector runner could meet it, and no vector has one); a case of the
binds-vectors with an object that does not type; the order of two ids or
two file names that differ in a character beyond U+FFFF. The bundles made
for the run exercised all of these but the two that only a vector can.

Usage: powershell -ExecutionPolicy Bypass -File validate_core.ps1 [bundle-dirs...]
       -VectorsOnly to skip bundles; -TrustedKeys file.json for verification mode;
       -RequireRiskBasis turns uncovered selections into failures (policy switch);
       -RequireAuthors turns the AUTHOR-1..4 lines into failures (policy switch);
       -AsOf YYYY-MM-DD sets the date REVIEW-1 compares a review-due with
       (default: the date of the run, in UTC).
#>
# Every argument without a name is a bundle folder. Until 2026-11-14 only
# the first was: parameters were bound by position, so in
# `validate_core.ps1 a b` the folder `b` was taken for the file of trusted
# keys and the run stopped trying to read it. Found when the end-to-end
# test of attestation-binds handed this file nine folders at once.
[CmdletBinding(PositionalBinding = $false)]
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Bundles = @(), [switch]$VectorsOnly, [string]$TrustedKeys = "",
      [switch]$RequireRiskBasis, [switch]$RequireAuthors, [string]$AsOf = "")

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Numerics
$HERE = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT = (Resolve-Path (Join-Path $HERE "..\..")).Path
$SKILL = Join-Path $ROOT "jascon"
$CONF = Join-Path $SKILL "conformance"
$INV = [System.Globalization.CultureInfo]::InvariantCulture

# Every map is keyed ORDINALLY. PowerShell's @{} and [ordered]@{} compare
# keys case-insensitively, so two ids differing only in case collided here
# while validate_core.py keeps both (D2: ids are string-compared; #45).
function New-Map { return (New-Object System.Collections.Hashtable ([System.StringComparer]::Ordinal)) }
function New-OMap { return (New-Object System.Collections.Specialized.OrderedDictionary ([System.StringComparer]::Ordinal)) }

# Every comparison of two strings is ORDINAL too: code point by code point,
# as validate_core.py compares (D2), with nothing folded and nothing ignored.
# PowerShell's operators cannot do that. -eq, -ne and -contains fold case,
# and all of them, the -c forms included, compare under a culture, which
# ignores U+00AD SOFT HYPHEN and calls canonically equivalent sequences
# equal. With them a Tailoring whose id differed from its content's origin
# by one soft hyphen was read as the authority's own, and an operation
# addressed a statement whose id it did not spell (backlog #58). So no
# operator in this file compares two strings, and
# .github/scripts/lint-twin.ps1 fails the build when one does:
#   against a literal   [string]::Equals($x, 'literal', $ORD)
#                       inline, because a function call costs about thirty
#                       times as much and these sit in the inner loops
#   two values          Str-Eq $a $b       a string equals only a string
#   membership          Str-In $list $x
#   lookup tables       Ord-Table @{...}   a plain @{} folds the case of its keys
# [string]::Equals reads $null as the empty string and a number as its
# digits. Against a literal that is neither empty nor the spelling of a
# number, that cannot make two things equal that are not; everywhere else
# Str-Eq decides.
$ORD = [System.StringComparison]::Ordinal
function Str-Eq($a, $b) {
    if (($a -is [string]) -and ($b -is [string])) { return [string]::Equals($a, $b, $ORD) }
    return (($null -eq $a) -and ($null -eq $b))
}
function Str-In($list, $x) {
    foreach ($y in $list) { if (Str-Eq $y $x) { return $true } }
    return $false
}
function Ord-Table($literal) {
    $m = (New-Map); foreach ($k in $literal.Keys) { $m[[string]$k] = $literal[$k] }
    return $m
}

# ---------------- json -> ordered maps ----------------
# ConvertFrom-Json wraps this same parser and then builds a PSCustomObject per
# object, which costs most of the read and cannot hold two members that
# differ only in case, or an empty member name. Reading the parser's own
# dictionaries is faster and takes every JSON object validate_core.py takes.
Add-Type -AssemblyName System.Web.Extensions
$JSON = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$JSON.MaxJsonLength = [int]::MaxValue
$JSON.RecursionLimit = 1020
function ConvertTo-Map($o) {
    if ($o -is [System.Collections.IDictionary]) {
        $m = (New-OMap)
        foreach ($kv in $o.GetEnumerator()) {
            $x = $kv.Value
            if (($null -eq $x) -or ($x -is [string]) -or ($x -is [System.ValueType])) { $m[[string]$kv.Key] = $x }
            else { $m[[string]$kv.Key] = ConvertTo-Map $x }
        }
        return $m
    }
    if ($o -is [System.Management.Automation.PSCustomObject]) {
        $m = (New-OMap)
        foreach ($p in $o.PSObject.Properties) { $m[$p.Name] = ConvertTo-Map $p.Value }
        return $m
    }
    if (($o -is [System.Collections.IEnumerable]) -and -not ($o -is [string])) {
        $a = New-Object System.Collections.ArrayList
        foreach ($x in $o) {
            if (($null -eq $x) -or ($x -is [string]) -or ($x -is [System.ValueType])) { [void]$a.Add($x) }
            else { [void]$a.Add((ConvertTo-Map $x)) }
        }
        return ,$a
    }
    return $o
}
function Parse-Json([string]$txt) {
    # the parser returns $null for an empty text; JSON has no empty document
    if ($txt.Trim().Length -eq 0) { throw 'not JSON: the text is empty' }
    $v = ConvertTo-Map ($JSON.DeserializeObject($txt))
    return ,$v
}
function Read-Json([string]$path) {
    # a rooted path is read directly (Get-Content costs milliseconds per
    # file); a relative one still goes through PowerShell's own location
    if ([System.IO.Path]::IsPathRooted($path)) { $txt = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8) }
    else { $txt = [string](Get-Content -Raw -Encoding UTF8 $path) }
    $v = Parse-Json $txt
    return ,$v
}
function Is-Map($v) { return ($v -is [System.Collections.IDictionary]) }
function Is-List($v) { return (-not (Is-Map $v)) -and ($v -is [System.Collections.IEnumerable]) -and -not ($v -is [string]) }
function Copy-Deep($v) {
    if (Is-Map $v) { $m = (New-OMap); foreach ($k in $v.Keys) { $m[$k] = Copy-Deep $v[$k] }; return $m }
    if (Is-List $v) { $a = New-Object System.Collections.ArrayList
        foreach ($x in $v) { [void]$a.Add((Copy-Deep $x)) }; return ,$a }
    return $v
}

# ---------------- canonical form (RFC 8785 member ordering) ----------------
# only these need escaping: the quote, the backslash, C0 controls
$ESC_RX = New-Object System.Text.RegularExpressions.Regex '["\\\u0000-\u001f]'
function Esc-Json([string]$s) {
    if (-not $ESC_RX.IsMatch($s)) { return $s }     # the common case: nothing to escape
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $s.ToCharArray()) {
        $c = [int]$ch
        if ($c -eq 34) { [void]$sb.Append('\"') }
        elseif ($c -eq 92) { [void]$sb.Append('\\') }
        elseif ($c -eq 8) { [void]$sb.Append('\b') }
        elseif ($c -eq 9) { [void]$sb.Append('\t') }
        elseif ($c -eq 10) { [void]$sb.Append('\n') }
        elseif ($c -eq 12) { [void]$sb.Append('\f') }
        elseif ($c -eq 13) { [void]$sb.Append('\r') }
        elseif ($c -lt 32) { [void]$sb.Append('\u' + $c.ToString('x4')) }
        else { [void]$sb.Append($ch) }
    }
    return $sb.ToString()
}
function Write-Canonical($v, $sb) {
    if ($v -is [System.Collections.IDictionary]) {
        $keys = New-Object 'System.Collections.Generic.List[string]'
        foreach ($k in $v.Keys) { $keys.Add([string]$k) }
        $keys.Sort([System.StringComparer]::Ordinal)     # UTF-16 code units
        [void]$sb.Append('{')
        $first = $true
        foreach ($k in $keys) {
            if ($first) { $first = $false } else { [void]$sb.Append(',') }
            if ($ESC_RX.IsMatch($k)) { [void]$sb.Append('"').Append((Esc-Json $k)).Append('":') }
            else { [void]$sb.Append('"').Append($k).Append('":') }
            $x = $v[$k]
            if ($x -is [string]) {       # a text leaf needs no call of its own
                if ($ESC_RX.IsMatch($x)) { [void]$sb.Append('"').Append((Esc-Json $x)).Append('"') }
                else { [void]$sb.Append('"').Append($x).Append('"') }
            } else { Write-Canonical $x $sb }
        }
        [void]$sb.Append('}')
        return
    }
    if ($null -eq $v) { [void]$sb.Append('null'); return }
    if ($v -is [string]) {
        if ($ESC_RX.IsMatch($v)) { [void]$sb.Append('"').Append((Esc-Json $v)).Append('"') }
        else { [void]$sb.Append('"').Append($v).Append('"') }
        return
    }
    if ($v -is [bool]) { if ($v) { [void]$sb.Append('true') } else { [void]$sb.Append('false') }; return }
    if ($v -is [System.Collections.IEnumerable]) {
        [void]$sb.Append('[')
        $first = $true
        foreach ($x in $v) {
            if ($first) { $first = $false } else { [void]$sb.Append(',') }
            if ($x -is [string]) {
                if ($ESC_RX.IsMatch($x)) { [void]$sb.Append('"').Append((Esc-Json $x)).Append('"') }
                else { [void]$sb.Append('"').Append($x).Append('"') }
            } else { Write-Canonical $x $sb }
        }
        [void]$sb.Append(']')
        return
    }
    if ($v -is [decimal]) { [void]$sb.Append($v.ToString($INV)); return }
    if ($v -is [double]) { [void]$sb.Append($v.ToString('R', $INV)); return }
    [void]$sb.Append($v.ToString($INV))
}
function Format-Canonical($v) {
    if ($null -eq $v) { return 'null' }
    if ($v -is [string]) {
        if ($ESC_RX.IsMatch($v)) { return '"' + (Esc-Json $v) + '"' }
        return '"' + $v + '"'
    }
    if ($v -is [bool]) { if ($v) { return 'true' } else { return 'false' } }
    $sb = New-Object System.Text.StringBuilder
    Write-Canonical $v $sb
    return $sb.ToString()
}
$SHA = [System.Security.Cryptography.SHA256]::Create()
function Sha256-Hex([byte[]]$bytes) {
    return 'sha256:' + (($SHA.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '')
}
function Canonical($obj) {
    # the semantic form drops the top-level `annotations` only, so a shallow
    # copy of the top level is enough (it was a deep copy of the object)
    if (($obj -is [System.Collections.IDictionary]) -and $obj.Contains('annotations')) {
        $o = (New-OMap)
        foreach ($k in $obj.Keys) {
            if (-not [string]::Equals([string]$k, 'annotations', [System.StringComparison]::Ordinal)) { $o[[string]$k] = $obj[$k] } }
        return Format-Canonical $o
    }
    return Format-Canonical $obj
}
function SDig($obj) { return Sha256-Hex ([System.Text.Encoding]::UTF8.GetBytes((Canonical $obj))) }
function Content-Digest($obj) {
    $x = Copy-Deep $obj
    foreach ($k in @('id', 'version', 'label', 'canonical-alias', 'replaces')) { $x.Remove($k) }
    return SDig $x
}

# ---------------- schema-subset interpreter ----------------
# Consumes the normative kernel schema + stdlib descriptors. Supported
# keywords are exactly those the shipped schemas use; an UNKNOWN validation
# keyword throws (fail-loud, the D10 spirit - never silently pass).
$SCHEMA = Read-Json (Join-Path $SKILL "schemas\jascon-2.0.0.schema.json")
$DEFS = $SCHEMA['$defs']
$IGNORE_KW = @('description', 'title', '$schema', '$id', 'contentEncoding', 'default', 'examples', 'note', '$defs')
$KNOWN_KW = @('$ref', 'allOf', 'anyOf', 'oneOf', 'not', 'if', 'then', 'else', 'const', 'enum', 'type', 'required',
              'properties', 'additionalProperties', 'unevaluatedProperties', 'items',
              'minItems', 'maxItems', 'minLength', 'maxLength', 'minProperties', 'pattern',
              'propertyNames', 'minimum', 'maximum')
# Backlog #68. A `pattern` of a JSON Schema is an ECMA-262 regular expression
# (JSON Schema 2020-12, Core 6.4), and .NET reads two things differently that
# the kernel's patterns use: `$` also matches before one line break that ends
# the value, where ECMA-262 means the end of the value; and `.` matches every
# character but U+000A, where ECMA-262 also excludes U+000D, U+2028 and
# U+2029. So "2026-11-13" followed by a line break was a date here.
# Ecma-Pattern writes the pattern so that .NET reads both as ECMA-262 does:
# `$` becomes \z and `.` the class of what is no line terminator. An escape
# is copied with its next character, and inside [...] nothing is an operator.
# Nothing else is translated: \d, \w, \s and \b keep .NET's meaning, and no
# pattern of the kernel schema or of the standard library uses one.
function Ecma-Pattern([string]$p) {
    $sb = New-Object System.Text.StringBuilder
    $inClass = $false; $i = 0
    while ($i -lt $p.Length) {
        $c = [int]$p[$i]
        if ($c -eq 92) {                                        # \
            [void]$sb.Append($p[$i])
            if (($i + 1) -lt $p.Length) { [void]$sb.Append($p[$i + 1]) }
            $i += 2; continue
        }
        if ($inClass) { if ($c -eq 93) { $inClass = $false }; [void]$sb.Append($p[$i]) }
        elseif ($c -eq 91) { $inClass = $true; [void]$sb.Append($p[$i]) }
        elseif ($c -eq 36) { [void]$sb.Append('\z') }                     # $
        elseif ($c -eq 46) { [void]$sb.Append('[^\n\r\u2028\u2029]') }    # .
        else { [void]$sb.Append($p[$i]) }
        $i++
    }
    return $sb.ToString()
}
function Resolve-Ref([string]$ref) {
    if (-not $ref.StartsWith('#/$defs/')) { throw "unsupported `$ref: $ref" }
    return $DEFS[$ref.Substring(8)]
}
function Collect-Props($sch, $acc) {
    if ($null -eq $sch) { return }
    if ($sch.Contains('$ref')) { Collect-Props (Resolve-Ref $sch['$ref']) $acc }
    if ($sch.Contains('properties')) { foreach ($k in $sch['properties'].Keys) { [void]$acc.Add($k) } }
    if ($sch.Contains('allOf')) { foreach ($s in $sch['allOf']) { Collect-Props $s $acc } }
}
function Type-Is($v, [string]$t) {
    # not a `switch`: it would match the type name without regard to case
    if ([string]::Equals($t, 'object', $ORD)) { return (Is-Map $v) }
    if ([string]::Equals($t, 'string', $ORD)) { return ($v -is [string]) }
    if ([string]::Equals($t, 'array', $ORD)) { return (Is-List $v) }
    if ([string]::Equals($t, 'boolean', $ORD)) { return ($v -is [bool]) }
    if ([string]::Equals($t, 'integer', $ORD)) { return (($v -is [int]) -or ($v -is [long])) -and -not ($v -is [bool]) }
    if ([string]::Equals($t, 'number', $ORD)) { return (($v -is [int]) -or ($v -is [long]) -or ($v -is [double]) -or ($v -is [decimal])) -and -not ($v -is [bool]) }
    if ([string]::Equals($t, 'null', $ORD)) { return ($null -eq $v) }
    throw "unknown type keyword: $t"
}
# SPEED (2026-11-11). The interpreter took 0.16 s per object, four fifths
# of a bundle run. Four changes:
#  - a schema node is read ONCE into a plan: its keywords are held to the
#    subset (still fail-loud, still on first visit) and put in evaluation
#    order - the cheap ones first, so a shape that lacks a required member
#    fails before its subschemas are walked;
#  - type inference tests one object against all eleven shapes, and every
#    shape begins with $ref base: a $ref applied to the object under
#    inference is evaluated once and remembered for the other ten;
#  - the declared-property set of a closed shape is built once per node;
#  - compiled patterns are kept (Regex.IsMatch keeps only fifteen).
# Two comparisons became exact on the way: declared property names and
# const / enum values are compared ordinally (they were -notcontains and
# -ceq, which fold case resp. follow the culture - backlog #58).
$TS_ORDER = @('type', 'required', 'minProperties', 'const', 'enum', 'minLength', 'maxLength', 'pattern',
              'minItems', 'maxItems', 'minimum', 'maximum', 'propertyNames', '$ref', 'allOf', 'anyOf',
              'oneOf', 'not', 'if', 'properties', 'additionalProperties', 'unevaluatedProperties', 'items')
$script:TsPlans = New-Object 'System.Collections.Generic.Dictionary[object,object]'       # schema node -> its keywords, in order
$script:TsDeclared = New-Object 'System.Collections.Generic.Dictionary[object,object]'    # closed node -> declared names
$script:TsRegex = New-Object 'System.Collections.Generic.Dictionary[string,object]' ([System.StringComparer]::Ordinal)
$script:TsTop = $null       # the object under type inference, or $null
$script:TsRefMemo = $null   # $ref -> verdict, for that object only
function New-SchemaPlan($sch) {
    foreach ($kw in $sch.Keys) {
        if ((-not (Str-In $KNOWN_KW $kw)) -and (-not (Str-In $IGNORE_KW $kw))) {
            throw "schema keyword '$kw' outside the documented subset (fail-loud)"
        }
    }
    $list = New-Object System.Collections.ArrayList
    foreach ($kw in $TS_ORDER) { if ($sch.Contains($kw)) { [void]$list.Add($kw) } }
    $plan = $list.ToArray()
    $script:TsPlans[$sch] = $plan
    return ,$plan
}
function Get-Declared($sch) {
    $acc = New-Object System.Collections.ArrayList
    Collect-Props $sch $acc
    $set = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($k in $acc) { [void]$set.Add([string]$k) }
    $script:TsDeclared[$sch] = $set
    return ,$set
}
function Test-Schema($sch, $v) {
    if ($null -eq $sch) { return $true }
    $plan = $null
    if (-not $script:TsPlans.TryGetValue($sch, [ref]$plan)) { $plan = New-SchemaPlan $sch }
    $isMap = $v -is [System.Collections.IDictionary]
    $isStr = $v -is [string]
    $isList = (-not $isMap) -and (-not $isStr) -and ($v -is [System.Collections.IEnumerable])
    foreach ($kw in $plan) {
        if ([string]::Equals($kw, '$ref', $ORD)) {
            $ref = $sch['$ref']
            if (($null -ne $script:TsTop) -and [object]::ReferenceEquals($v, $script:TsTop)) {
                if ($script:TsRefMemo.ContainsKey($ref)) { $r = $script:TsRefMemo[$ref] }
                else { $r = Test-Schema (Resolve-Ref $ref) $v; $script:TsRefMemo[$ref] = $r }
            } else { $r = Test-Schema (Resolve-Ref $ref) $v }
            if (-not $r) { return $false }
        }
        elseif ([string]::Equals($kw, 'type', $ORD)) {
            $t = $sch['type']
            if ([string]::Equals($t, 'object', $ORD)) { if (-not $isMap) { return $false } }
            elseif ([string]::Equals($t, 'string', $ORD)) { if (-not $isStr) { return $false } }
            elseif ([string]::Equals($t, 'array', $ORD)) { if (-not $isList) { return $false } }
            elseif (-not (Type-Is $v $t)) { return $false }
        }
        elseif ([string]::Equals($kw, 'properties', $ORD)) {
            if ($isMap) {
                $props = $sch['properties']
                foreach ($k in $props.Keys) {
                    if ($v.Contains($k)) { if (-not (Test-Schema $props[$k] $v[$k])) { return $false } } } }
        }
        elseif ([string]::Equals($kw, 'required', $ORD)) {
            if ($isMap) { foreach ($k in $sch['required']) { if (-not $v.Contains($k)) { return $false } } }
        }
        elseif ([string]::Equals($kw, 'additionalProperties', $ORD)) {
            if ($isMap) {
                $ap = $sch['additionalProperties']
                $declared = $null
                if (-not $script:TsDeclared.TryGetValue($sch, [ref]$declared)) { $declared = Get-Declared $sch }
                foreach ($k in $v.Keys) {
                    if (-not $declared.Contains([string]$k)) {
                        if ($ap -is [bool]) { if (-not $ap) { return $false } }
                        else { if (-not (Test-Schema $ap $v[$k])) { return $false } } } } }
        }
        elseif ([string]::Equals($kw, 'items', $ORD)) {
            if ($isList) { $is = $sch['items']; foreach ($x in $v) { if (-not (Test-Schema $is $x)) { return $false } } }
        }
        elseif ([string]::Equals($kw, 'allOf', $ORD)) {
            foreach ($s in $sch['allOf']) { if (-not (Test-Schema $s $v)) { return $false } }
        }
        elseif ([string]::Equals($kw, 'enum', $ORD)) {
            $hit = $false
            if ($isStr) {
                foreach ($e in $sch['enum']) {
                    if (($e -is [string]) -and [string]::Equals($v, $e, [System.StringComparison]::Ordinal)) { $hit = $true; break } }
            } else {
                $cv = Format-Canonical $v
                foreach ($e in $sch['enum']) {
                    if ([string]::Equals($cv, (Format-Canonical $e), [System.StringComparison]::Ordinal)) { $hit = $true; break } }
            }
            if (-not $hit) { return $false }
        }
        elseif ([string]::Equals($kw, 'pattern', $ORD)) {
            if ($isStr) {
                $pt = $sch['pattern']; $rx = $null
                if (-not $script:TsRegex.TryGetValue($pt, [ref]$rx)) {
                    $rx = New-Object System.Text.RegularExpressions.Regex (Ecma-Pattern $pt)
                    $script:TsRegex[$pt] = $rx }
                if (-not $rx.IsMatch($v)) { return $false } }
        }
        elseif ([string]::Equals($kw, 'const', $ORD)) {
            if (-not [string]::Equals((Format-Canonical $v), (Format-Canonical $sch['const']), [System.StringComparison]::Ordinal)) { return $false }
        }
        elseif ([string]::Equals($kw, 'minLength', $ORD)) { if ($isStr) { if ($v.Length -lt $sch['minLength']) { return $false } } }
        elseif ([string]::Equals($kw, 'maxLength', $ORD)) { if ($isStr) { if ($v.Length -gt $sch['maxLength']) { return $false } } }
        elseif ([string]::Equals($kw, 'minItems', $ORD)) { if ($isList) { if (@($v).Count -lt $sch['minItems']) { return $false } } }
        elseif ([string]::Equals($kw, 'maxItems', $ORD)) { if ($isList) { if (@($v).Count -gt $sch['maxItems']) { return $false } } }
        elseif ([string]::Equals($kw, 'minProperties', $ORD)) { if ($isMap) { if ($v.Count -lt $sch['minProperties']) { return $false } } }
        elseif ([string]::Equals($kw, 'anyOf', $ORD)) {
            $any = $false
            foreach ($s in $sch['anyOf']) { if (Test-Schema $s $v) { $any = $true; break } }
            if (-not $any) { return $false }
        }
        elseif ([string]::Equals($kw, 'if', $ORD)) {
            if (Test-Schema $sch['if'] $v) {
                if ($sch.Contains('then')) { if (-not (Test-Schema $sch['then'] $v)) { return $false } } }
            elseif ($sch.Contains('else')) { if (-not (Test-Schema $sch['else'] $v)) { return $false } }
        }
        elseif ([string]::Equals($kw, 'unevaluatedProperties', $ORD)) {
            if ($isMap -and ($sch['unevaluatedProperties'] -eq $false)) {
                $declared = $null
                if (-not $script:TsDeclared.TryGetValue($sch, [ref]$declared)) { $declared = Get-Declared $sch }
                foreach ($k in $v.Keys) { if (-not $declared.Contains([string]$k)) { return $false } } }
        }
        elseif ([string]::Equals($kw, 'propertyNames', $ORD)) {
            if ($isMap) { $pn = $sch['propertyNames']; foreach ($k in $v.Keys) { if (-not (Test-Schema $pn ([string]$k))) { return $false } } }
        }
        elseif ([string]::Equals($kw, 'oneOf', $ORD)) {         # exactly one branch holds (CP-CHECK-1: checkObservation)
            $n1 = 0
            foreach ($s in $sch['oneOf']) { if (Test-Schema $s $v) { $n1++ } }
            if ($n1 -ne 1) { return $false }
        }
        elseif ([string]::Equals($kw, 'not', $ORD)) { if (Test-Schema $sch['not'] $v) { return $false } }
        elseif ([string]::Equals($kw, 'minimum', $ORD)) { if (Type-Is $v 'number') { if ($v -lt $sch['minimum']) { return $false } } }
        elseif ([string]::Equals($kw, 'maximum', $ORD)) { if (Type-Is $v 'number') { if ($v -gt $sch['maximum']) { return $false } } }
    }
    return $true
}
$TYPES = @('requirement', 'requirementSet', 'tailoring', 'mapping', 'component',
           'implementation', 'assessment', 'finding', 'attestation', 'risk', 'check')
function Infer-Types($obj) {
    $m = New-Object System.Collections.ArrayList
    $script:TsTop = $obj; $script:TsRefMemo = (New-Map)
    try { foreach ($t in $TYPES) { if (Test-Schema $DEFS[$t] $obj) { [void]$m.Add($t) } } }
    finally { $script:TsTop = $null; $script:TsRefMemo = $null }
    return ,$m
}
function Infer-Single($obj) {
    $m = Infer-Types $obj
    if (@($m).Count -eq 1) { return $m[0] }
    return $null
}

# stdlib facet descriptors (fail-closed registry)
$STDLIB = (New-Map); $STDLIB_DECL = (New-Map)
foreach ($f in (Get-ChildItem (Join-Path $SKILL "schemas\stdlib") -Filter *.json | Sort-Object Name)) {
    $d = Read-Json $f.FullName
    $STDLIB[$d['id']] = $d['schema']
    $STDLIB_DECL[$d['id']] = $d['modifies-semantics']
}

# ---------------- optional-empty rule (D3.3) ----------------
$OPTIONAL_CONTAINERS = @('aliases', 'canonical-alias', 'replaces', 'relations', 'facets',
                         'annotations', 'parameters', 'deviations', 'excludes',
                         'source-scope', 'target-scope', 'evidence-refs', 'statement-refs',
                         'capabilities', 'authorizations', 'actions', 'choices',
                         'threat-refs', 'component-refs', 'treatments', 'risk-refs', 'tailoring-refs',
                         'statement-ids', 'applies-when', 'check-results', 'derived-from')
$OPTIONAL_SET = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
foreach ($k in $OPTIONAL_CONTAINERS) { [void]$OPTIONAL_SET.Add($k) }
function Optional-Empty-Walk($obj, [string]$path, $out) {
    if ($obj -is [System.Collections.IDictionary]) {
        foreach ($k in $obj.Keys) {
            $v = $obj[$k]
            if ($null -eq $v -or $v -is [string]) { continue }
            if ($v -is [System.Collections.IDictionary]) {
                if ($v.Count -eq 0 -and $OPTIONAL_SET.Contains([string]$k)) { [void]$out.Add("$path.$k") }
                Optional-Empty-Walk $v "$path.$k" $out
            } elseif ($v -is [System.Collections.IEnumerable]) {
                if (@($v).Count -eq 0 -and $OPTIONAL_SET.Contains([string]$k)) { [void]$out.Add("$path.$k") }
                Optional-Empty-Walk $v "$path.$k" $out
            }
        }
    } elseif (($obj -is [System.Collections.IEnumerable]) -and -not ($obj -is [string])) {
        $i = 0
        foreach ($v in $obj) {
            if (($null -ne $v) -and -not ($v -is [string]) -and
                (($v -is [System.Collections.IDictionary]) -or ($v -is [System.Collections.IEnumerable]))) {
                Optional-Empty-Walk $v "$path[$i]" $out }
            $i++
        }
    }
}
function Optional-Empty-Violations($obj, [string]$path = '$') {
    $out = New-Object System.Collections.ArrayList
    Optional-Empty-Walk $obj $path $out
    return ,$out
}

# ---------------- the number domain (D3.9, NUMBER-1) ----------------
# A JSON number in a bundle is an integer written in plain digits, of
# magnitude at most 2^53 - 1. Two reasons, one rule. RANGE: beyond 2^53 a
# double no longer holds every integer, so a JavaScript tool reads
# 9007199254740993 as ...992 while this parser keeps it as an Int64 - two
# digests, two verdicts for one file. SPELLING: `1.0`, `1e3` and `-0` are
# second spellings of 1, 1000 and 0; this parser reads 1.0 as a decimal and
# would hash it as written, a JavaScript one as `1`. The rule rejects; it
# never rewrites (D3.4).
#
# Two checks, because the spelling is gone once a text is parsed (-0 arrives
# here as the Int32 0):
#   Number-Spelling-Violations   wherever a bundle file is read
#   Number-Violations            on every object, and in check-verdict
# A fraction is a `decimal`, which is a string.
$NUMBER_MAX = [long]9007199254740991
$NUMBER_MAX_DIGITS = '9007199254740991'
$NUMBER_RULE = 'a JSON number is an integer in plain digits, of magnitude at most 2^53 - 1 (9007199254740991) - no fraction, no exponent, no -0; a number two tools read differently has two digests and two verdicts'
# strings are taken out first, in one call, so that digits inside them are
# never looked at and the loop below sees number tokens only
$JSON_STRING_RX = New-Object System.Text.RegularExpressions.Regex '"[^"\\]*(?:\\.[^"\\]*)*"'
$NUMBER_TOKEN_RX = New-Object System.Text.RegularExpressions.Regex '-?[0-9][0-9.eE+-]*'
$NUMBER_PLAIN_RX = New-Object System.Text.RegularExpressions.Regex '^-?(?:0|[1-9][0-9]*)\z'
function Number-Spelling-Violations([string]$text) {
    # $text: a JSON text. -> the number tokens that break NUMBER-1, as written.
    # The digits are compared as text, so no float takes part in the decision.
    $out = New-Object System.Collections.ArrayList
    $bare = $JSON_STRING_RX.Replace($text, '""')
    foreach ($m in $NUMBER_TOKEN_RX.Matches($bare)) {
        $tok = [string]$m.Value
        $digits = $tok.TrimStart('-')
        if ((-not $NUMBER_PLAIN_RX.IsMatch($tok)) -or [string]::Equals($tok, '-0', [System.StringComparison]::Ordinal) -or ($digits.Length -gt $NUMBER_MAX_DIGITS.Length) -or
            (($digits.Length -eq $NUMBER_MAX_DIGITS.Length) -and ([string]::CompareOrdinal($digits, $NUMBER_MAX_DIGITS) -gt 0))) {
            [void]$out.Add($tok) }
    }
    return ,$out
}
function In-Number-Domain($x) {
    if (($x -is [bool]) -or -not (($x -is [int]) -or ($x -is [long]))) { return $false }
    $n = [long]$x
    return (($n -le $NUMBER_MAX) -and ($n -ge (-$NUMBER_MAX)))
}
function Number-Walk($obj, [string]$path, $out) {
    # a parsed JSON value is null, a string, a bool, a map, a list - or a
    # number, which is the only value type left
    if ($obj -is [System.Collections.IDictionary]) {
        foreach ($k in $obj.Keys) {
            $v = $obj[$k]
            if (($null -eq $v) -or ($v -is [string]) -or ($v -is [bool])) { continue }
            if ($v -is [System.ValueType]) {
                if (-not (In-Number-Domain $v)) { [void]$out.Add("$path.$k = $(Format-Canonical $v)") }
            } else { Number-Walk $v "$path.$k" $out }
        }
    } elseif (($obj -is [System.Collections.IEnumerable]) -and -not ($obj -is [string])) {
        $i = 0
        foreach ($v in $obj) {
            if (($null -ne $v) -and -not ($v -is [string]) -and -not ($v -is [bool])) {
                if ($v -is [System.ValueType]) {
                    if (-not (In-Number-Domain $v)) { [void]$out.Add("$path[$i] = $(Format-Canonical $v)") }
                } else { Number-Walk $v "$path[$i]" $out }
            }
            $i++
        }
    }
}
function Number-Violations($obj, [string]$path = '$') {
    # the backstop for values that never were a text here (vectors)
    $out = New-Object System.Collections.ArrayList
    Number-Walk $obj $path $out
    return ,$out
}
function Number-Problems($raw, $obj) {
    # -> what breaks NUMBER-1 in one bundle file: its bytes if given, else its value
    $bad = New-Object System.Collections.ArrayList
    if ($null -ne $raw) {
        foreach ($t in (Number-Spelling-Violations ([System.Text.Encoding]::UTF8.GetString($raw)))) { [void]$bad.Add("written as $t") } }
    if (($bad.Count -eq 0) -and ($null -ne $obj)) { foreach ($v in (Number-Violations $obj)) { [void]$bad.Add($v) } }
    return ,$bad
}
function Number-Failures([string]$section, [string]$rel, $raw, $obj) {
    $bad = Number-Problems $raw $obj
    if ($bad.Count -gt 0) {
        $more = ''; if ($bad.Count -gt 1) { $more = " (and $($bad.Count - 1) more)" }
        FAIL $section "${rel}: [NUMBER-1] $($bad[0])$more - $NUMBER_RULE" }
}

# ---------------- modality lattice ----------------
$OBL = Ord-Table @{unspecified = 0; may = 1; should = 2; must = 3}
$PRO = Ord-Table @{unspecified = 0; 'should-not' = 1; 'must-not' = 2}
function Modality-Verdict([string]$frm, [string]$to) {
    if (Str-Eq $frm $to) { return 'monotone' }
    if ([string]::Equals($frm, 'unspecified', $ORD)) { return 'monotone' }
    if ([string]::Equals($to, 'unspecified', $ORD)) { return 'easing' }
    if ([string]::Equals($frm, 'may', $ORD) -and [string]::Equals($to, 'may-only', $ORD)) { return 'monotone' }
    if ([string]::Equals($frm, 'may-only', $ORD) -and [string]::Equals($to, 'may', $ORD)) { return 'easing' }
    if ([string]::Equals($frm, 'may-only', $ORD) -or [string]::Equals($to, 'may-only', $ORD)) { return 'axis-change' }
    if ($OBL.ContainsKey($frm) -and $OBL.ContainsKey($to)) {
        if ($OBL[$to] -ge $OBL[$frm]) { return 'monotone' } else { return 'easing' } }
    if ($PRO.ContainsKey($frm) -and $PRO.ContainsKey($to)) {
        if ($PRO[$to] -ge $PRO[$frm]) { return 'monotone' } else { return 'easing' } }
    return 'axis-change'
}

# ---------------- parameter law ----------------
# Two JSON values as validate_core.py's `==` sees them. A string equals only
# the same string. Numbers are equal by value whatever their spelling, and
# Python counts true and false among them, as 1 and 0. Anything else is
# equal when its canonical form is.
function Val-Num($v) {
    if ($v -is [bool]) { if ($v) { return [decimal]1 } else { return [decimal]0 } }
    if (($v -is [int]) -or ($v -is [long]) -or ($v -is [decimal])) { return [decimal]$v }
    return $null
}
function Val-Eq($a, $b) {
    if (($a -is [string]) -or ($b -is [string])) { return (Str-Eq $a $b) }
    $na = Val-Num $a; $nb = Val-Num $b
    if (($null -ne $na) -and ($null -ne $nb)) { return (Str-Eq $na $nb) }
    return [string]::Equals((Format-Canonical $a), (Format-Canonical $b), $ORD)
}
function Val-In($list, $x) {
    foreach ($y in $list) { if (Val-Eq $y $x) { return $true } }
    return $false
}
function Param-Check($decl, $value) {
    $t = $decl['type']
    if ([string]::Equals($t, 'calendar-period', $ORD) -and -not $decl.Contains('calendar-ref')) { return 'invalid' }
    if ($null -eq $value) { return 'invalid' }
    if ([string]::Equals($t, 'choice', $ORD)) {
        $allowed = New-Object System.Collections.ArrayList
        foreach ($c in $decl['choices']) { [void]$allowed.Add($c['value']) }
        if (Is-List $value) {
            if (-not [string]::Equals($decl['cardinality'], 'many', $ORD) -or @($value).Count -eq 0) { return 'invalid' }
            foreach ($x in $value) { if (-not (Val-In $allowed $x)) { return 'deviation-required' } }
            return 'valid'
        }
        if (Val-In $allowed $value) { return 'valid' } else { return 'deviation-required' }
    }
    if ([string]::Equals($t, 'integer', $ORD)) {
        if (-not (In-Number-Domain $value)) { return 'invalid' }      # NUMBER-1: beyond 2^53 two tools read two values
        if ($decl.Contains('min') -and $value -lt $decl['min']) { return 'deviation-required' }
        if ($decl.Contains('max') -and $value -gt $decl['max']) { return 'deviation-required' }
        return 'valid'
    }
    if ([string]::Equals($t, 'decimal', $ORD)) {
        # D3.4 canonical form (rev P10 #37): no leading zeros, no negative
        # zero; bounds compare exactly via [decimal] (double loses precision)
        if (-not ($value -is [string])) { return 'invalid' }
        if (-not [System.Text.RegularExpressions.Regex]::IsMatch($value, '^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)\z')) { return 'invalid' }
        $d = [decimal]::Parse($value, $INV)
        if ($decl.Contains('min') -and $d -lt [decimal]::Parse([string]$decl['min'], $INV)) { return 'deviation-required' }
        if ($decl.Contains('max') -and $d -gt [decimal]::Parse([string]$decl['max'], $INV)) { return 'deviation-required' }
        return 'valid'
    }
    if ([string]::Equals($t, 'elapsed-duration', $ORD) -or [string]::Equals($t, 'calendar-period', $ORD)) {
        $cls = @('days', 'bizdays', 'weeks', 'months', 'years')
        if ([string]::Equals($t, 'elapsed-duration', $ORD)) { $cls = @('seconds', 'minutes', 'hours') }
        if (-not (Is-Map $value) -or -not $value.Contains('num') -or -not $value.Contains('unit')) { return 'invalid' }
        if (-not (Str-In $cls $value['unit'])) { return 'invalid' }
        if ([string]::Equals($decl['tightening'], 'lower', $ORD)) {
            if ($decl.Contains('num') -and (Str-Eq $value['unit'] $decl['unit']) -and $value['num'] -gt $decl['num']) {
                return 'deviation-required' } }
        return 'valid'
    }
    return 'valid'
}

# ---------------- reference closure (#16) ----------------
function Closure-Errors($objs) {
    $errs = New-Object System.Collections.ArrayList
    function Need([string]$oid, [string]$ref, [string]$what) {
        if (-not $objs.Contains($ref)) { [void]$errs.Add("${oid}: closure-required $what does not resolve in-bundle: $ref") }
    }
    foreach ($oid in $objs.Keys) {
        $t = $objs[$oid].t; $o = $objs[$oid].o
        foreach ($ca in @($o['canonical-alias'])) {
            if ($null -eq $ca) { continue }
            if ($objs.Contains($ca['of'])) {
                $tgt = $objs[$ca['of']].o
                if (-not (Str-Eq (Content-Digest $o) (Content-Digest $tgt))) {
                    [void]$errs.Add("${oid}: canonical-alias claims SAME content as $($ca['of']) but content digests differ - a meaning change must use ``replaces`` (backlog #14)") } } }
        if ([string]::Equals($t, 'requirementSet', $ORD)) {
            foreach ($m in @($o['members'])) { if ($null -ne $m) { Need $oid $m['ref'] 'member ref' } }
        } elseif ([string]::Equals($t, 'tailoring', $ORD)) {
            # a Tailoring edge is typed, like a Risk edge (RISK-12): a set-ref
            # that is not a RequirementSet selects nothing, silently; an
            # exclude that is neither a Requirement nor a Set removes nothing
            foreach ($s in @($o['selects'])) {
                if ($null -eq $s -or -not $s.Contains('set-ref')) { continue }
                $sr = [string]$s['set-ref']
                Need $oid $sr 'selects set-ref'
                if ($objs.Contains($sr) -and -not [string]::Equals($objs[$sr].t, 'requirementSet', $ORD)) {
                    [void]$errs.Add("${oid}: selects set-ref resolves to a $($objs[$sr].t), not a RequirementSet: $sr (D13: a selection names a Set - chaining runs on the resolved package, never by reference)") }
            }
            foreach ($e in @($o['excludes'])) {
                if ($null -eq $e) { continue }
                $er = [string]$e['ref']
                Need $oid $er 'excludes ref'
                if ($objs.Contains($er) -and -not [string]::Equals($objs[$er].t, 'requirement', $ORD) -and -not [string]::Equals($objs[$er].t, 'requirementSet', $ORD)) {
                    [void]$errs.Add("${oid}: excludes ref resolves to a $($objs[$er].t), neither a Requirement nor a RequirementSet: $er (D13: an exclusion scopes out requirements - one, or a Set's members)") }
            }
            foreach ($op in @($o['operations'])) {
                if ($null -eq $op) { continue }
                Need $oid $op['requirement-ref'] 'operation requirement-ref'
                if ($objs.Contains($op['requirement-ref']) -and $op.Contains('statement-id')) {
                    $tg = $objs[$op['requirement-ref']]
                    if ([string]::Equals($tg.t, 'requirement', $ORD)) {
                        $sids = @(); foreach ($s in $tg.o['statements']) { $sids += $s['id'] }
                        if (-not (Str-In $sids $op['statement-id'])) {
                            [void]$errs.Add("${oid}: operation statement-id '$($op['statement-id'])' names no statement of $($op['requirement-ref'])") } } } }
        } elseif ([string]::Equals($t, 'implementation', $ORD)) {
            Need $oid $o['component-ref'] 'component-ref'
            Need $oid $o['requirement-ref'] 'requirement-ref'
            foreach ($sb in @($o['satisfied-by'])) {
                if ($null -eq $sb) { continue }
                $inh = $sb['inherited-from']
                if ($null -ne $inh) {
                    if (-not $objs.Contains($inh['component-ref'])) {
                        [void]$errs.Add("${oid}: inherited-from component does not resolve in-bundle: $($inh['component-ref'])")
                    } else {
                        $comp = $objs[$inh['component-ref']].o
                        $auths = @(); foreach ($a in @($comp['authorizations'])) { if ($null -ne $a) { $auths += $a['id'] } }
                        if (-not (Str-In $auths $inh['basis-ref'])) {
                            [void]$errs.Add("${oid}: basis-ref '$($inh['basis-ref'])' names no authorization of $($inh['component-ref']) (D5 edge-local rule)") } } } }
        } elseif ([string]::Equals($t, 'finding', $ORD)) {
            Need $oid $o['assessment-ref'] 'assessment-ref'
            Need $oid $o['requirement-ref'] 'requirement-ref'
            # risk-refs are LANDMARK (the register normally lives in another
            # bundle); like a Mapping scope the edge binds IF the target is
            # present: an in-bundle target must be a Risk (RISK-12)
            foreach ($rr in @($o['risk-refs'])) {
                if ($null -eq $rr) { continue }
                if ($objs.Contains($rr) -and -not [string]::Equals($objs[$rr].t, 'risk', $ORD)) {
                    [void]$errs.Add("${oid}: risk-refs entry resolves in-bundle to a $($objs[$rr].t), not a Risk: $rr (RISK-12: a Risk edge is typed - a mis-aimed ref is a wrong statement, not a loose one)") } }
        } elseif ([string]::Equals($t, 'risk', $ORD)) {
            # RISK-7: the controls a risk leans on are closure-required
            foreach ($tr in @($o['treatments'])) {
                if ($null -eq $tr) { continue }
                $q = [string]$tr['requirement-ref']
                Need $oid $q 'treatments requirement-ref (RISK-7)'
                if ($objs.Contains($q)) {
                    $tg = $objs[$q]
                    if (-not [string]::Equals($tg.t, 'requirement', $ORD)) {
                        [void]$errs.Add("${oid}: treatments requirement-ref resolves to a $($tg.t), not a Requirement: $q (RISK-12: a Risk edge is typed - coverage joins on Requirement ids)")
                    } else {
                        $sids = @(); foreach ($s in $tg.o['statements']) { $sids += $s['id'] }
                        foreach ($sid in @($tr['statement-ids'])) {
                            if ($null -eq $sid) { continue }
                            if (-not (Str-In $sids $sid)) {
                                [void]$errs.Add("${oid}: treatments statement-id '$sid' names no statement of $q (RISK-8: clause precision is addressable or it is prose)") } } } }
            }
            # RISK-7b: the assets at risk are Components of this bundle
            foreach ($cref in @($o['component-refs'])) {
                if ($null -eq $cref) { continue }
                Need $oid $cref 'component-refs (RISK-7)'
                if ($objs.Contains($cref) -and -not [string]::Equals($objs[$cref].t, 'component', $ORD)) {
                    [void]$errs.Add("${oid}: component-refs entry resolves to a $($objs[$cref].t), not a Component: $cref (RISK-12: a Risk edge is typed - the asset at risk is a Component)") } }
            # the Statement(s) of Applicability this risk's treatment belongs to
            foreach ($tref in @($o['tailoring-refs'])) {
                if ($null -eq $tref) { continue }
                Need $oid $tref 'tailoring-refs (RISK-7)'
                if ($objs.Contains($tref) -and -not [string]::Equals($objs[$tref].t, 'tailoring', $ORD)) {
                    [void]$errs.Add("${oid}: tailoring-refs entry resolves to a $($objs[$tref].t), not a Tailoring: $tref (RISK-12: a Risk edge is typed - the scope of a treatment is a Tailoring)") }
            }
            # RISK-13: levels compare within ONE scale and never across (D23)
            if ($o.Contains('rating') -and $o.Contains('residual-rating')) {
                $sa = [string]$o['rating']['scale-ref']; $sb = [string]$o['residual-rating']['scale-ref']
                if (-not (Str-Eq $sa $sb)) {
                    [void]$errs.Add("${oid}: residual-rating is on $sb, rating on $sa (RISK-13: a residual level is what remains of a level - it presupposes a rating, on the same scale)") }
                # ... and so do likelihood and impact, where both sides carry them
                foreach ($part in @('likelihood', 'impact')) {
                    $pa = $o['rating'][$part]; $pr = $o['residual-rating'][$part]
                    if ((Is-Map $pa) -and (Is-Map $pr)) {
                        $ua = [string]$pa['scale-ref']; $ub = [string]$pr['scale-ref']
                        if (-not (Str-Eq $ua $ub)) {
                            [void]$errs.Add("${oid}: residual-rating $part is on $ub, rating $part on $ua (RISK-13: a residual level is what remains of a level - it presupposes a rating, on the same scale)") }
                    }
                }
            }
        } elseif ([string]::Equals($t, 'mapping', $ORD)) {
            foreach ($side in @('source', 'target')) {
                $ref = $o["$side-ref"]
                if ($objs.Contains($ref) -and [string]::Equals($objs[$ref].t, 'requirement', $ORD)) {
                    $sids = @(); foreach ($s in $objs[$ref].o['statements']) { $sids += $s['id'] }
                    foreach ($sc in @($o["$side-scope"])) {
                        if ($null -eq $sc) { continue }
                        $sid = ([string]$sc).Split(':', 2)[1]
                        if (-not (Str-In $sids $sid)) {
                            [void]$errs.Add("${oid}: $side-scope '$sc' names no statement of the in-bundle endpoint") } } } }
        }
    }
    # membership graphs are DAGs (D21; P10 #39): overlap is legal, cycles
    # are not - naive baseline expansion / nearest-Set search would loop.
    $color = (New-Map)
    foreach ($root in @($objs.Keys)) {
        if (-not [string]::Equals($objs[$root].t, 'requirementSet', $ORD) -or $color.ContainsKey($root)) { continue }
        $refs0 = New-Object System.Collections.ArrayList
        foreach ($m in @($objs[$root].o['members'])) { if ($null -ne $m) { [void]$refs0.Add([string]$m['ref']) } }
        $stack = New-Object System.Collections.ArrayList
        [void]$stack.Add(@{sid = $root; refs = $refs0; i = 0})
        $color[$root] = 1
        while ($stack.Count -gt 0) {
            $fr = $stack[$stack.Count - 1]
            if ($fr['i'] -ge $fr['refs'].Count) { $color[$fr['sid']] = 2; $stack.RemoveAt($stack.Count - 1); continue }
            $adv = $fr['refs'][$fr['i']]
            $fr['i'] = $fr['i'] + 1
            if (-not $objs.Contains($adv) -or -not [string]::Equals($objs[$adv].t, 'requirementSet', $ORD)) { continue }
            if ($color.ContainsKey($adv) -and $color[$adv] -eq 1) {
                $names = @(); foreach ($f in $stack) { $names += $f['sid'] }; $names += $adv
                [void]$errs.Add("$($fr['sid']): RequirementSet membership cycle: $($names -join ' -> ') (D21: membership graphs are acyclic; P10 #39)")
            } elseif (-not $color.ContainsKey($adv)) {
                $color[$adv] = 1
                $r2 = New-Object System.Collections.ArrayList
                foreach ($m in @($objs[$adv].o['members'])) { if ($null -ne $m) { [void]$r2.Add([string]$m['ref']) } }
                [void]$stack.Add(@{sid = $adv; refs = $r2; i = 0})
            }
        }
    }
    return ,$errs
}

# ---------------- facet enforcement (#17) ----------------
function Facet-Errors($pairs, $pinned) {
    $errs = New-Object System.Collections.ArrayList
    foreach ($pair in $pairs) {
        $pth = $pair[0]; $obj = $pair[1]
        $facets = $obj['facets']
        if ($null -eq $facets) { continue }
        foreach ($key in $facets.Keys) {
            $base = $key.Substring(0, $key.LastIndexOf('@'))
            if ($key.StartsWith('private:') -or $base.StartsWith('private:')) { continue }
            $sch = $STDLIB[$base]
            if ($null -eq $sch) { $sch = $pinned[$base] }
            if ($null -eq $sch) {
                [void]$errs.Add("${pth}: unregistered facet '$key' - not stdlib, not pinned in the manifest, not private: (dangerous-by-default, D10)")
                continue
            }
            if (-not (Test-Schema $sch $facets[$key])) {
                [void]$errs.Add("${pth}: facet '$key' payload violates its schema") }
        }
    }
    return ,$errs
}

# ---------------- Ed25519 (RFC 8032) over BigInteger ----------------
$BI = [System.Numerics.BigInteger]
$EDP = ([System.Numerics.BigInteger]::Pow(2, 255)) - 19
$EDL = ([System.Numerics.BigInteger]::Pow(2, 252)) + [System.Numerics.BigInteger]::Parse('27742317777372353535851937790883648493')
function BMod($a, $m) { $r = $a % $m; if ($r.Sign -lt 0) { $r = $r + $m }; return $r }
$EDD = BMod (-121665 * [System.Numerics.BigInteger]::ModPow(121666, $EDP - 2, $EDP)) $EDP
function Ed-Add($P, $Q) {
    $a = BMod (($P[1] - $P[0]) * ($Q[1] - $Q[0])) $EDP
    $b = BMod (($P[1] + $P[0]) * ($Q[1] + $Q[0])) $EDP
    $c = BMod (2 * $P[3] * $Q[3] * $EDD) $EDP
    $d = BMod (2 * $P[2] * $Q[2]) $EDP
    $e = $b - $a; $f = $d - $c; $g = $d + $c; $h = $b + $a
    return @((BMod ($e * $f) $EDP), (BMod ($g * $h) $EDP), (BMod ($f * $g) $EDP), (BMod ($e * $h) $EDP))
}
function Ed-Mul($s, $P) {
    $Q = @([System.Numerics.BigInteger]::Zero, [System.Numerics.BigInteger]::One, [System.Numerics.BigInteger]::One, [System.Numerics.BigInteger]::Zero)
    $n = $s
    while ($n -gt [System.Numerics.BigInteger]::Zero) {
        if (($n % 2) -eq [System.Numerics.BigInteger]::One) { $Q = Ed-Add $Q $P }
        $P = Ed-Add $P $P
        $n = $n / 2
    }
    return $Q
}
function BI-FromLE([byte[]]$b) {
    $x = New-Object byte[] ($b.Length + 1)
    [Array]::Copy($b, $x, $b.Length)
    return New-Object System.Numerics.BigInteger(,$x)
}
function BI-ToLE32($n) {
    $b = $n.ToByteArray()
    $out = New-Object byte[] 32
    [Array]::Copy($b, $out, [Math]::Min($b.Length, 32))
    return ,$out
}
function Ed-Compress($P) {
    $zi = [System.Numerics.BigInteger]::ModPow($P[2], $EDP - 2, $EDP)
    $x = BMod ($P[0] * $zi) $EDP
    $y = BMod ($P[1] * $zi) $EDP
    if (($x % 2) -eq [System.Numerics.BigInteger]::One) { $y = $y + ([System.Numerics.BigInteger]::Pow(2, 255)) }
    return BI-ToLE32 $y
}
function Ed-Decompress([byte[]]$b) {
    $y = BI-FromLE $b
    $sign = $y -shr 255
    $y = $y - (($y -shr 255) * ([System.Numerics.BigInteger]::Pow(2, 255)))
    if ($y -ge $EDP) { return $null }
    $xx = BMod (($y * $y - 1) * [System.Numerics.BigInteger]::ModPow((BMod ($EDD * $y * $y + 1) $EDP), $EDP - 2, $EDP)) $EDP
    $x = [System.Numerics.BigInteger]::ModPow($xx, ($EDP + 3) / 8, $EDP)
    if ((BMod ($x * $x - $xx) $EDP) -ne [System.Numerics.BigInteger]::Zero) {
        $x = BMod ($x * [System.Numerics.BigInteger]::ModPow(2, ($EDP - 1) / 4, $EDP)) $EDP
        if ((BMod ($x * $x - $xx) $EDP) -ne [System.Numerics.BigInteger]::Zero) { return $null } }
    if (($x % 2) -ne $sign) { $x = $EDP - $x }
    return @($x, $y, [System.Numerics.BigInteger]::One, (BMod ($x * $y) $EDP))
}
$EDB = Ed-Decompress (BI-ToLE32 (BMod (4 * [System.Numerics.BigInteger]::ModPow(5, $EDP - 2, $EDP)) $EDP))
$SHA512 = [System.Security.Cryptography.SHA512]::Create()
function Ed-Verify([byte[]]$pub, [byte[]]$msg, [byte[]]$sig) {
    if ($sig.Length -ne 64 -or $pub.Length -ne 32) { return $false }
    $A = Ed-Decompress $pub
    if ($null -eq $A) { return $false }
    $Rb = $sig[0..31]; $sb = $sig[32..63]
    $s = BI-FromLE $sb
    if ($s -ge $EDL) { return $false }
    $R = Ed-Decompress $Rb
    if ($null -eq $R) { return $false }
    $km = New-Object byte[] (64 + $msg.Length)
    [Array]::Copy($Rb, 0, $km, 0, 32); [Array]::Copy($pub, 0, $km, 32, 32)
    [Array]::Copy($msg, 0, $km, 64, $msg.Length)
    $k = BMod (BI-FromLE ($SHA512.ComputeHash($km))) $EDL
    $lhs = Ed-Compress (Ed-Mul $s $EDB)
    $rhs = Ed-Compress (Ed-Add $R (Ed-Mul $k $A))
    return (@(Compare-Object $lhs $rhs -SyncWindow 0).Length -eq 0)
}
$DSSE_PT = 'application/vnd.jascon.attestation+json'
function PAE([byte[]]$payload) {
    $t = [System.Text.Encoding]::ASCII.GetBytes($DSSE_PT)
    $head = [System.Text.Encoding]::ASCII.GetBytes('DSSEv1 ' + $t.Length + ' ')
    $mid = [System.Text.Encoding]::ASCII.GetBytes(' ' + $payload.Length + ' ')
    $out = New-Object byte[] ($head.Length + $t.Length + $mid.Length + $payload.Length)
    [Array]::Copy($head, 0, $out, 0, $head.Length)
    [Array]::Copy($t, 0, $out, $head.Length, $t.Length)
    [Array]::Copy($mid, 0, $out, $head.Length + $t.Length, $mid.Length)
    [Array]::Copy($payload, 0, $out, $head.Length + $t.Length + $mid.Length, $payload.Length)
    return ,$out
}
function Hex-Bytes([string]$hex) {
    $out = New-Object byte[] ($hex.Length / 2)
    for ($i = 0; $i -lt $out.Length; $i++) { $out[$i] = [Convert]::ToByte($hex.Substring($i * 2, 2), 16) }
    return ,$out
}
function Verify-Envelope($env, $att, $trusted) {
    if (-not (Is-Map $env)) { return @('error', 'envelope unreadable') }
    if (-not [string]::Equals($env['payloadType'], $DSSE_PT, $ORD)) { return @('error', 'wrong payloadType') }
    try { $payload = [Convert]::FromBase64String($env['payload']) }
    catch { return @('error', 'payload is not valid base64') }
    $canon = [System.Text.Encoding]::UTF8.GetBytes((Canonical $att))
    if (@(Compare-Object $payload $canon -SyncWindow 0).Length -ne 0) {
        return @('error', "payload != the Attestation's canonical form (attestation-binds)") }
    $key = $null
    if ($null -ne $trusted) { $key = $trusted[$att['signer']] }
    if ($null -eq $key) { return @('unverified', 'no trusted key supplied for the signer') }
    $pae = PAE $payload
    foreach ($sg in @($env['signatures'])) {
        if ($null -eq $sg) { continue }
        try {
            if (Ed-Verify (Hex-Bytes $key) $pae ([Convert]::FromBase64String($sg['sig']))) {
                return @('verified', '') }
        } catch { }
    }
    return @('error', 'no signature verifies under the trusted key (Ed25519)')
}

# ---------------- tier derivation (#19, D13 rev 4, #24) ----------------
function Uri-Origin([string]$u) {
    $p = $u.Split('/')
    if ($u.StartsWith('http') -and $p.Length -ge 3) { return ($p[0..2] -join '/') }
    return $u
}
function Derive-Tier($tobj, $objs, $envelopes, $trusted) {
    $origins = New-Object System.Collections.ArrayList
    function Add-Origin([string]$x) { if (-not (Str-In $origins $x)) { [void]$origins.Add($x) } }
    function Set-Member-Origins([string]$sid, [int]$depth) {
        $tgt = $null
        if ($objs.Contains($sid)) { $tgt = $objs[$sid] }
        $hasMembers = $false
        if ($null -ne $tgt -and [string]::Equals($tgt.t, 'requirementSet', $ORD)) {
            if (@($tgt.o['members']).Count -gt 0) { $hasMembers = $true } }
        if ($depth -gt 4 -or -not $hasMembers) { Add-Origin (Uri-Origin $sid); return }
        foreach ($m in $tgt.o['members']) {
            $mt = $null
            if ($objs.Contains($m['ref'])) { $mt = $objs[$m['ref']] }
            if ($null -ne $mt -and [string]::Equals($mt.t, 'requirementSet', $ORD)) { Set-Member-Origins $m['ref'] ($depth + 1) }
            else { Add-Origin (Uri-Origin $m['ref']) }
        }
    }
    foreach ($s in @($tobj['selects'])) {
        if ($null -eq $s) { continue }
        if ($s.Contains('set-ref')) { Set-Member-Origins $s['set-ref'] 0 }
        else { Add-Origin '<predicate>' }
    }
    foreach ($op in @($tobj['operations'])) {
        if ($null -ne $op) { Add-Origin (Uri-Origin $op['requirement-ref']) }
    }
    [void]$origins.Remove('')
    $contentOrigin = $null
    if (@($origins).Count -eq 1 -and -not (Str-In $origins '<predicate>')) { $contentOrigin = $origins[0] }
    $claimed = ($null -ne $contentOrigin) -and (Str-Eq (Uri-Origin $tobj['id']) $contentOrigin)
    if ($null -ne $contentOrigin) {
        foreach ($oid in $objs.Keys) {
            $t = $objs[$oid].t; $o = $objs[$oid].o
            if (-not [string]::Equals($t, 'attestation', $ORD)) { continue }
            if (-not (Str-Eq (Uri-Origin ([string]$o['signer'])) $contentOrigin)) { continue }
            foreach ($subj in @($o['subject-semantic-digests'])) {
                if ($null -eq $subj -or -not (Is-Map $subj)) { continue }
                if ((Str-Eq $subj['id'] $tobj['id']) -and (Str-Eq $subj['semantic-digest'] (SDig $tobj))) {
                    if ($null -ne $trusted) {
                        $env = $null
                        if ($null -ne $envelopes -and $o.Contains('envelope-ref')) { $env = $envelopes[$o['envelope-ref']] }
                        $st = 'error'
                        if ($null -ne $env) { $st = (Verify-Envelope $env $o $trusted)[0] }
                        if (-not [string]::Equals($st, 'verified', $ORD)) { continue }
                    }
                    return 'authority-proven'
                }
            }
        }
    }
    if ($claimed) { return 'authority-claimed' } else { return 'consumer' }
}

# ---------------- op-law duties (D13 + #19/#24) ----------------
function Duty-Errors($objs, $pinnedDecl, $envelopes, $trusted) {
    $errs = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) {
        if (-not [string]::Equals($objs[$oid].t, 'tailoring', $ORD)) { continue }
        $tobj = $objs[$oid].o
        $tier = Derive-Tier $tobj $objs $envelopes $trusted
        $seenT = New-Object System.Collections.ArrayList
        foreach ($op in @($tobj['operations'])) {
            if ($null -eq $op) { continue }
            # D13: two operations addressing the same target = validation
            # error (P10 #30 - was vector-only)
            $tkey = "$($op['requirement-ref'])|$($op['statement-id'])|$($op['parameter'])|$($op['field'])|$($op['facet'])"
            if (Str-In $seenT $tkey) {
                [void]$errs.Add("${oid}: two operations address the same target ($tkey) within one Tailoring (D13: override rides Tailoring-of-Tailoring chaining, never in-place; P10 #30)")
            }
            [void]$seenT.Add($tkey)
            $hasDev = $op.Contains('deviation') -or $op.Contains('deviation-ref')
            $duty = $null
            $kind = $op['op']
            if ([string]::Equals($kind, 'set-modality', $ORD)) {
                if ($objs.Contains($op['requirement-ref']) -and [string]::Equals($objs[$op['requirement-ref']].t, 'requirement', $ORD)) {
                    $stmt = $null
                    foreach ($s in $objs[$op['requirement-ref']].o['statements']) {
                        if (Str-Eq $s['id'] $op['statement-id']) { $stmt = $s; break } }
                    if ($null -ne $stmt) {
                        $v = Modality-Verdict $stmt['modality'] $op['modality']
                        if (-not [string]::Equals($v, 'monotone', $ORD)) { $duty = "non-monotone set-modality ($v)" } } }
            } elseif ([string]::Equals($kind, 'replace-prose', $ORD)) {
                if ([string]::Equals($op['intent'], 'substantive', $ORD)) { $duty = 'substantive replace-prose' }
            } elseif ([string]::Equals($kind, 'attach-facet', $ORD) -or [string]::Equals($kind, 'detach-facet', $ORD)) {
                $fid = ([string]$op['facet'])
                $base = $fid
                if ($base.Contains('@')) { $base = $base.Substring(0, $base.LastIndexOf('@')) }
                if ($fid.StartsWith('private:') -or $base.StartsWith('private:')) {
                    # modifies-semantics [] by definition (D10)
                } elseif ($STDLIB_DECL.ContainsKey($base) -or ($null -ne $pinnedDecl -and $pinnedDecl.ContainsKey($base))) {
                    $decl = $STDLIB_DECL[$base]
                    if ($null -eq $decl -and $null -ne $pinnedDecl) { $decl = $pinnedDecl[$base] }
                    if ($null -ne $decl -and @($decl).Count -gt 0) { $duty = "$kind of a semantics-bearing facet" }
                } else {
                    # neither stdlib nor pinned nor private: (P10 #29)
                    [void]$errs.Add("${oid}: $kind references facet '$fid' that is neither stdlib, nor pinned in the manifest, nor private: (dangerous-by-default, D10; P10 #29)")
                }
            } elseif ([string]::Equals($kind, 'set-parameter', $ORD)) {
                $pdecl = $null
                if ($objs.Contains($op['requirement-ref']) -and [string]::Equals($objs[$op['requirement-ref']].t, 'requirement', $ORD)) {
                    foreach ($s in $objs[$op['requirement-ref']].o['statements']) {
                        if (-not (Str-Eq $s['id'] $op['statement-id'])) { continue }
                        foreach ($p in @($s['parameters'])) {
                            if ($null -ne $p -and (Str-Eq $p['name'] $op['parameter'])) { $pdecl = $p } } } }
                if ($null -ne $pdecl) {
                    $verdict = Param-Check $pdecl $op['value']
                    if ([string]::Equals($verdict, 'invalid', $ORD)) {
                        [void]$errs.Add("${oid}: set-parameter '$($op['parameter'])' value fails the declared type/bounds (D13; not Deviation-escapable)")
                    } elseif ([string]::Equals($verdict, 'deviation-required', $ORD)) {
                        $duty = 'out-of-bounds / against-tightening set-parameter' } }
            } elseif ([string]::Equals($kind, 'remove-relation', $ORD)) {
                $rel = $op['relation']
                if ((Is-Map $rel) -and [string]::Equals($rel['type'], 'required', $ORD)) { $duty = 'remove-relation of a ``required`` edge' }
            }
            if ($null -ne $duty -and -not $hasDev -and [string]::Equals($tier, 'consumer', $ORD)) {
                [void]$errs.Add("${oid}: $duty without a Deviation at consumer tier (derived tier: $tier; B.1.6/D13 rev 2)")
            }
        }
    }
    return ,$errs
}

# ---------------- composition (D3.5) ----------------
function Semver([string]$v) {
    # the digits 0-9 and \z: .NET's \d also takes the digits of other scripts, which [int] then
    # cannot read, and its $ also matches before a final line break (#68)
    $m = [System.Text.RegularExpressions.Regex]::Match($v, '^([0-9]+)\.([0-9]+)\.([0-9]+)\z')
    if (-not $m.Success) { return $null }
    return @([int]$m.Groups[1].Value, [int]$m.Groups[2].Value, [int]$m.Groups[3].Value)
}
function Compose($aObjs, $aPins, $bObjs, $bPins) {
    $errors = New-Object System.Collections.ArrayList
    $resolutions = (New-OMap)
    $all = New-Object System.Collections.ArrayList
    foreach ($k in $aPins.Keys) { if (-not (Str-In $all $k)) { [void]$all.Add($k) } }
    foreach ($k in $bPins.Keys) { if (-not (Str-In $all $k)) { [void]$all.Add($k) } }
    $sorted = @($all); [Array]::Sort($sorted, [System.StringComparer]::Ordinal)
    foreach ($fid in $sorted) {
        $pa = $aPins[$fid]; $pb = $bPins[$fid]
        if ($null -ne $pa -and $null -ne $pb) {
            $sa = Semver $pa['version']; $sb = Semver $pb['version']
            if ($null -eq $sa -or $null -eq $sb) {
                [void]$errors.Add("${fid}: non-semver pin ($($pa['version']) / $($pb['version'])) - the registry policy is semver (D3.5)")
                continue
            }
            if ([int]$sa[0] -ne [int]$sb[0]) {
                [void]$errors.Add("${fid}: major lines $($pa['version']) vs $($pb['version']) are incompatible (D3.5; reported, never a silent pick)")
                continue
            }
            $win = $pb
            if (($sa[1] -gt $sb[1]) -or ([int]$sa[1] -eq [int]$sb[1] -and $sa[2] -ge $sb[2])) { $win = $pa }
            $resolutions[$fid] = $win['version']
            $sch = $win['schema']
            if ($null -eq $sch) { $sch = [ordered]@{type = 'object'} }
            foreach ($side in @(@('A', $aObjs), @('B', $bObjs))) {
                foreach ($pair in $side[1]) {
                    $o = $pair[1]
                    if ($null -eq $o['facets']) { continue }
                    foreach ($key in $o['facets'].Keys) {
                        $base = $key.Substring(0, $key.LastIndexOf('@'))
                        if (-not (Str-Eq $base $fid)) { continue }
                        if (-not (Test-Schema $sch $o['facets'][$key])) {
                            [void]$errors.Add("${fid}: $($side[0]) $($pair[0]): payload fails re-validation under the resolved $($win['version'])") } } } }
        } else {
            $win = $pa; if ($null -eq $win) { $win = $pb }
            $resolutions[$fid] = $win['version']
        }
    }
    $aIds = (New-Map)
    foreach ($pair in $aObjs) { $aIds[$pair[0]] = $pair[1] }
    foreach ($pair in $bObjs) {
        if ($aIds.ContainsKey($pair[0])) {
            $oa = $aIds[$pair[0]]; $ob = $pair[1]
            if (-not (Str-Eq $oa['version'] $ob['version'])) {
                [void]$errors.Add("$($pair[0]): composed at two versions ($($oa['version']) vs $($ob['version'])) - cross-version resolution needs the lineage machinery, REPORTED")
            } elseif (-not (Str-Eq (SDig $oa) (SDig $ob))) {
                [void]$errors.Add("$($pair[0]): same id + version but DIFFERENT semantic digests - divergent twins (reported, never silently picked)") } } }
    return @($resolutions, $errors)
}

# ---------------- conditional-apply (B.1.8) ----------------
function Path-Get($obj, [string]$path, $objs) {
    $hops = $path.Split([string[]]@('->'), [System.StringSplitOptions]::None)
    if ($hops.Length -gt 2) { return @('error', "path '$path' exceeds the one-hop budget (B.2)") }
    $cur = $obj
    for ($i = 0; $i -lt $hops.Length; $i++) {
        if ($i -eq 1) {
            $tgt = $null
            if (($cur -is [string]) -and $objs.Contains($cur)) { $tgt = $objs[$cur] }
            if ($null -eq $tgt) { return @('error', "reference hop '$($hops[0])' does not resolve in-bundle") }
            $cur = $tgt.o
        }
        foreach ($part in $hops[$i].Trim().Split('.')) {
            if (Str-Eq $part '') { continue }
            if ((Is-Map $cur) -and $cur.Contains($part)) { $cur = $cur[$part] }
            else { return @('absent', $null) }
        }
    }
    return @('ok', $cur)
}
function Eval-Predicate($pred, $obj, $objs) {
    $kinds = New-Object System.Collections.ArrayList
    foreach ($k in @('field-equals', 'param-equals', 'present')) { if ($pred.Contains($k)) { [void]$kinds.Add($k) } }
    $boolean = $false
    foreach ($k in @('and', 'or', 'not')) { if ($pred.Contains($k)) { $boolean = $true } }
    if (@($kinds).Count -ne 1 -or $boolean) {
        return @('error', 'trigger must be exactly ONE predicate - no nesting, no boolean composition (B.2)') }
    $k = $kinds[0]; $a = $pred[$k]
    if ([string]::Equals($k, 'field-equals', $ORD)) {
        $r = Path-Get $obj $a['path'] $objs
        if ([string]::Equals($r[0], 'error', $ORD)) { return @('error', $r[1]) }
        if ([string]::Equals($r[0], 'absent', $ORD)) { return @('holds-not', "path '$($a['path'])' absent") }
        if (Str-Eq (Format-Canonical $r[1]) (Format-Canonical $a['value'])) {
            return @('holds', "path '$($a['path'])' matched") }
        return @('holds-not', "path '$($a['path'])' differs")
    }
    if ([string]::Equals($k, 'param-equals', $ORD)) {
        foreach ($s in @($obj['statements'])) {
            if ($null -eq $s) { continue }
            foreach ($p in @($s['parameters'])) {
                if ($null -eq $p) { continue }
                if (Str-Eq $p['name'] $a['name']) {
                    if (-not $p.Contains('default')) {
                        return @('error', "parameter '$($a['name'])' declared but UNBOUND - its own error via prose-params-resolve, never silently false (B.2)") }
                    if (Str-Eq (Format-Canonical $p['default']) (Format-Canonical $a['value'])) {
                        return @('holds', "param '$($a['name'])' matched") }
                    return @('holds-not', "param '$($a['name'])' differs") } } }
        return @('holds-not', "no parameter '$($a['name'])' declared")
    }
    $r = Path-Get $obj $a['path'] $objs
    if ([string]::Equals($r[0], 'error', $ORD)) { return @('error', $r[1]) }
    if ([string]::Equals($r[0], 'ok', $ORD)) { return @('holds', "path '$($a['path'])' present") }
    return @('holds-not', "path '$($a['path'])' absent")
}
function Conditional-Apply($inst, $objs) {
    $errs = New-Object System.Collections.ArrayList
    $enf = $inst['enforcement']; $prim = $enf['primitive']
    $keys = @($objs.Keys | ForEach-Object { [string]$_ }); [Array]::Sort($keys, [System.StringComparer]::Ordinal)
    foreach ($oid in $keys) {
        $o = $objs[$oid].o
        $r = Eval-Predicate $inst['trigger'] $o $objs
        if ([string]::Equals($r[0], 'error', $ORD)) {
            [void]$errs.Add("FAIL [conditional-apply:$($inst['instance-id'])] on $oid`n  trigger: malformed/unevaluable: $($r[1])`n  rationale: $($inst['rationale'])")
            continue }
        if (-not [string]::Equals($r[0], 'holds', $ORD)) { continue }
        $detail = $null
        if ([string]::Equals($prim, 'param-bounds', $ORD)) {
            $decl = [ordered]@{type = $enf['type']}
            if ($null -eq $decl['type']) { $decl['type'] = 'integer' }
            foreach ($kk in @('min', 'max', 'unit', 'num', 'tightening', 'calendar-ref', 'choices', 'cardinality')) {
                if ($enf.Contains($kk)) { $decl[$kk] = $enf[$kk] } }
            $found = $false
            foreach ($s in @($o['statements'])) {
                if ($null -eq $s) { continue }
                foreach ($p in @($s['parameters'])) {
                    if ($null -eq $p) { continue }
                    if ((Str-Eq $p['name'] $enf['parameter']) -and $p.Contains('default')) {
                        $found = $true
                        $v = Param-Check $decl $p['default']
                        if (-not [string]::Equals($v, 'valid', $ORD)) {
                            $detail = "parameter '$($enf['parameter'])' value outside the enforced bounds ($v)" } } } }
            if (-not $found) { $detail = "parameter '$($enf['parameter'])' not bound on any statement" }
        } elseif ([string]::Equals($prim, 'code-from', $ORD)) {
            $pg = Path-Get $o $enf['path'] $objs
            $inCodes = $false
            if ([string]::Equals($pg[0], 'ok', $ORD)) {
                foreach ($c in $enf['codes']) { if (Str-Eq (Format-Canonical $c) (Format-Canonical $pg[1])) { $inCodes = $true } } }
            if (-not $inCodes) { $detail = "path '$($enf['path'])' not in the declared code list" }
        } else {
            $detail = "unknown enforcement primitive '$prim'"
        }
        if ($null -ne $detail) {
            [void]$errs.Add("FAIL [conditional-apply:$($inst['instance-id'])] on $oid`n  trigger: $($r[1]) held; enforcement [$prim] failed: $detail`n  rationale: $($inst['rationale'])") }
    }
    return ,$errs
}

# ---------------- runner scaffolding ----------------
# ---------------- RISK-1..6: the schema enforces, this names (CP-RISK-1) ----------------
# The six shape rules are schema conditionals, so the schema-subset
# interpreter already refuses the object. This returns the violated rule
# ids so a failure can name its rule (Ch. 15.4) and so risk-vectors.json
# can hold every implementation to `expected-rule` instead of to one
# library's message text. It never ACCEPTS anything; the schema decides.
function Risk-Rule-Violations($o) {
    $out = New-Object System.Collections.ArrayList
    if (-not (Is-Map $o)) { return ,$out }
    $missing = $false
    foreach ($k in @('scenario', 'owner-ref', 'state')) { if (-not $o.Contains($k)) { $missing = $true } }
    if ($missing) { [void]$out.Add('RISK-1') }
    $st = $o['state']; $tr = $o['treatment']
    if (([string]::Equals($st, 'assessed', $ORD) -or [string]::Equals($st, 'treated', $ORD)) -and -not $o.Contains('rating')) { [void]$out.Add('RISK-2') }
    if ([string]::Equals($st, 'treated', $ORD) -and (-not $o.Contains('treatment') -or -not $o.Contains('acceptance'))) { [void]$out.Add('RISK-3') }
    if ([string]::Equals($tr, 'modify', $ORD) -and -not $o.Contains('treatments')) { [void]$out.Add('RISK-4') }
    if ([string]::Equals($tr, 'share', $ORD) -and -not $o.Contains('shared-with-ref')) { [void]$out.Add('RISK-5') }
    if ([string]::Equals($tr, 'retain', $ORD) -and -not $o.Contains('acceptance')) { [void]$out.Add('RISK-6') }
    if ($o.Contains('residual-rating') -and -not $o.Contains('rating')) { [void]$out.Add('RISK-13') }
    return ,$out
}

# ---------------- B.1.9 risk-coverage (CP-RISK-1) ----------------
function Sorted-Ordinal($list) {
    $a = @($list | ForEach-Object { [string]$_ })
    [Array]::Sort($a, [System.StringComparer]::Ordinal)
    return ,$a
}
# The order of Python's sorted(): by code point. It is the ordinal order
# except where a name has a character beyond U+FFFF, which UTF-16 writes as
# two code units from D800 on and so puts before U+E000..U+FFFF. Used only
# where validate_core.py sorts that way and the order is printed or recorded;
# everything else in this file sorts with Sorted-Ordinal, as by_code_unit()
# does there. The key is the UTF-32 form, big end first, written in hex.
function Sorted-CodePoint($list) {
    $a = @($list | ForEach-Object { [string]$_ })
    $utf32 = New-Object System.Text.UTF32Encoding($true, $false)
    $keys = @($a | ForEach-Object { [System.BitConverter]::ToString($utf32.GetBytes($_)) })
    [Array]::Sort($keys, $a, [System.StringComparer]::Ordinal)
    return ,$a
}
function Same-Set($a, $b) {
    $x = New-Object System.Collections.ArrayList
    foreach ($i in @($a)) { if ($null -ne $i) { [void]$x.Add([string]$i) } }
    $y = New-Object System.Collections.ArrayList
    foreach ($i in @($b)) { if ($null -ne $i) { [void]$y.Add([string]$i) } }
    if ($x.Count -ne $y.Count) { return $false }
    foreach ($i in $x) { if (-not (Str-In $y $i)) { return $false } }
    return $true
}
# A Risk justifies a control only while it is being managed: `retired` is
# terminal (C.3c) and lifecycle `withdrawn` unpublishes the object.
function Risk-Is-Live($r) { return ((-not [string]::Equals($r['state'], 'retired', $ORD)) -and (-not [string]::Equals($r['lifecycle'], 'withdrawn', $ORD))) }
# A Risk JUSTIFIES a requirement once a treatment decision rests on an
# assessed risk: live, published (not draft), state assessed or treated,
# and a treatment option chosen (ISO/IEC 27001 6.1.3 a-b). Without this a
# three-field stub would satisfy -RequireRiskBasis.
function Risk-Justifies($r) {
    if (-not (Risk-Is-Live $r)) { return $false }
    if ([string]::Equals($r['lifecycle'], 'draft', $ORD)) { return $false }
    if ((-not [string]::Equals($r['state'], 'assessed', $ORD)) -and (-not [string]::Equals($r['state'], 'treated', $ORD))) { return $false }
    return [bool]$r.Contains('treatment')
}
# tailoring-refs scope a Risk; without them it applies to every Tailoring
function Risk-Applies($r, [string]$tid) {
    $n = 0; $hit = $false
    foreach ($x in @($r['tailoring-refs'])) { if ($null -ne $x) { $n++; if (Str-Eq ([string]$x) $tid) { $hit = $true } } }
    return (($n -eq 0) -or $hit)
}
function Risk-Is-Scoped($r) {
    foreach ($x in @($r['tailoring-refs'])) { if ($null -ne $x) { return $true } }
    return $false
}
# ids -> Requirement ids, through nested Sets to any depth (D21: a DAG; the
# seen list makes a malformed cycle terminate)
function Expand-Refs($refs, $objs) {
    $out = New-Object System.Collections.ArrayList
    $seen = New-Object System.Collections.ArrayList
    $stack = New-Object System.Collections.ArrayList
    foreach ($x in @($refs)) { if ($null -ne $x) { [void]$stack.Add([string]$x) } }
    while ($stack.Count -gt 0) {
        $sid = $stack[$stack.Count - 1]
        $stack.RemoveAt($stack.Count - 1)
        if (Str-In $seen $sid) { continue }
        [void]$seen.Add($sid)
        if (-not $objs.Contains($sid)) { continue }
        $tgt = $objs[$sid]
        if ([string]::Equals($tgt.t, 'requirementSet', $ORD)) {
            foreach ($m in @($tgt.o['members'])) { if ($null -ne $m) { [void]$stack.Add([string]$m['ref']) } }
        } elseif ([string]::Equals($tgt.t, 'requirement', $ORD)) {
            if (-not (Str-In $out $sid)) { [void]$out.Add($sid) }
        }
    }
    return ,$out
}
# set-refs name Sets (typed in Closure-Errors); an exclude names a
# Requirement or a Set, and a Set excludes its members; a withdrawn
# Requirement is not in force. A predicate select is resolved by the
# tailoring engine, not here: its presence makes the selection OPEN.
function Selected-Requirements($tobj, $objs) {
    $roots = New-Object System.Collections.ArrayList
    $isOpen = $false
    foreach ($s in @($tobj['selects'])) {
        if ($null -eq $s) { continue }
        if ($s.Contains('set-ref')) {
            $sr = [string]$s['set-ref']
            if ($objs.Contains($sr) -and [string]::Equals($objs[$sr].t, 'requirementSet', $ORD)) { [void]$roots.Add($sr) }
        } else { $isOpen = $true }
    }
    $sel = Expand-Refs $roots $objs
    $exRoots = New-Object System.Collections.ArrayList
    foreach ($e in @($tobj['excludes'])) { if ($null -ne $e) { [void]$exRoots.Add([string]$e['ref']) } }
    foreach ($q in @(Expand-Refs $exRoots $objs)) { if ($null -ne $q) { $sel.Remove([string]$q) } }
    $gone = New-Object System.Collections.ArrayList
    foreach ($q in @($sel)) { if ($null -ne $q -and [string]::Equals($objs[$q].o['lifecycle'], 'withdrawn', $ORD)) { [void]$gone.Add([string]$q) } }
    foreach ($q in $gone) { $sel.Remove($q) }
    return @{sel = $sel; isOpen = $isOpen; gone = $gone}
}
function Add-To-Bucket($bucket, [string]$q, [string]$rid) {
    if (-not $bucket.ContainsKey($q)) { $bucket[$q] = New-Object System.Collections.ArrayList }
    if (-not (Str-In $bucket[$q] $rid)) { [void]$bucket[$q].Add($rid) }
}
function Risk-Coverage($objs, $envelopes, $trusted) {
    $notes = New-Object System.Collections.ArrayList
    $errs = New-Object System.Collections.ArrayList
    $riskIds = New-Object System.Collections.ArrayList
    $tailIds = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) {
        if ([string]::Equals($objs[$oid].t, 'risk', $ORD)) { [void]$riskIds.Add([string]$oid) }
        if ([string]::Equals($objs[$oid].t, 'tailoring', $ORD)) { [void]$tailIds.Add([string]$oid) }
    }
    $riskIds = Sorted-Ordinal $riskIds
    $inForce = New-Object System.Collections.ArrayList
    foreach ($tid in (Sorted-Ordinal $tailIds)) {
        if ([string]::Equals($objs[$tid].o['lifecycle'], 'withdrawn', $ORD)) {
            [void]$notes.Add("${tid}: withdrawn - selects nothing and is not reported (a withdrawn Statement of Applicability is history)")
        } else { [void]$inForce.Add($tid) }
    }
    $report = (New-OMap)
    $selections = (New-Map)
    # No Tailoring at all: nothing was scoped out, so every Requirement in
    # force is in play; the implicit selection is reported under '*'. (All
    # Tailorings WITHDRAWN is a different statement and selects nothing.)
    if ($tailIds.Count -eq 0) { [void]$inForce.Add('*') }
    foreach ($tid in $inForce) {
        if ([string]::Equals($tid, '*', $ORD)) {
            $tobj = (New-Map); $tier = 'none'
            $all = New-Object System.Collections.ArrayList
            foreach ($oid in $objs.Keys) {
                if ([string]::Equals($objs[$oid].t, 'requirement', $ORD) -and -not [string]::Equals($objs[$oid].o['lifecycle'], 'withdrawn', $ORD)) { [void]$all.Add([string]$oid) } }
            $sr = @{sel = $all; isOpen = $false; gone = (New-Object System.Collections.ArrayList)}
        } else {
            $tobj = $objs[$tid].o
            $tier = Derive-Tier $tobj $objs $envelopes $trusted
            $sr = Selected-Requirements $tobj $objs
        }
        $sel = $sr.sel
        $selections[$tid] = $sr
        if ($sr.isOpen) {
            [void]$notes.Add("${tid}: predicate select not expanded by risk-coverage (engine-resolved) - the selection is a lower bound") }
        if ($sr.gone.Count -gt 0) {
            [void]$notes.Add("${tid}: $($sr.gone.Count) selected requirement(s) are withdrawn and not counted (first: $((Sorted-Ordinal $sr.gone)[0]))") }
        $treats = (New-Map); $pending = (New-Map); $lapsed = (New-Map)
        foreach ($rid in $riskIds) {
            $r = $objs[$rid].o
            if (-not (Risk-Applies $r $tid)) { continue }
            $bucket = $lapsed
            if (Risk-Justifies $r) { $bucket = $treats } elseif (Risk-Is-Live $r) { $bucket = $pending }
            foreach ($tr in @($r['treatments'])) {
                if ($null -ne $tr) { Add-To-Bucket $bucket ([string]$tr['requirement-ref']) $rid } }
        }
        $covered = New-Object System.Collections.ArrayList
        $uncovered = New-Object System.Collections.ArrayList
        $pendingOnly = New-Object System.Collections.ArrayList
        $lapsedOnly = New-Object System.Collections.ArrayList
        $lab = $tid; if ([string]::Equals($tid, '*', $ORD)) { $lab = '(no Tailoring)' }   # as validate_core.py labels the implicit selection
        foreach ($q in (Sorted-Ordinal $sel)) {
            if ($treats.ContainsKey($q)) { [void]$covered.Add($q); continue }
            [void]$uncovered.Add($q)
            if ($pending.ContainsKey($q)) {
                [void]$pendingOnly.Add($q)
                [void]$notes.Add("${lab}: selected $q is named only by Risk(s) without an assessed treatment decision $((Sorted-Ordinal $pending[$q]) -join ', ') - counted as uncovered (a risk justifies once it is assessed and its option chosen)")
            } elseif ($lapsed.ContainsKey($q)) {
                [void]$lapsedOnly.Add($q)
                [void]$notes.Add("${lab}: selected $q is named only by retired/withdrawn Risk(s) $((Sorted-Ordinal $lapsed[$q]) -join ', ') - counted as uncovered (C.3c: a retired risk justifies nothing)")
            }
        }
        $exclNo = 0
        foreach ($e in @($tobj['excludes'])) { if ($null -ne $e -and -not $e.Contains('rationale')) { $exclNo++ } }
        if ([string]::Equals($tier, 'consumer', $ORD) -and $exclNo -gt 0) {
            [void]$notes.Add("${tid}: $exclNo exclude(s) without rationale at consumer tier (RISK-10, SHOULD: an SoA exclusion carries its justification)") }
        $report[$tid] = @{tier = $tier; selected = $sel.Count; isOpen = $sr.isOpen; covered = $covered; uncovered = $uncovered; pending = $pendingOnly; lapsed = $lapsedOnly}
    }
    # RISK-14 (SHOULD): with more than one Tailoring in force an unscoped
    # Risk counts in each
    if ($inForce.Count -gt 1) {
        foreach ($rid in $riskIds) {
            $r = $objs[$rid].o
            $hasTr = $false
            foreach ($tr in @($r['treatments'])) { if ($null -ne $tr) { $hasTr = $true } }
            if ((Risk-Is-Live $r) -and $hasTr -and -not (Risk-Is-Scoped $r)) {
                [void]$notes.Add("${rid}: no tailoring-refs in a bundle with $($inForce.Count) Tailorings - its treatment counts in each (RISK-14, SHOULD: a Risk names the Tailoring its treatment belongs to)") }
        }
    }
    # RISK-11 binds LIVE risks only and is asked of the Tailorings the risk
    # belongs to (its tailoring-refs, else all in force); an unresolved or
    # mistyped target is RISK-7/12's failure. Where one of THOSE selections
    # is open the question is undecidable here: said, not guessed.
    $outOfScope = (New-Map); $undecided = (New-Map)
    if ($true) {
        foreach ($rid in $riskIds) {
            $r = $objs[$rid].o
            if (-not (Risk-Is-Live $r)) { continue }
            $mine = New-Object System.Collections.ArrayList
            foreach ($tid in $inForce) { if (Risk-Applies $r $tid) { [void]$mine.Add($tid) } }
            foreach ($tr in @($r['treatments'])) {
                if ($null -eq $tr) { continue }
                $q = [string]$tr['requirement-ref']
                if (-not $objs.Contains($q)) { continue }
                if (-not [string]::Equals($objs[$q].t, 'requirement', $ORD)) { continue }
                $selected = $false; $anyOpen = $false
                foreach ($tid in $mine) {
                    if (Str-In $selections[$tid].sel $q) { $selected = $true }
                    if ($selections[$tid].isOpen) { $anyOpen = $true }
                }
                if ($selected) { continue }
                if ((-not [string]::Equals($objs[$q].o['lifecycle'], 'withdrawn', $ORD)) -and $anyOpen) { Add-To-Bucket $undecided $q $rid }
                else { Add-To-Bucket $outOfScope $q $rid }
            }
        }
    }
    foreach ($q in (Sorted-Ordinal @($undecided.Keys))) {
        $first = (Sorted-Ordinal $undecided[$q])[0]
        [void]$notes.Add("${first}: treatment names $q, which no set-ref select reaches - RISK-11 undecided: a predicate select of its Tailoring(s) may select it")
    }
    foreach ($q in (Sorted-Ordinal @($outOfScope.Keys))) {
        $first = (Sorted-Ordinal $outOfScope[$q])[0]
        $scoped = $false
        foreach ($rid in $outOfScope[$q]) { if (Risk-Is-Scoped $objs[$rid].o) { $scoped = $true } }
        $why = 'which no Tailoring in this bundle selects'
        if ($scoped) { $why = 'which the Tailoring(s) it belongs to do not select' }
        if ([string]::Equals($objs[$q].o['lifecycle'], 'withdrawn', $ORD)) { $why = 'which is withdrawn' }
        [void]$errs.Add("${first}: treatment names $q, $why (RISK-11: a risk cannot lean on a control the SoA dropped)")
    }
    return @{report = $report; errs = $errs; notes = $notes; risks = $riskIds.Count}
}
# RISK-9 (SHOULD): a risk-adjustment Deviation names the Risk it adjusts for
function Risk-Link-Notes($objs) {
    $notes = New-Object System.Collections.ArrayList
    $riskIds = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { if ([string]::Equals($objs[$oid].t, 'risk', $ORD)) { [void]$riskIds.Add([string]$oid) } }
    if ($riskIds.Count -eq 0) { return ,$notes }
    foreach ($oid in $objs.Keys) {
        $o = $objs[$oid].o
        $devs = New-Object System.Collections.ArrayList
        foreach ($d in @($o['deviations'])) { if ($null -ne $d) { [void]$devs.Add($d) } }
        if ([string]::Equals($objs[$oid].t, 'tailoring', $ORD)) {
            foreach ($op in @($o['operations'])) {
                if ($null -eq $op) { continue }
                if (Is-Map $op['deviation']) { [void]$devs.Add($op['deviation']) } } }
        foreach ($d in $devs) {
            if (-not [string]::Equals($d['type'], 'risk-adjustment', $ORD)) { continue }
            $hit = $false
            foreach ($ref in @($d['refs'])) { if ($null -ne $ref -and (Str-In $riskIds $ref)) { $hit = $true } }
            if (-not $hit) {
                [void]$notes.Add("${oid}: risk-adjustment Deviation references no Risk of this bundle (RISK-9, SHOULD: the adjustment names the risk it accepts)") }
        }
    }
    return ,$notes
}
# the normative B.1.9 failure, printed under the policy switch
function Risk-Basis-Fail([string]$tid, [string]$q) {
    return "FAIL [risk-coverage] $tid  selected $q`n  justified by no Risk`n  rationale: ISO/IEC 27001 6.1.3 d - inclusion in the Statement of Applicability carries its justification"
}

# ---------------- who decided, and when (CP-AUTHOR-1) ----------------
# The port of the section of the same name in validate_core.py. The schema
# leaves every one of these fields optional: a catalogue authority's
# content needs none. What is missing is REPORTED, one line per object and
# rule (Author-Report), and fails nothing unless -RequireAuthors asks for
# it. REVIEW-1 (Review-Report) reports a `review-due` that has passed, on
# an approved Deviation and on a Risk still managed, against the date of
# the run in UTC or -AsOf; nothing fails by it, with or without the switch.
# The rules in one place, as validate_core.py keeps them (AUTHOR_RULES); the
# messages below carry the rule id and do not quote this text.
$AUTHOR_RULES = Ord-Table @{
    'AUTHOR-1' = 'a consumer''s Tailoring says who decided each select, exclude and operation - on the entry, or once on the Tailoring'
    'AUTHOR-2' = 'a Risk, a Finding and an Implementation say who wrote this version and when (provenance): each records a judgement'
    'AUTHOR-3' = 'an approved or withdrawn Deviation says when it was decided (decided); `opened` is when it was asked for'
    'AUTHOR-4' = 'an authorization says on which day it was given (date); it already names the authority'
    'REVIEW-1' = 'a review-due that has passed is reported, on an approved Deviation and on a Risk still managed - the date exists to be looked at'
}
# -> @{w; d} for every Deviation an object carries: in its `deviations`
# list and, on a Tailoring, inline on an operation. `w` says where.
function Deviations-Of([string]$t, $o) {
    $out = New-Object System.Collections.ArrayList
    if (Is-List $o['deviations']) {
        $i = 0
        foreach ($d in $o['deviations']) {
            if (Is-Map $d) { [void]$out.Add(@{w = "deviations[$i]"; d = $d}) }
            $i++
        }
    }
    if ([string]::Equals($t, 'tailoring', $ORD) -and (Is-List $o['operations'])) {
        $i = 0
        foreach ($op in $o['operations']) {
            if ((Is-Map $op) -and (Is-Map $op['deviation'])) { [void]$out.Add(@{w = "operations[$i].deviation"; d = $op['deviation']}) }
            $i++
        }
    }
    return ,$out
}
# -> @{rule; id; n; msg}, one per object and rule, in the ordinal order of
# the ids and, for one object, of the rules. AUTHOR-1 asks only a Tailoring
# at consumer tier (D13: duties bind there; an authority's Tailoring is
# attributed by its origin and its Attestation). An entry without
# `provenance` has its Tailoring's.
function Author-Report($objs, $envelopes, $trusted) {
    $out = New-Object System.Collections.ArrayList
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { [void]$ids.Add([string]$oid) }
    foreach ($oid in (Sorted-Ordinal $ids)) {
        $t = $objs[$oid].t; $o = $objs[$oid].o
        if ([string]::Equals($t, 'tailoring', $ORD)) {
            $tier = Derive-Tier $o $objs $envelopes $trusted
            if ([string]::Equals($tier, 'consumer', $ORD) -and -not $o.Contains('provenance')) {
                $parts = New-Object System.Collections.ArrayList
                $n = 0
                foreach ($kw in @(@('selects', 'select'), @('excludes', 'exclude'), @('operations', 'operation'))) {
                    $entries = 0; $bare = 0
                    if (Is-List $o[$kw[0]]) {
                        foreach ($e in $o[$kw[0]]) {
                            if (-not (Is-Map $e)) { continue }
                            $entries++
                            if (-not $e.Contains('provenance')) { $bare++ }
                        }
                    }
                    if ($bare -gt 0) { $n += $bare; [void]$parts.Add("$bare of $entries $($kw[1])(s)") }
                }
                if ($n -gt 0) {
                    [void]$out.Add(@{rule = 'AUTHOR-1'; id = $oid; n = $n; msg = "${oid}: $(@($parts) -join ', ') name no author, and the Tailoring names none (AUTHOR-1)"}) }
            }
        }
        $word = $null
        if ([string]::Equals($t, 'risk', $ORD)) { $word = 'Risk' }
        elseif ([string]::Equals($t, 'finding', $ORD)) { $word = 'Finding' }
        elseif ([string]::Equals($t, 'implementation', $ORD)) { $word = 'Implementation' }
        if (($null -ne $word) -and -not $o.Contains('provenance')) {
            [void]$out.Add(@{rule = 'AUTHOR-2'; id = $oid; n = 1; msg = "${oid}: this $word does not say who wrote it and when (AUTHOR-2)"}) }
        if ($o.Contains('deviations') -or [string]::Equals($t, 'tailoring', $ORD)) {
            $undated = New-Object System.Collections.ArrayList
            foreach ($wd in (Deviations-Of $t $o)) {
                $st = $wd.d['state']
                if (([string]::Equals($st, 'approved', $ORD) -or [string]::Equals($st, 'withdrawn', $ORD)) -and -not $wd.d.Contains('decided')) {
                    [void]$undated.Add($wd.w) }
            }
            if ($undated.Count -gt 0) {
                [void]$out.Add(@{rule = 'AUTHOR-3'; id = $oid; n = $undated.Count; msg = "${oid}: $($undated.Count) Deviation(s) approved or withdrawn without ``decided``: $(@($undated) -join ', ') (AUTHOR-3)"}) }
        }
        if ([string]::Equals($t, 'component', $ORD) -and (Is-List $o['authorizations'])) {
            $bare = New-Object System.Collections.ArrayList
            foreach ($a in $o['authorizations']) {
                if ((Is-Map $a) -and -not $a.Contains('date')) { [void]$bare.Add([string]$a['id']) } }
            if ($bare.Count -gt 0) {
                [void]$out.Add(@{rule = 'AUTHOR-4'; id = $oid; n = $bare.Count; msg = "${oid}: $($bare.Count) authorization(s) without a date: $(@($bare) -join ', ') (AUTHOR-4)"}) }
        }
    }
    return ,$out
}
# REVIEW-1 reads days. A day is a [datetime] at 00:00:00 UTC; every text is
# parsed with an explicit format under the invariant culture, never the
# culture of the machine.
function Parse-Day($s) {    # 'YYYY-MM-DD' -> the day, or $null when it is not a day of the calendar
    if (-not ($s -is [string])) { return $null }
    $d = [datetime]::MinValue
    if (-not [datetime]::TryParseExact($s, 'yyyy-MM-dd', $INV, [System.Globalization.DateTimeStyles]::None, [ref]$d)) { return $null }
    return [datetime]::SpecifyKind($d, [System.DateTimeKind]::Utc)
}
# an RFC 3339 date-time: the wall clock, fractional seconds (which never
# move the day), and the offset - Z, +hh:mm or -hh:mm
$REVIEW_DT_RX = New-Object System.Text.RegularExpressions.Regex '^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})(?:\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})\z'
$ELAPSED_SECONDS = Ord-Table @{seconds = 1; minutes = 60; hours = 3600}
# -> @{day; why}: the UTC calendar day a `review-due` falls on, or $null
# and why it cannot be evaluated. $start is the date a duration counts from.
function Utc-Day($due, $start) {
    $kind = $due['type']
    $noDay = @{day = $null; why = 'not a day of the calendar'}
    if ([string]::Equals($kind, 'date', $ORD)) {
        $day = Parse-Day $due['value']
        if ($null -eq $day) { return $noDay }
        return @{day = $day; why = $null}
    }
    if ([string]::Equals($kind, 'datetime', $ORD)) {
        if (-not ($due['value'] -is [string])) { return $noDay }
        $m = $REVIEW_DT_RX.Match($due['value'])
        if (-not $m.Success) { return $noDay }
        $at = [datetime]::MinValue
        if (-not [datetime]::TryParseExact($m.Groups[1].Value, "yyyy-MM-dd'T'HH:mm:ss", $INV, [System.Globalization.DateTimeStyles]::None, [ref]$at)) { return $noDay }
        $off = $m.Groups[2].Value
        $minutes = 0
        if (-not [string]::Equals($off, 'Z', $ORD)) {
            $minutes = ([int]::Parse($off.Substring(1, 2), $INV) * 60) + [int]::Parse($off.Substring(4, 2), $INV)
            if ($minutes -ge 1440) { return $noDay }       # an offset is less than a day
            if ($off.StartsWith('-', $ORD)) { $minutes = -$minutes }
        }
        # the wall clock is $minutes ahead of UTC; a result outside the years 1..9999 throws
        try { $utc = [datetime]::SpecifyKind($at, [System.DateTimeKind]::Utc).AddMinutes(-$minutes) } catch { return $noDay }
        return @{day = $utc.Date; why = $null}
    }
    if ([string]::Equals($kind, 'elapsed-duration', $ORD)) {
        if ($null -eq $start) { return @{day = $null; why = 'a duration, and no date to count it from'} }
        $from = Parse-Day $start
        if ($null -eq $from) { return $noDay }
        $unit = [string]$due['unit']
        if (-not $ELAPSED_SECONDS.ContainsKey($unit)) { return @{day = $null; why = 'not a typed review-due'} }
        # added to 00:00:00 UTC of the start date: whole days of seconds move
        # the day. The years 1..9999 hold 3652059 days; a duration longer
        # than that, or one that ends after them, falls on no day.
        try {
            $seconds = [decimal]$due['num'] * [decimal]$ELAPSED_SECONDS[$unit]
            $days = [decimal]::Floor($seconds / 86400)
            if (($days -gt 3652058) -or ($days -lt -3652058)) { return $noDay }
            $day = $from.AddDays([double]$days)
        } catch { return $noDay }
        return @{day = $day; why = $null}
    }
    if ([string]::Equals($kind, 'calendar-period', $ORD)) {
        return @{day = $null; why = "a calendar period, and this tool has no calendar $($due['calendar-ref']) (D9: fail-closed without the named calendar)"}
    }
    return @{day = $null; why = 'not a typed review-due'}
}
# REVIEW-1 -> @{dated; overdue; blind}: how many review dates were asked,
# the overdue ones @{id; w; day} and the not evaluable ones @{id; w; why}.
# A point in time has passed when its UTC calendar day is before $asOfDay; due
# today is not overdue. A duration counts from `decided`, else `opened`, on
# a Deviation, and from `acceptance.date` on a Risk. Asked of an approved
# Deviation and of a Risk still managed, in the ordinal order of the ids,
# then of Deviations-Of, the Risk's own `review-due` last.
function Review-Report($objs, [datetime]$asOfDay) {
    $dated = 0
    $overdue = New-Object System.Collections.ArrayList
    $blind = New-Object System.Collections.ArrayList
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { [void]$ids.Add([string]$oid) }
    foreach ($oid in (Sorted-Ordinal $ids)) {
        $t = $objs[$oid].t; $o = $objs[$oid].o
        $asked = New-Object System.Collections.ArrayList
        if ($o.Contains('deviations') -or [string]::Equals($t, 'tailoring', $ORD)) {
            foreach ($wd in (Deviations-Of $t $o)) {
                $d = $wd.d
                if ((-not [string]::Equals($d['state'], 'approved', $ORD)) -or -not (Is-Map $d['review-due'])) { continue }
                $start = $d['decided']
                if (-not (Ck-Truthy $start)) { $start = $d['opened'] }
                [void]$asked.Add(@{w = $wd.w; due = $d['review-due']; start = $start})
            }
        }
        if ([string]::Equals($t, 'risk', $ORD) -and (Risk-Is-Live $o) -and (Is-Map $o['review-due'])) {
            $start = $null
            if (Is-Map $o['acceptance']) { $start = $o['acceptance']['date'] }
            [void]$asked.Add(@{w = 'review-due'; due = $o['review-due']; start = $start})
        }
        foreach ($a in $asked) {
            $dated++
            $r = Utc-Day $a.due $a.start
            if ($null -eq $r.day) { [void]$blind.Add(@{id = $oid; w = $a.w; why = $r.why}) }
            elseif ($r.day -lt $asOfDay) { [void]$overdue.Add(@{id = $oid; w = $a.w; day = $r.day.ToString('yyyy-MM-dd', $INV)}) }
        }
    }
    return @{dated = $dated; overdue = $overdue; blind = $blind}
}
# REVIEW-1 reads the date of the run, in UTC, unless -AsOf sets it. This is
# the one place where this file reads a clock.
$AS_OF = [datetime]::UtcNow.Date
if (-not (Str-Eq $AsOf '')) {
    $AS_OF = Parse-Day $AsOf
    if ($null -eq $AS_OF) { throw "-AsOf '$AsOf' is not a date, YYYY-MM-DD" }
}
# Prints the two reports for one bundle. AUTHOR lines are notes, or
# failures under -RequireAuthors; REVIEW lines are always notes.
function Report-Authors-And-Reviews([string]$section, $objs, $envelopes) {
    foreach ($a in (Author-Report $objs $envelopes $TRUSTED)) {
        if ($RequireAuthors) { FAIL $section $a.msg } else { Write-Host "    note: $($a.msg)" }
    }
    $r = Review-Report $objs $AS_OF
    if ($r.dated -gt 0) {
        Write-Host "    review: $($r.dated) review date(s) asked as of $($AS_OF.ToString('yyyy-MM-dd', $INV)): $($r.overdue.Count) overdue, $($r.blind.Count) not evaluable (REVIEW-1)" }
    foreach ($x in $r.overdue) { Write-Host "    note: $($x.id): $($x.w) was due on $($x.day) (REVIEW-1: overdue; it still holds until someone acts)" }
    foreach ($x in $r.blind) { Write-Host "    note: $($x.id): $($x.w) is not evaluated: $($x.why) (REVIEW-1)" }
}

$COUNTS = (New-Map)
$FAILURES = New-Object System.Collections.ArrayList
function OK([string]$section) { if (-not $COUNTS.ContainsKey($section)) { $COUNTS[$section] = 0 }; $COUNTS[$section]++ }
function FAIL([string]$section, [string]$msg) {
    $k = "${section}:FAIL"
    if (-not $COUNTS.ContainsKey($k)) { $COUNTS[$k] = 0 }; $COUNTS[$k]++
    [void]$FAILURES.Add("[$section] $msg")
}
function Load-Vectors([string]$name) { return Read-Json (Join-Path $CONF $name) }
function To-Objs($list) {
    $objs = (New-OMap)
    foreach ($o in $list) {
        $t = Infer-Single $o
        if ($null -ne $t) { $objs[$o['id']] = @{t = $t; o = $o} }
    }
    return $objs
}

function Run-Jcs {
    foreach ($case in (Load-Vectors 'jcs-vectors.json')['vectors']) {
        if ($case.Contains('canonical') -and $null -ne $case['canonical']) {
            $got = Canonical $case['input']
            if (Str-Eq $got $case['canonical']) { OK 'jcs' } else { FAIL 'jcs' "$($case['name']): got $got" }
        } elseif ($case.Contains('authoring-input')) {
            $viol = Optional-Empty-Violations $case['authoring-input']
            $verdict = 'valid'; if (@($viol).Count -gt 0) { $verdict = 'invalid' }
            if (Str-Eq $verdict $case['expected']) { OK 'jcs' } else { FAIL 'jcs' "$($case['name']): got $verdict" }
        } elseif ($case.Contains('number-text')) {
            # NUMBER-1 on a JSON text (a vector file cannot carry 1.0 as a
            # number: its own parser would have read it already)
            $text = [string]$case['number-text']
            $val = Parse-Json $text
            # no operator compares two strings here (D2: code point by code point, never under a culture)
            $isValid = (((Number-Spelling-Violations $text).Count -eq 0) -and ((Number-Violations $val).Count -eq 0))
            $verdict = 'invalid'; if ($isValid) { $verdict = 'valid' }
            $got = ''; if ($isValid) { $got = Canonical $val }
            $asExpected = [string]::Equals($verdict, [string]$case['expected'], [System.StringComparison]::Ordinal)
            $sameForm = (-not $isValid) -or [string]::Equals($got, [string]$case['canonical-text'], [System.StringComparison]::Ordinal)
            if ($asExpected -and $sameForm) { OK 'jcs' }
            else { FAIL 'jcs' "$($case['name']): expected $($case['expected']), got $verdict $got" }
        }
    }
}
function Run-Modality {
    foreach ($case in (Load-Vectors 'modality-vectors.json')['vectors']) {
        $got = Modality-Verdict $case['from'] $case['to']
        if (Str-Eq $got $case['verdict']) { OK 'modality' } else { FAIL 'modality' "$($case['from'])->$($case['to']): got $got" }
    }
}
function Run-Parameters {
    foreach ($case in (Load-Vectors 'parameter-vectors.json')['vectors']) {
        $got = Param-Check $case['parameter'] $case['value']
        if (Str-Eq $got $case['verdict']) { OK 'parameter' } else { FAIL 'parameter' "$($case['name']): expected $($case['verdict']), got $got" }
    }
}
function Run-Tailoring {
    foreach ($case in (Load-Vectors 'tailoring-vectors.json')['vectors']) {
        $ops = @($case['operations'])
        $verdict = 'valid'
        $seen = New-Object System.Collections.ArrayList
        foreach ($op in $ops) {
            if ($null -eq $op) { continue }
            $tkey = "$($op['requirement-ref'])|$($op['statement-id'])|$($op['parameter'])|$($op['field'])|$($op['facet'])"
            if (Str-In $seen $tkey) { $verdict = 'error' }
            [void]$seen.Add($tkey)
        }
        if (-not [string]::Equals($verdict, 'error', $ORD)) {
            foreach ($op in $ops) {
                if ($null -eq $op) { continue }
                $needsDev = $false
                if ([string]::Equals($op['op'], 'set-modality', $ORD) -and $case.Contains('base-modality')) {
                    if (-not [string]::Equals((Modality-Verdict $case['base-modality'] $op['modality']), 'monotone', $ORD)) { $needsDev = $true } }
                if ([string]::Equals($op['op'], 'replace-prose', $ORD) -and [string]::Equals($op['intent'], 'substantive', $ORD)) { $needsDev = $true }
                if ([string]::Equals($op['op'], 'set-parameter', $ORD) -and $case.Contains('parameter-decl')) {
                    $pv = Param-Check $case['parameter-decl'] $op['value']
                    if ([string]::Equals($pv, 'invalid', $ORD)) { $verdict = 'error' }
                    elseif ([string]::Equals($pv, 'deviation-required', $ORD)) { $needsDev = $true } }
                if ([string]::Equals($op['op'], 'remove-relation', $ORD) -and (Is-Map $op['relation']) -and [string]::Equals($op['relation']['type'], 'required', $ORD)) {
                    $needsDev = $true }
                if ([string]::Equals($op['op'], 'attach-facet', $ORD) -or [string]::Equals($op['op'], 'detach-facet', $ORD)) {   # P10 #29
                    $fid = ([string]$op['facet']); $fbase = $fid
                    if ($fbase.Contains('@')) { $fbase = $fbase.Substring(0, $fbase.LastIndexOf('@')) }
                    if ($fid.StartsWith('private:') -or $fbase.StartsWith('private:')) {
                        # [] by definition (D10)
                    } elseif ($case.Contains('facet-decls') -and $case['facet-decls'].Contains($fbase)) {
                        if (@($case['facet-decls'][$fbase]).Count -gt 0) { $needsDev = $true }
                    } else {
                        $verdict = 'error' } }
                if ($needsDev -and [string]::Equals($case['tier'], 'consumer', $ORD) -and -not $op.Contains('deviation') -and -not $op.Contains('deviation-ref')) {
                    $verdict = 'error' }
            }
        }
        if (Str-Eq $verdict $case['verdict']) { OK 'tailoring' } else { FAIL 'tailoring' "$($case['name']): expected $($case['verdict']), got $verdict" }
    }
}
function Run-Attestation {
    $v = Load-Vectors 'attestation-vectors.json'
    foreach ($case in $v['vectors']) {
        $sc = $case['scenario']
        $signedSem = SDig $sc['subject']
        $delivered = Copy-Deep $sc['subject']
        if ($sc.Contains('delivered-subject')) { $delivered = Copy-Deep $sc['delivered-subject'] }
        $mut = $sc['delivered-mutation']
        if ([string]::Equals($mut, 'annotation-added', $ORD)) { $delivered['annotations'] = [ordered]@{web_name = 'chrome'} }
        # package-digest differences (reindent) matter only as bytes; semantically:
        $delSem = SDig $delivered
        $got = 'semantic-match'
        if (-not (Str-Eq $delSem $signedSem)) { $got = 'tamper' }
        elseif (-not [string]::Equals($mut, 'reindent', $ORD) -and -not [string]::Equals($mut, 'annotation-added', $ORD)) { $got = 'full-match' }
        if (Str-Eq $got $case['expected']) { OK 'attestation' } else { FAIL 'attestation' "$($case['name']): expected $($case['expected']), got $got" }
    }
    # the primitive applied to a bundle (backlog #46): the verdict, which
    # manifest is bound, and what became of every subject, in their order.
    # Every object of a case must type, or the case fails.
    if (Is-List $v['binds-vectors']) {
        foreach ($case in $v['binds-vectors']) {
            $objs = To-Objs $case['objects']
            $r = Attestation-Binds $case['attestation'] $case['manifest-digest'] $objs $case['kept-packs']
            $got = New-Object System.Collections.ArrayList
            foreach ($s in $r.subjects) { [void]$got.Add($s.st) }
            $want = $case['expected-subjects']
            $same = (Str-Eq $r.verdict $case['expected']) -and (Str-Eq $r.manifest $case['expected-manifest'])
            if (-not (Is-List $want) -or (@($want).Count -ne $got.Count)) { $same = $false }
            else { for ($i = 0; $i -lt $got.Count; $i++) { if (-not (Str-Eq $got[$i] $want[$i])) { $same = $false } } }
            $wantFails = $case['expected-failure']
            if (-not ($wantFails -is [bool]) -or ([bool]$wantFails -ne [bool]$r.fails)) { $same = $false }
            if ($same -and ($objs.Count -eq @($case['objects']).Count)) { OK 'attestation' }
            else {
                FAIL 'attestation' ("binds $($case['name']): expected $($case['expected']) / $($case['expected-manifest']) / [$(@($want) -join ', ')] / fails=$wantFails, " +
                                    "got $($r.verdict) / $($r.manifest) / [$(@($got) -join ', ')] / fails=$($r.fails); $($objs.Count) of $(@($case['objects']).Count) object(s) typed")
            }
        }
    }
}
function Run-Facets {
    foreach ($case in (Load-Vectors 'facet-vectors.json')['vectors']) {
        $pinned = (New-Map)
        if ($case.Contains('pinned') -and $null -ne $case['pinned']) {
            foreach ($k in $case['pinned'].Keys) { $pinned[$k] = $case['pinned'][$k] } }
        $errs = Facet-Errors @(,@($case['name'], $case['object'])) $pinned
        $got = 'valid'; if (@($errs).Count -gt 0) { $got = 'invalid' }
        if (Str-Eq $got $case['expected']) { OK 'facet' } else { FAIL 'facet' "$($case['name']): expected $($case['expected']), got $got" }
    }
}
function Run-References {
    foreach ($case in (Load-Vectors 'reference-vectors.json')['vectors']) {
        $errs = Closure-Errors (To-Objs $case['objects'])
        if (@($errs).Count -eq $case['expected-errors']) { OK 'reference' }
        else { FAIL 'reference' "$($case['name']): expected $($case['expected-errors']), got $(@($errs).Count): $(@($errs) -join ' | ')" }
    }
}
$DEV_NEXT = Ord-Table @{investigating = @('pending', 'withdrawn'); pending = @('approved', 'withdrawn'); approved = @(); withdrawn = @()}
$FIND_NEXT = Ord-Table @{open = @('in-remediation', 'closed'); 'in-remediation' = @('closed'); closed = @()}
function Run-Lifecycle {
    $v = Load-Vectors 'lifecycle-vectors.json'
    foreach ($case in $v['deviation-transitions']) {
        $got = Str-In $DEV_NEXT[$case['from']] $case['to']
        if ([bool]$got -eq [bool]$case['valid']) { OK 'lifecycle' } else { FAIL 'lifecycle' "deviation $($case['from'])->$($case['to'])" }
    }
    foreach ($case in $v['finding-transitions']) {
        $got = Str-In $FIND_NEXT[$case['from']] $case['to']
        if ([bool]$got -eq [bool]$case['valid']) { OK 'lifecycle' } else { FAIL 'lifecycle' "finding $($case['from'])->$($case['to'])" }
    }
    foreach ($case in $v['identity-events']) {
        $allowed = [string]::Equals($case['record'], 'canonical-alias', $ORD)
        $want = [string]::Equals($case['substitution'], 'allowed', $ORD)
        if ([bool]$allowed -eq [bool]$want) { OK 'lifecycle' } else { FAIL 'lifecycle' "identity $($case['record'])" }
    }
    foreach ($case in $v['relationship-composition']) {
        $a = $case['a']; $b = $case['b']
        $got = 'supports'
        if ([string]::Equals($a, 'supplements', $ORD) -or [string]::Equals($b, 'supplements', $ORD)) { $got = $null }
        elseif ([string]::Equals($a, 'equal', $ORD) -and [string]::Equals($b, 'equal', $ORD)) { $got = 'equal' }
        elseif ([string]::Equals($a, 'equal', $ORD)) { $got = $b }
        elseif ([string]::Equals($b, 'equal', $ORD)) { if ([string]::Equals($a, 'supports', $ORD)) { $got = $a } else { $got = 'supports' } }
        $okv = (Str-Eq $got $case['composed'])
        if (-not $okv -and [string]::Equals($case['composed'], 'supports', $ORD) -and ([string]::Equals($got, 'supports', $ORD) -or [string]::Equals($got, 'intersects', $ORD))) { $okv = $true }
        if ($okv) { OK 'lifecycle' } else { FAIL 'lifecycle' "compose($a,$b): expected $($case['composed']), got $got" }
    }
    # shape disjointness over the eleven minimal objects
    $P = 'https://ex.org'
    $minimal = [ordered]@{
        requirement = [ordered]@{id = "$P/r"; version = '1'; lifecycle = 'active';
            statements = @([ordered]@{id = 's1'; modality = 'must'; 'obligated-parties' = @("$P/p"); prose = [ordered]@{en = 'X.'}})}
        requirementSet = [ordered]@{id = "$P/s"; version = '1'; lifecycle = 'active'; members = @([ordered]@{ref = "$P/r"; sequence = 10})}
        tailoring = [ordered]@{id = "$P/t"; version = '1'; lifecycle = 'active'; selects = @([ordered]@{'set-ref' = "$P/s"})}
        mapping = [ordered]@{id = "$P/m"; version = '1'; lifecycle = 'active'; 'source-ref' = "$P/r"; 'target-ref' = "$P/r2";
            relationship = 'supports'; direction = 'source-to-target'; confidence = 'draft';
            provenance = [ordered]@{'author-ref' = "$P/p"; date = '2026-07-21'}}
        component = [ordered]@{id = "$P/c"; version = '1'; lifecycle = 'active'; kind = 'service'}
        implementation = [ordered]@{id = "$P/i"; version = '1'; lifecycle = 'active'; 'component-ref' = "$P/c";
            'requirement-ref' = "$P/r"; responsibility = 'provider';
            'satisfied-by' = @([ordered]@{'capability-ref' = 'cap'}); status = 'implemented'}
        assessment = [ordered]@{id = "$P/a"; version = '1'; lifecycle = 'active'; 'subject-refs' = @("$P/r");
            method = [ordered]@{kind = 'review'}; 'performer-ref' = "$P/p"; time = '2026-07-21'; result = 'satisfied'}
        finding = [ordered]@{id = "$P/f"; version = '1'; lifecycle = 'active'; 'assessment-ref' = "$P/a";
            'requirement-ref' = "$P/r"; state = 'open'}
        attestation = [ordered]@{id = "$P/at"; version = '1'; lifecycle = 'active';
            'subject-semantic-digests' = @('sha256:' + ('0' * 64)); 'content-manifest-digest' = 'sha256:' + ('0' * 64);
            signer = "$P/p"; timestamp = '2026-07-21'}
        risk = [ordered]@{id = "$P/rk"; version = '1'; lifecycle = 'active'; scenario = [ordered]@{en = 'X.'};
            'owner-ref' = "$P/p"; state = 'identified'}
        check = [ordered]@{id = "$P/ck"; version = '1'; lifecycle = 'active'; 'requirement-ref' = "$P/r";
            platform = "$P/platform/linux"; observes = @([ordered]@{name = 'x'; type = 'integer'});
            criteria = @([ordered]@{fact = 'x'; op = 'at-most'; expected = 4}); confidence = 'draft';
            provenance = [ordered]@{'author-ref' = "$P/p"; date = '2026-11-11'}}
    }
    foreach ($want in $minimal.Keys) {
        $m = Infer-Types $minimal[$want]
        if (@($m).Count -eq 1 -and (Str-Eq $m[0] $want)) { OK 'lifecycle' }
        else { FAIL 'lifecycle' "disjointness: minimal $want matches [$(@($m) -join ',')]" }
    }
    $bare = Infer-Types ([ordered]@{id = "$P/x"; version = '1'; lifecycle = 'active'})
    if (@($bare).Count -gt 0) { FAIL 'lifecycle' 'disjointness: field-free object matches a type' }
    else { OK 'lifecycle' }
}
function Run-Tiers {
    foreach ($case in (Load-Vectors 'tier-vectors.json')['vectors']) {
        $byId = (New-Map)
        foreach ($o in $case['objects']) { $byId[$o['id']] = $o }
        foreach ($o in $case['objects']) {
            foreach ($subj in @($o['subject-semantic-digests'])) {
                if ((Is-Map $subj) -and [string]::Equals($subj['semantic-digest'], 'COMPUTE', $ORD)) {
                    if ($byId.ContainsKey($subj['id'])) { $subj['semantic-digest'] = SDig $byId[$subj['id']] } } } }
        $objs = To-Objs $case['objects']
        $tobj = $null
        foreach ($oid in $objs.Keys) { if ([string]::Equals($objs[$oid].t, 'tailoring', $ORD)) { $tobj = $objs[$oid].o } }
        $tier = Derive-Tier $tobj $objs $null $null
        $errs = Duty-Errors $objs $null $null $null
        $got = 'valid'; if (@($errs).Count -gt 0) { $got = 'invalid' }
        if ((Str-Eq $tier $case['expected-tier']) -and (Str-Eq $got $case['expected'])) { OK 'tier' }
        else { FAIL 'tier' "$($case['name']): expected $($case['expected-tier'])/$($case['expected']), got $tier/$got" }
    }
}
function Run-Dsse {
    foreach ($case in (Load-Vectors 'dsse-vectors.json')['vectors']) {
        $objs = To-Objs $case['objects']
        $att = $null; $tobj = $null
        foreach ($oid in $objs.Keys) {
            if ([string]::Equals($objs[$oid].t, 'attestation', $ORD)) { $att = $objs[$oid].o }
            if ([string]::Equals($objs[$oid].t, 'tailoring', $ORD)) { $tobj = $objs[$oid].o } }
        $envs = $case['envelopes']; $trusted = $case['trusted-keys']
        $st = 'absent'; $why = ''
        if ($att.Contains('envelope-ref') -and $null -ne $envs -and $null -ne $envs[$att['envelope-ref']]) {
            $r = Verify-Envelope $envs[$att['envelope-ref']] $att $trusted
            $st = $r[0]; $why = $r[1] }
        $tier = $null
        if ($null -ne $tobj) { $tier = Derive-Tier $tobj $objs $envs $trusted }
        $okc = $true
        if ($case.Contains('expected-envelope')) {
            $ee = $case['expected-envelope']
            if ($ee.Contains(':')) {
                $w = $ee.Split(':', 2)
                if (-not (Str-Eq $st $w[0]) -or -not $why.Contains($w[1])) { $okc = $false }
            } elseif (-not (Str-Eq $st $ee)) { $okc = $false } }
        if ($okc -and $case.Contains('expected-tier')) { if (-not (Str-Eq $tier $case['expected-tier'])) { $okc = $false } }
        if ($okc) { OK 'dsse' } else { FAIL 'dsse' "$($case['name']): got $st($why)/$tier" }
    }
}
function Run-Composition {
    foreach ($case in (Load-Vectors 'composition-vectors.json')['vectors']) {
        $aP = @(); foreach ($o in @($case['a']['objects'])) { $aP += ,@($o['id'], $o) }
        $bP = @(); foreach ($o in @($case['b']['objects'])) { $bP += ,@($o['id'], $o) }
        $aPins = $case['a']['pins']; if ($null -eq $aPins) { $aPins = (New-OMap) }
        $bPins = $case['b']['pins']; if ($null -eq $bPins) { $bPins = (New-OMap) }
        $r = Compose $aP $aPins $bP $bPins
        $res = $r[0]; $errs = $r[1]
        $exp = @($case['expected-errors'])
        $okc = (@($errs).Count -eq @($exp).Count)
        foreach ($frag in $exp) {
            $hit = $false
            foreach ($e in $errs) { if ($e.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        if ($case.Contains('expected-resolutions')) {
            foreach ($fid in $case['expected-resolutions'].Keys) {
                if (-not (Str-Eq $res[$fid] $case['expected-resolutions'][$fid])) { $okc = $false } } }
        if ($okc) { OK 'composition' } else { FAIL 'composition' "$($case['name']): got $(@($errs) -join ' | ')" }
    }
}
function Run-Conditional {
    foreach ($case in (Load-Vectors 'conditional-vectors.json')['vectors']) {
        $errs = Conditional-Apply $case['instance'] (To-Objs $case['objects'])
        $okc = (@($errs).Count -eq $case['expected-fails'])
        foreach ($frag in @($case['expected-frags'])) {
            if ($null -eq $frag) { continue }
            $hit = $false
            foreach ($e in $errs) { if ($e.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        if ($okc) { OK 'conditional' } else { FAIL 'conditional' "$($case['name']): got $(@($errs).Count): $(@($errs) -join ' ~ ')" }
    }
}
# C.3c Risk states: forward only, skipping allowed, retired terminal
$RISK_NEXT = Ord-Table @{identified = @('assessed', 'treated', 'retired'); assessed = @('treated', 'retired'); treated = @('retired'); retired = @()}
# ---------------- the kernel-version pin (backlog #44) ----------------
# A manifest MAY carry `kernel-version`; absent means 1.0.0 content.
# KERNEL-1: content beyond 1.0.0 (a Risk, Finding.risk-refs) pins the kernel
# it needs. KERNEL-2: a tool stops at a pin it does not implement and names
# both versions.
$KERNEL_VERSION = '2.0.0'
$KERNEL_SUPPORTED = @('1.0.0', '2.0.0')
function Kernel-Pin-Errors($manifest, $objs) {
    $errs = New-Object System.Collections.ArrayList
    $pin = $null
    if ((Is-Map $manifest) -and $manifest.Contains('kernel-version')) { $pin = [string]$manifest['kernel-version'] }
    if ($null -ne $pin -and (-not (Str-In $KERNEL_SUPPORTED $pin))) {
        [void]$errs.Add("manifest pins kernel-version $pin; this validator implements $KERNEL_VERSION and reads $($KERNEL_SUPPORTED -join ', ') (KERNEL-2: a tool stops at a kernel it does not implement, and says which)")
        return ,$errs
    }
    $why = $null
    $hasScales = $false
    if (Is-Map $manifest) { foreach ($x in @($manifest['scales'])) { if ($null -ne $x) { $hasScales = $true } } }
    if ($hasScales) { $why = 'the manifest pins scale definitions' }
    # CP-ADVICE-1: the pack header of a manifest, statement-ids on a capability
    if ($null -eq $why -and (Is-Map $manifest) -and (Ck-Truthy $manifest['pack'])) { $why = 'the manifest carries a pack header' }
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { [void]$ids.Add([string]$oid) }
    foreach ($oid in (Sorted-Ordinal $ids)) {
        if ($null -ne $why) { break }
        $t = $objs[$oid].t; $o = $objs[$oid].o
        if ([string]::Equals($t, 'risk', $ORD)) { $why = "$oid is a Risk"; break }
        $hasRefs = $false
        foreach ($x in @($o['risk-refs'])) { if ($null -ne $x) { $hasRefs = $true } }
        if ([string]::Equals($t, 'finding', $ORD) -and $hasRefs) { $why = "$oid carries risk-refs"; break }
        # CP-CHECK-1: the Check type, Assessment.check-results / .tailoring-ref, Finding.check-ref
        if ([string]::Equals($t, 'check', $ORD)) { $why = "$oid is a Check"; break }
        if ([string]::Equals($t, 'assessment', $ORD) -and ((Ck-Truthy $o['check-results']) -or (Ck-Truthy $o['tailoring-ref']))) {
            $why = "$oid carries check results"; break }
        if ([string]::Equals($t, 'finding', $ORD) -and (Ck-Truthy $o['check-ref'])) { $why = "$oid carries a check-ref"; break }
        if ([string]::Equals($t, 'component', $ORD)) {
            foreach ($c in @($o['capabilities'])) {
                if ($null -ne $c -and (Ck-Truthy $c['statement-ids'])) { $why = "$oid names clauses on a capability (statement-ids)" } }
            if (($null -eq $why) -and (Is-Map $o) -and $o.Contains('product-version')) {
                $why = "$oid names the product version it describes (product-version)" }
            if ($null -ne $why) { break }
        }
        # CP-AUTHOR-1: `provenance` where 1.0.0 had none, `decided` and
        # `review-due` on a Deviation, `date` on an authorization
        if (([string]::Equals($t, 'tailoring', $ORD) -or [string]::Equals($t, 'implementation', $ORD) -or [string]::Equals($t, 'finding', $ORD)) -and $o.Contains('provenance')) {
            $why = "$oid names its author (provenance)"; break }
        if ([string]::Equals($t, 'tailoring', $ORD)) {
            foreach ($k in @('selects', 'excludes', 'operations')) {
                if (-not (Is-List $o[$k])) { continue }
                foreach ($e in $o[$k]) {
                    if ((Is-Map $e) -and $e.Contains('provenance')) {
                        $why = "$oid names the author of a select, an exclude or an operation (provenance)" } }
            }
            if ($null -ne $why) { break }
        }
        if ($o.Contains('deviations') -or [string]::Equals($t, 'tailoring', $ORD)) {
            foreach ($wd in (Deviations-Of $t $o)) {
                if ($wd.d.Contains('decided') -or $wd.d.Contains('review-due')) {
                    $why = "$oid carries a Deviation with ``decided`` or ``review-due``" } }
            if ($null -ne $why) { break }
        }
        if ([string]::Equals($t, 'component', $ORD) -and (Is-List $o['authorizations'])) {
            foreach ($a in $o['authorizations']) {
                if ((Is-Map $a) -and $a.Contains('date')) { $why = "$oid dates an authorization" } }
            if ($null -ne $why) { break }
        }
    }
    if ($null -ne $why -and -not [string]::Equals($pin, '2.0.0', $ORD)) {
        $said = 'pins no kernel-version'
        if ($null -ne $pin) { $said = "pins kernel-version $pin" }
        [void]$errs.Add("$why, which needs kernel 2.0.0, but the manifest $said (KERNEL-1: content beyond 1.0.0 names its kernel, so that an older tool can say what it is missing)")
    }
    return ,$errs
}
# DATE-1..5: fields 1.0.0 left as free text and 2.0.0 types (author
# decision 2026-11-12, backlog #47a and #52): Deviation.opened is a date,
# the due of a Finding's action a typed point in time or duration. With
# CP-AUTHOR-1, the "when" of who-and-when: DATE-1 also names a Deviation's
# `decided`; DATE-3 the `date` of a Mapping's provenance (a date); DATE-4
# the `time` of an Assessment and DATE-5 the `timestamp` of an Attestation
# (a date or an RFC 3339 date-time with an offset). The schema enforces;
# this names the rule when an object matches no type, so that a 1.0.0
# bundle with a free-text date is told what to correct. It never ACCEPTS
# anything.
function Is-When($v) {      # a date, or an RFC 3339 date-time with an offset
    return ((Test-Schema $DEFS['date'] $v) -or (Test-Schema $DEFS['dateTime'] $v))
}
function Date-Walk($x, $out) {
    if (Is-Map $x) {
        if ($x.Contains('deviations') -and (Is-List $x['deviations'])) {
            foreach ($dv in $x['deviations']) {
                if (-not (Is-Map $dv)) { continue }
                foreach ($field in @('opened', 'decided')) {
                    if ($dv.Contains($field) -and -not (Test-Schema $DEFS['date'] $dv[$field])) {
                        if (-not $out.Contains('DATE-1')) { [void]$out.Add('DATE-1') } }
                }
            }
        }
        foreach ($k in @($x.Keys)) { if (-not [string]::Equals($k, 'deviations', $ORD)) { Date-Walk $x[$k] $out } }
    } elseif (Is-List $x) {
        foreach ($v in $x) { Date-Walk $v $out }
    }
}
function Date-Rule-Violations($o) {
    $out = New-Object System.Collections.ArrayList
    if (-not (Is-Map $o)) { return ,$out }
    Date-Walk $o $out
    if ($o.Contains('actions') -and (Is-List $o['actions'])) {
        foreach ($a in $o['actions']) {
            if ((Is-Map $a) -and $a.Contains('due') -and -not (Test-Schema $DEFS['due'] $a['due'])) {
                if (-not $out.Contains('DATE-2')) { [void]$out.Add('DATE-2') } }
        }
    }
    # the three fields are told apart by the signature of their type
    $prov = $o['provenance']
    if ($o.Contains('relationship') -and (Is-Map $prov) -and $prov.Contains('date') -and -not (Test-Schema $DEFS['date'] $prov['date'])) {
        [void]$out.Add('DATE-3') }
    if ($o.Contains('performer-ref') -and $o.Contains('time') -and -not (Is-When $o['time'])) { [void]$out.Add('DATE-4') }
    if ($o.Contains('signer') -and $o.Contains('timestamp') -and -not (Is-When $o['timestamp'])) { [void]$out.Add('DATE-5') }
    return ,$out
}
function Run-Kernel {
    foreach ($case in (Load-Vectors 'kernel-vectors.json')['vectors']) {
        $objs = To-Objs $case['objects']
        $errs = New-Object System.Collections.ArrayList
        if (-not (Test-Schema $DEFS['contentManifest'] $case['manifest'])) { [void]$errs.Add('manifest schema violation') }
        else { foreach ($e in (Kernel-Pin-Errors $case['manifest'] $objs)) { [void]$errs.Add($e) } }
        $exp = 0
        if ($case.Contains('expected-fails')) { $exp = $case['expected-fails'] }
        $okc = (($errs.Count -eq $exp) -and ($objs.Count -eq @($case['objects']).Count))
        foreach ($frag in @($case['expected-frags'])) {
            if ($null -eq $frag) { continue }
            $hit = $false
            foreach ($e in $errs) { if ($e.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        if ($okc) { OK 'kernel' } else { FAIL 'kernel' "$($case['name']): expected $exp, got $(@($errs) -join ' ~ ')" }
    }
    # closed shapes of fields that 2.0.0 typed or added; an invalid vector names its rule
    $all = Load-Vectors 'kernel-vectors.json'
    if ($all.Contains('shape-vectors')) {
        foreach ($case in $all['shape-vectors']) {
            $m = Infer-Types $case['document']
            $got = 'invalid'
            if ((@($m).Count -eq 1) -and (Str-Eq ([string]@($m)[0]) ([string]$case['kind']))) { $got = 'valid' }
            $named = (@(Date-Rule-Violations $case['document']) | Sort-Object) -join ','
            $want = ''
            if ($case.Contains('expected-rules')) { $want = (@($case['expected-rules']) | Sort-Object) -join ',' }
            if ((Str-Eq $got ([string]$case['expected'])) -and (Str-Eq $named $want)) { OK 'kernel' }
            else { FAIL 'kernel' "shape $($case['name']): expected $($case['expected']) [$want], got $got [$named]" }
        }
    }
}

# ---------------- pinned scale definitions (SCALE-1..3) ----------------
# A scale is the organisation's own: how many levels and what they are
# called. Its definition is a file the manifest pins by digest under
# `scales`, levels listed lowest first. A scale-ref no pin answers stays a
# landmark.
function Scale-Definition-Errors($sd, $pin) {
    $errs = New-Object System.Collections.ArrayList
    $name = '?'
    if ((Is-Map $sd) -and $sd.Contains('id')) { $name = [string]$sd['id'] }
    if ($null -ne $pin) { $name = [string]$pin['path'] }
    if (-not (Test-Schema $DEFS['scale'] $sd)) {
        [void]$errs.Add("${name}: not a scale definition (SCALE-1)")
        return ,$errs
    }
    $codes = New-Object System.Collections.ArrayList
    $dup = New-Object System.Collections.ArrayList
    foreach ($lv in @($sd['levels'])) {
        $c = [string]$lv['level']
        if (Str-In $codes $c) { if (-not (Str-In $dup $c)) { [void]$dup.Add($c) } } else { [void]$codes.Add($c) }
    }
    if ($dup.Count -gt 0) { [void]$errs.Add("${name}: level(s) $($dup -join ', ') listed twice - a level has one place in the order (SCALE-1)") }
    if ($null -ne $pin) {
        if ((-not (Str-Eq ([string]$pin['id']) ([string]$sd['id']))) -or (-not (Str-Eq ([string]$pin['exact-version']) ([string]$sd['version'])))) {
            [void]$errs.Add("${name}: pinned as $($pin['id']) $($pin['exact-version']), the file says $($sd['id']) $($sd['version']) (SCALE-1: the pin and the definition agree)") }
    }
    return ,$errs
}
function Scale-Codes($sd) {
    $codes = New-Object System.Collections.ArrayList
    foreach ($lv in @($sd['levels'])) { [void]$codes.Add([string]$lv['level']) }
    return ,$codes
}
# SCALE-1, second half: a matrix names two pinned scales, has one cell per
# pair of their levels, and every cell is a level of its own scale. A matrix
# that fails is reported and then ignored (removed from the definition).
function Matrix-Errors($scales) {
    $errs = New-Object System.Collections.ArrayList
    $sids = New-Object System.Collections.ArrayList
    foreach ($sid in $scales.Keys) { [void]$sids.Add([string]$sid) }
    foreach ($sid in (Sorted-Ordinal $sids)) {
        $sd = $scales[$sid]
        if (-not $sd.Contains('matrix')) { continue }
        $mx = $sd['matrix']
        $mine = Scale-Codes $sd
        $bad = New-Object System.Collections.ArrayList
        $lref = [string]$mx['likelihood-scale']; $iref = [string]$mx['impact-scale']
        if (-not $scales.ContainsKey($lref)) { [void]$bad.Add("its likelihood-scale $lref is not pinned in this bundle") }
        if (-not $scales.ContainsKey($iref)) { [void]$bad.Add("its impact-scale $iref is not pinned in this bundle") }
        if ($bad.Count -eq 0) {
            $lk = Scale-Codes $scales[$lref]; $ik = Scale-Codes $scales[$iref]
            $cells = $mx['cells']
            foreach ($k in @($cells.Keys)) { if (-not (Str-In $lk ([string]$k))) { [void]$bad.Add("row '$k' is no level of the likelihood scale") } }
            foreach ($l in $lk) {
                if (-not $cells.Contains($l)) { [void]$bad.Add("no row for likelihood '$l'"); continue }
                $row = $cells[$l]
                foreach ($i in $ik) { if (-not $row.Contains($i)) { [void]$bad.Add("row '$l' has no cell for impact '$i'") } }
                foreach ($k in @($row.Keys)) {
                    if (-not (Str-In $ik ([string]$k))) { [void]$bad.Add("row '$l' has a cell '$k' that is no level of the impact scale") }
                    elseif (-not (Str-In $mine ([string]$row[$k]))) { [void]$bad.Add("row '$l' yields '$($row[$k])', no level of this scale") }
                }
            }
        }
        if ($bad.Count -gt 0) {
            [void]$errs.Add("${sid}: matrix is not usable: $(@($bad | Select-Object -First 4) -join '; ') (SCALE-1: a matrix has one cell per pair of levels of its two pinned scales, each cell a level of its own scale)")
            $sd.Remove('matrix')
        }
    }
    return ,$errs
}
# every level a Risk states: @{where; level; sref}
function Risk-Levels($o) {
    $out = New-Object System.Collections.ArrayList
    foreach ($field in @('rating', 'residual-rating')) {
        $r = $o[$field]
        if (-not (Is-Map $r)) { continue }
        [void]$out.Add(@{where = $field; level = [string]$r['level']; sref = [string]$r['scale-ref']})
        foreach ($part in @('likelihood', 'impact')) {
            $p = $r[$part]
            if (Is-Map $p) { [void]$out.Add(@{where = "$field.$part"; level = [string]$p['level']; sref = [string]$p['scale-ref']}) }
        }
    }
    return ,$out
}
# $scales: scale id -> definition. Returns @{errs; notes}.
function Scale-Errors($scales, $objs) {
    $errs = New-Object System.Collections.ArrayList
    $notes = New-Object System.Collections.ArrayList
    $order = (New-Map)
    foreach ($sid in $scales.Keys) {
        $codes = New-Object System.Collections.ArrayList
        foreach ($lv in @($scales[$sid]['levels'])) { [void]$codes.Add([string]$lv['level']) }
        $order[[string]$sid] = $codes
    }
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { if ([string]::Equals($objs[$oid].t, 'risk', $ORD)) { [void]$ids.Add([string]$oid) } }
    foreach ($oid in (Sorted-Ordinal $ids)) {
        $seen = (New-Map)
        foreach ($x in (Risk-Levels $objs[$oid].o)) {
            if (-not $order.ContainsKey($x.sref)) { continue }
            $codes = $order[$x.sref]
            $pos = -1
            for ($i = 0; $i -lt $codes.Count; $i++) { if (Str-Eq $codes[$i] $x.level) { $pos = $i; break } }
            if ($pos -lt 0) {
                [void]$errs.Add("${oid}: $($x.where) level '$($x.level)' is not a level of $($x.sref) (its levels: $($codes -join ', ')) (SCALE-2: a level is one the scale defines)")
            } else { $seen[$x.where] = @{pos = $pos; sref = $x.sref; level = $x.level} }
        }
        foreach ($part in @('', '.likelihood', '.impact')) {
            $a = $seen["rating$part"]; $b = $seen["residual-rating$part"]
            if (($null -ne $a) -and ($null -ne $b) -and (Str-Eq $a.sref $b.sref) -and ($b.pos -gt $a.pos)) {
                $what = "residual$part"
                if (Str-Eq $part '') { $what = 'residual level' }
                [void]$notes.Add("${oid}: $what '$($b.level)' is above '$($a.level)' on $($a.sref) (SCALE-3, SHOULD: what remains after treatment is not more than what was there)")
            }
        }
        # SCALE-4: on a scale that carries a matrix, a rating that states both
        # inputs states the level of their cell - or says why it does not
        $o = $objs[$oid].o
        foreach ($field in @('rating', 'residual-rating')) {
            $r = $o[$field]
            if (-not (Is-Map $r)) { continue }
            $rs = [string]$r['scale-ref']
            if (-not $scales.ContainsKey($rs)) { continue }
            if (-not $scales[$rs].Contains('matrix')) { continue }
            $mx = $scales[$rs]['matrix']
            $lk = $r['likelihood']; $im = $r['impact']
            if (-not ((Is-Map $lk) -and (Is-Map $im))) { continue }
            if ((-not (Str-Eq ([string]$lk['scale-ref']) ([string]$mx['likelihood-scale']))) -or (-not (Str-Eq ([string]$im['scale-ref']) ([string]$mx['impact-scale'])))) {
                [void]$errs.Add("${oid}: $field is on $rs, whose matrix combines $($mx['likelihood-scale']) and $($mx['impact-scale']), but states its likelihood and impact on other scales (SCALE-4: a level and its inputs belong to one method)")
                continue
            }
            $ll = [string]$lk['level']; $il = [string]$im['level']
            if (-not $mx['cells'].Contains($ll)) { continue }
            if (-not $mx['cells'][$ll].Contains($il)) { continue }
            $want = [string]$mx['cells'][$ll][$il]
            if (Str-Eq ([string]$r['level']) $want) { continue }
            $said = "${oid}: $field states '$($r['level'])'; the matrix of $rs yields '$want' for likelihood '$ll' and impact '$il'"
            if ($r.Contains('override-rationale')) { [void]$notes.Add("$said - overridden with a rationale (SCALE-4)") }
            else { [void]$errs.Add("$said (SCALE-4: a level follows from its matrix, or the rating carries an override-rationale)") }
        }
    }
    return @{errs = $errs; notes = $notes}
}
function Run-Scale {
    foreach ($case in (Load-Vectors 'scale-vectors.json')['vectors']) {
        $errs = New-Object System.Collections.ArrayList
        $scales = (New-Map)
        foreach ($sd in @($case['scales'])) {
            if ($null -eq $sd) { continue }
            $e = Scale-Definition-Errors $sd $null
            foreach ($m in $e) { [void]$errs.Add($m) }
            if ($e.Count -eq 0) { $scales[[string]$sd['id']] = $sd }
        }
        foreach ($m in (Matrix-Errors $scales)) { [void]$errs.Add($m) }
        $objs = To-Objs $case['objects']
        $se = Scale-Errors $scales $objs
        foreach ($m in $se.errs) { [void]$errs.Add($m) }
        $exp = 0
        if ($case.Contains('expected-fails')) { $exp = $case['expected-fails'] }
        $okc = (($errs.Count -eq $exp) -and ($objs.Count -eq @($case['objects']).Count))
        foreach ($frag in @($case['expected-frags'])) {
            if ($null -eq $frag) { continue }
            $hit = $false
            foreach ($m in $errs) { if ($m.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        $wantNotes = 0
        foreach ($frag in @($case['expected-notes'])) {
            if ($null -eq $frag) { continue }
            $wantNotes++
            $hit = $false
            foreach ($m in $se.notes) { if ($m.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        if ($case.Contains('expected-notes') -and $wantNotes -eq 0 -and $se.notes.Count -gt 0) { $okc = $false }
        if ($okc) { OK 'scale' } else { FAIL 'scale' "$($case['name']): expected $exp, got $(@($errs) -join ' ~ ') | notes: $(@($se.notes) -join ' ~ ')" }
    }
}

# CP-AUTHOR-1: `author-vectors` hold Author-Report to [rule, object id,
# count] in order; `review-vectors` hold Review-Report, run with the
# vector's `as-of`, to [object id, where] for the overdue and for the not
# evaluable (absent = empty). A vector whose objects do not all get a type
# fails. The lists are compared in their canonical form: order, text and
# number alike.
function Run-Author {
    $v = Load-Vectors 'author-vectors.json'
    foreach ($case in $v['author-vectors']) {
        $objs = To-Objs $case['objects']
        $got = $null
        if ($objs.Count -eq @($case['objects']).Count) {
            $got = New-Object System.Collections.ArrayList
            foreach ($a in (Author-Report $objs $null $null)) { [void]$got.Add(@($a.rule, $a.id, $a.n)) }
        }
        $gotText = Format-Canonical $got
        $wantText = Format-Canonical $case['expected']
        if (Str-Eq $gotText $wantText) { OK 'author' }
        else { FAIL 'author' "$($case['name']): expected $wantText, got $gotText" }
    }
    foreach ($case in $v['review-vectors']) {
        $objs = To-Objs $case['objects']
        $asOfDay = Parse-Day $case['as-of']
        $got = $null
        if (($objs.Count -eq @($case['objects']).Count) -and ($null -ne $asOfDay)) {
            $r = Review-Report $objs $asOfDay
            $over = New-Object System.Collections.ArrayList
            foreach ($x in $r.overdue) { [void]$over.Add(@($x.id, $x.w)) }
            $blind = New-Object System.Collections.ArrayList
            foreach ($x in $r.blind) { [void]$blind.Add(@($x.id, $x.w)) }
            $got = @($over, $blind)
        }
        $wantOver = New-Object System.Collections.ArrayList
        if ($case.Contains('expected-overdue')) { $wantOver = $case['expected-overdue'] }
        $wantBlind = New-Object System.Collections.ArrayList
        if ($case.Contains('expected-not-evaluable')) { $wantBlind = $case['expected-not-evaluable'] }
        $gotText = Format-Canonical $got
        $wantText = Format-Canonical @($wantOver, $wantBlind)
        if (Str-Eq $gotText $wantText) { OK 'author' }
        else { FAIL 'author' "$($case['name']): as of $($case['as-of']) expected [overdue, not evaluable] $wantText, got $gotText" }
    }
}

function Run-Risk {
    $v = Load-Vectors 'risk-vectors.json'
    foreach ($case in $v['risk-transitions']) {
        $got = Str-In $RISK_NEXT[$case['from']] $case['to']
        if ([bool]$got -eq [bool]$case['valid']) { OK 'risk' } else { FAIL 'risk' "risk $($case['from'])->$($case['to'])" }
    }
    foreach ($case in $v['object-vectors']) {
        $o = $case['object']
        $m = Infer-Types $o
        $viol = Risk-Rule-Violations $o
        $okc = $false
        if ([string]::Equals($case['expected'], 'valid', $ORD)) {
            # the two layers agree on "valid": exactly the risk shape, no rule named
            $okc = (@($m).Count -eq 1 -and [string]::Equals($m[0], 'risk', $ORD) -and @($viol).Count -eq 0)
        } else {
            $okc = (@($m).Count -eq 0)
            # expected-rule is the portable assertion; expected-frag is advisory
            # (one schema library's message text) and is not evaluated here
            if ($okc -and $case.Contains('expected-rule')) { $okc = (Str-In $viol $case['expected-rule']) }
        }
        if ($okc) { OK 'risk' }
        else { FAIL 'risk' "$($case['name']): expected $($case['expected']) $($case['expected-rule']), matched [$(@($m) -join ',')], rules named [$(@($viol) -join ',')]" }
    }
    foreach ($case in $v['bundle-vectors']) {
        $objs = To-Objs $case['objects']
        $errs = New-Object System.Collections.ArrayList
        foreach ($e in (Closure-Errors $objs)) { [void]$errs.Add($e) }
        $rc = Risk-Coverage $objs $null $null
        foreach ($e in $rc.errs) { [void]$errs.Add($e) }
        $notes = New-Object System.Collections.ArrayList
        foreach ($n in $rc.notes) { [void]$notes.Add($n) }
        foreach ($n in (Risk-Link-Notes $objs)) { [void]$notes.Add($n) }
        $expFails = 0
        if ($case.Contains('expected-fails')) { $expFails = $case['expected-fails'] }
        $okc = ($errs.Count -eq $expFails)
        foreach ($frag in @($case['expected-frags'])) {
            if ($null -eq $frag) { continue }
            $hit = $false
            foreach ($e in $errs) { if ($e.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        foreach ($frag in @($case['expected-notes'])) {
            if ($null -eq $frag) { continue }
            $hit = $false
            foreach ($n in $notes) { if ($n.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        if ($case.Contains('expected-coverage') -and $null -ne $case['expected-coverage']) {
            foreach ($tid in $case['expected-coverage'].Keys) {
                $want = $case['expected-coverage'][$tid]
                $got = $rc.report[$tid]
                if ($null -eq $got) { $okc = $false; continue }
                if (-not (Same-Set $got.uncovered $want['uncovered'])) { $okc = $false }
                if (-not (Same-Set $got.covered $want['covered'])) { $okc = $false }
                if ($want.Contains('lapsed')) { if (-not (Same-Set $got.lapsed $want['lapsed'])) { $okc = $false } }
                if ($want.Contains('pending')) { if (-not (Same-Set $got.pending $want['pending'])) { $okc = $false } }
            }
        }
        if ($okc) { OK 'risk' }
        else { FAIL 'risk' "$($case['name']): got $($errs.Count) fails: $(@($errs) -join ' ~ ') | notes: $(@($notes) -join ' ~ ')" }
    }
}

# ---------------- CHECK (CP-CHECK-1, kernel 2.0.0; backlog #56) ----------------
# Check is the eleventh kernel type: a typed fact contract (`observes`) and
# a flat conjunction over twelve comparators (`criteria`) - primitive
# check-verdict, App. B.1.10. Every verdict an Assessment records is
# recomputed here from the observation it records. Three-valued (strong
# Kleene AND): one not-satisfied decides, else one inconclusive, else
# satisfied. An unbound parameter is inconclusive, never a default (D9).
#
# Values are compared ORDINALLY ([string]::Equals / CompareOrdinal), never
# with -ceq: PowerShell's -ceq is culture-sensitive, so "a" + U+00AD equals
# "a" there, while validate_core.py compares code points.
$CK_SAT = 'satisfied'; $CK_NOT = 'not-satisfied'; $CK_INC = 'inconclusive'; $CK_NA = 'not-applicable'
$COLLECTOR_FACET = 'https://ns.jascon.net/stdlib/facet/collector'
$DECIMAL_RX = '^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)\z'
$CHECK_RULES = @{
    'CHECK-1'  = 'a check discharges a requirement; when that requirement is in the bundle the edge is typed and the clauses it names exist'
    'CHECK-2'  = 'every assertion reads a fact the check declares, and a fact is declared once - the fact contract is all a collector promises'
    'CHECK-3'  = 'an operator compares what it can compare - ordering on numbers, patterns on text, set operators on lists - and a literal has the fact''s type'
    'CHECK-4'  = 'a bound value comes from a parameter the requirement declares exactly once on the covered clauses, with a fitting type - so tailoring the requirement retunes the check; a pattern is never a parameter'
    'CHECK-5'  = 'tightening a parameter must never loosen the check: at-most needs a parameter that tightens lower, at-least one that tightens higher'
    'CHECK-6'  = 'a pattern is an I-Regexp (RFC 9485) within the kernel''s size limits, so two conformant tools return one verdict, in bounded time'
    'CHECK-7'  = 'collectors are well-formed and each is named once, so a result row can say which code observed'
    'CHECK-8'  = 'a result names the check it ran and that check''s semantic digest - a changed check is a different check'
    'CHECK-9'  = 'a recorded outcome is the one check-verdict computes from the recorded observation - verdicts are recomputed, never taken on trust'
    'CHECK-10' = 'an assessment that carries check results has one row per check, and its result is their aggregate: any not-satisfied, else any inconclusive or none applicable, else satisfied'
    'CHECK-11' = 'no observation, no verdict: a row without one is inconclusive and says why'
    'CHECK-12' = 'a row names only parameters its check reads, and their values are the ones the Tailoring it names binds - an implementer does not set its own pass mark'
    'CHECK-13' = 'a result''s collector-id names a collector the check declares'
    'CHECK-14' = 'a Finding raised by a check is about the requirement - and the clause - that check discharges'
    'CHECK-15' = 'evidence is content-addressed and stays inside the bundle''s store, evidence/sha256/: every digest in the chain verifies against the bytes, and a record describes the run it is attached to - its check, its collector and its observation'
}

# -- I-Regexp (RFC 9485) for matches / matches-not --
# The dialect is the ABNF of RFC 9485: XSD regexps without character-class
# subtraction, without multi-character escapes (\d \w \s ...) and without
# Unicode blocks. Matching is the WHOLE value, case-sensitive, by code
# point; `^` and `$` are ordinary characters; `.` is any character but \n
# and \r. The pattern is NEVER handed to .NET Regex (CP-CHECK-1 6.3): the
# ABNF is parsed here and run as a Thompson state-set simulation - linear
# in program x input, no backtracking. A rejected pattern throws
# System.FormatException (the IRegexpError of validate_core.py).
# Ranges are flat int arrays: lo0, hi0, lo1, hi1, ... sorted and disjoint.
$IRE_MAX_PATTERN = 256      # code points
$IRE_MAX_STATES = 1000      # compiled program, after {m,n} expansion
$IRE_MAX_INPUT = 4096       # code points per matched value; longer -> inconclusive
$IRE_CATS = @('L', 'Lu', 'Ll', 'Lm', 'Lo', 'Lt', 'M', 'Mc', 'Me', 'Mn', 'N', 'Nd', 'Nl', 'No',
              'P', 'Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps', 'Z', 'Zl', 'Zp', 'Zs',
              'S', 'Sc', 'Sk', 'Sm', 'So', 'C', 'Cc', 'Cf', 'Cn', 'Co')
# System.Globalization.UnicodeCategory, by its integer value
$IRE_CAT_ABBR = @('Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Mn', 'Mc', 'Me', 'Nd', 'Nl', 'No', 'Zs', 'Zl', 'Zp',
                  'Cc', 'Cf', 'Cs', 'Co', 'Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po', 'Sm', 'Sc', 'Sk', 'So', 'Cn')
$script:IreCatRuns = $null
$script:IreCatCache = (New-Map)
$script:IreProgs = (New-Map)
$script:IreP = $null; $script:IrePos = 0; $script:IreSrc = ''
$script:IreK = $null; $script:IreR = $null; $script:IreA = $null; $script:IreB = $null

function Ire-CPs([string]$s) {
    $out = New-Object 'System.Collections.Generic.List[int]'
    $n = $s.Length; $i = 0
    while ($i -lt $n) {
        $c = [int]$s[$i]
        if ($c -ge 0xD800 -and $c -le 0xDBFF -and ($i + 1) -lt $n) {
            $d = [int]$s[$i + 1]
            if ($d -ge 0xDC00 -and $d -le 0xDFFF) {
                $out.Add(0x10000 + (($c - 0xD800) * 0x400) + ($d - 0xDC00)); $i += 2; continue }
        }
        $out.Add($c); $i++
    }
    return ,$out
}
function Ire-Norm($pairs) {
    $n = ($pairs.Count -shr 1)
    if ($n -eq 0) { return ,(New-Object int[] 0) }
    $los = New-Object int[] $n; $his = New-Object int[] $n
    for ($i = 0; $i -lt $n; $i++) { $los[$i] = $pairs[2 * $i]; $his[$i] = $pairs[2 * $i + 1] }
    [Array]::Sort($los, $his)
    $out = New-Object 'System.Collections.Generic.List[int]'
    for ($i = 0; $i -lt $n; $i++) {
        $c = $out.Count
        if ($c -gt 0 -and $los[$i] -le ($out[$c - 1] + 1)) { if ($his[$i] -gt $out[$c - 1]) { $out[$c - 1] = $his[$i] } }
        else { $out.Add($los[$i]); $out.Add($his[$i]) }
    }
    return ,($out.ToArray())
}
function Ire-Compl($pairs) {
    $rs = Ire-Norm $pairs
    $out = New-Object 'System.Collections.Generic.List[int]'
    $nxt = 0
    for ($i = 0; $i -lt $rs.Length; $i += 2) {
        if ($rs[$i] -gt $nxt) { $out.Add($nxt); $out.Add($rs[$i] - 1) }
        $nxt = $rs[$i + 1] + 1
    }
    if ($nxt -le 0x10FFFF) { $out.Add($nxt); $out.Add(0x10FFFF) }
    return ,($out.ToArray())
}
$IRE_DOT = Ire-Compl ([int[]]@(10, 10, 13, 13))

function Ire-Cat([string]$prop) {
    # code-point ranges of a Unicode general category - the HOST's Unicode
    # database (.NET here, unicodedata in validate_core.py)
    if ($script:IreCatCache.ContainsKey($prop)) { return ,($script:IreCatCache[$prop]) }
    if ($null -eq $script:IreCatRuns) {
        $runs = New-Object 'System.Collections.Generic.List[int]'
        $start = 0; $cur = -1
        for ($cp = 0; $cp -lt 0x110000; $cp++) {
            if ($cp -lt 0x10000) { $c = [int][System.Globalization.CharUnicodeInfo]::GetUnicodeCategory([char]$cp) }
            else { $c = [int][System.Globalization.CharUnicodeInfo]::GetUnicodeCategory([char]::ConvertFromUtf32($cp), 0) }
            if ([int]$c -ne $cur) {
                if ($cur -ge 0) { $runs.Add($start); $runs.Add($cp - 1); $runs.Add($cur) }
                $start = $cp; $cur = $c }
        }
        $runs.Add($start); $runs.Add(0x10FFFF); $runs.Add($cur)
        $script:IreCatRuns = $runs
    }
    $runs = $script:IreCatRuns
    $sel = New-Object 'System.Collections.Generic.List[int]'
    for ($i = 0; $i -lt $runs.Count; $i += 3) {
        if ($IRE_CAT_ABBR[$runs[$i + 2]].StartsWith($prop, [System.StringComparison]::Ordinal)) {
            $sel.Add($runs[$i]); $sel.Add($runs[$i + 1]) }
    }
    $rs = Ire-Norm $sel
    $script:IreCatCache[$prop] = $rs
    return ,$rs
}
$IRE_SURROGATE = 'a surrogate code point (U+D800 to U+DFFF) is not a character of I-Regexp (RFC 9485, NormalChar and CCchar)'
function Ire-Surrogate([int]$o) { return ($o -ge 0xD800 -and $o -le 0xDFFF) }
function Ire-Normal([int]$o) {     # NormalChar of the ABNF as PUBLISHED in RFC 9485: it skips the
                                   # surrogate code points, which the working group's file did not (#61)
    return (($o -le 0x27) -or ($o -eq 0x2C) -or ($o -eq 0x2D) -or ($o -ge 0x2F -and $o -le 0x3E) -or
            ($o -ge 0x40 -and $o -le 0x5A) -or ($o -ge 0x5E -and $o -le 0x7A) -or
            ($o -ge 0x7E -and -not ($o -ge 0xD800 -and $o -le 0xDFFF)))
}
function Ire-Peek([int]$k = 0) {
    $i = $script:IrePos + $k
    if ($i -lt $script:IreP.Count) { return $script:IreP[$i] }
    return -1
}
function Ire-Err([string]$what) {
    throw (New-Object System.FormatException ("$what at position $($script:IrePos) of '$($script:IreSrc)'"))
}
function Ire-Regexp {
    $br = New-Object System.Collections.ArrayList
    [void]$br.Add((Ire-Branch))
    while ((Ire-Peek) -eq 124) { $script:IrePos++; [void]$br.Add((Ire-Branch)) }
    return @{k = 'alt'; b = $br}
}
function Ire-Branch {
    $items = New-Object System.Collections.ArrayList
    while ($true) {
        $c = Ire-Peek
        if ($c -eq -1 -or $c -eq 124 -or $c -eq 41) { break }
        [void]$items.Add((Ire-Piece))
    }
    return @{k = 'cat'; i = $items}
}
function Ire-Piece {
    $a = Ire-Atom
    $c = Ire-Peek
    if ($c -eq 42) { $script:IrePos++; return @{k = 'rep'; a = $a; lo = 0; hi = -1} }
    if ($c -eq 43) { $script:IrePos++; return @{k = 'rep'; a = $a; lo = 1; hi = -1} }
    if ($c -eq 63) { $script:IrePos++; return @{k = 'rep'; a = $a; lo = 0; hi = 1} }
    if ($c -eq 123) {
        # \{([0-9]+)(,([0-9]*))?\}
        $P = $script:IreP; $n = $P.Count; $i = $script:IrePos + 1
        $d1 = ''; $d2 = ''; $comma = $false
        while ($i -lt $n -and $P[$i] -ge 48 -and $P[$i] -le 57) { $d1 += [char]$P[$i]; $i++ }
        if ($d1.Length -gt 0 -and $i -lt $n -and $P[$i] -eq 44) {
            $comma = $true; $i++
            while ($i -lt $n -and $P[$i] -ge 48 -and $P[$i] -le 57) { $d2 += [char]$P[$i]; $i++ }
        }
        if (-not ($d1.Length -gt 0 -and $i -lt $n -and $P[$i] -eq 125)) {
            Ire-Err 'malformed range quantifier (I-Regexp has {n}, {n,} and {n,m})' }
        $max = [System.Numerics.BigInteger]$IRE_MAX_STATES
        $lo = [System.Numerics.BigInteger]::Parse($d1, $INV)
        $hi = $null
        if (-not $comma) { $hi = $lo } elseif ($d2.Length -gt 0) { $hi = [System.Numerics.BigInteger]::Parse($d2, $INV) }
        if ($null -ne $hi -and $hi.CompareTo($lo) -lt 0) { Ire-Err 'range quantifier has its bounds reversed' }
        if ($lo.CompareTo($max) -gt 0 -or ($null -ne $hi -and $hi.CompareTo($max) -gt 0)) {
            Ire-Err 'range quantifier exceeds the size limit' }
        $script:IrePos = $i + 1
        $hiI = -1; if ($null -ne $hi) { $hiI = [int]$hi }
        return @{k = 'rep'; a = $a; lo = [int]$lo; hi = $hiI}
    }
    return $a
}
# the characters an I-Regexp escapes with a backslash: ( ) * + - . ? [ \ ] ^ { | }
$IRE_META = New-Object 'System.Collections.Generic.HashSet[int]'
foreach ($cp in @(40, 41, 42, 43, 45, 46, 63, 91, 92, 93, 94, 123, 124, 125)) { [void]$IRE_META.Add($cp) }
function Ire-Escape {
    $n = Ire-Peek 1
    if (($n -eq 112 -or $n -eq 80) -and (Ire-Peek 2) -eq 123) {
        $P = $script:IreP; $end = -1
        for ($i = $script:IrePos + 3; $i -lt $P.Count; $i++) { if ($P[$i] -eq 125) { $end = $i; break } }
        $prop = $null
        if ($end -gt 0) {
            $prop = ''
            for ($i = $script:IrePos + 3; $i -lt $end; $i++) {
                if ($P[$i] -gt 127) { $prop = $null; break }
                $prop += [char]$P[$i] }
        }
        if ($null -eq $prop -or (-not (Str-In $IRE_CATS $prop))) {
            Ire-Err "\$([char]$n){$prop} is not a Unicode general category (I-Regexp has categories, not blocks)" }
        $script:IrePos = $end + 1
        $rs = Ire-Cat $prop
        if ($n -eq 80) { $rs = Ire-Compl $rs }
        return ,$rs
    }
    if ($IRE_META.Contains([int]$n)) {
        $script:IrePos += 2; return ,([int[]]@($n, $n)) }
    if ($n -eq 110) { $script:IrePos += 2; return ,([int[]]@(10, 10)) }
    if ($n -eq 114) { $script:IrePos += 2; return ,([int[]]@(13, 13)) }
    if ($n -eq 116) { $script:IrePos += 2; return ,([int[]]@(9, 9)) }
    Ire-Err 'this escape is not I-Regexp (no \d \w \s \b, no back-references)'
}
function Ire-CcChar {
    $c = Ire-Peek
    if ($c -eq 92) {
        $n1 = Ire-Peek 1
        if ($n1 -eq 112 -or $n1 -eq 80) { Ire-Err 'a category escape cannot bound a range' }
        $r = Ire-Escape
        return $r[0]
    }
    if ($c -eq -1 -or $c -eq 45 -or $c -eq 91 -or $c -eq 93) { Ire-Err 'this character must be escaped inside a character class' }
    if (Ire-Surrogate $c) { Ire-Err $IRE_SURROGATE }
    $script:IrePos++
    return $c
}
function Ire-CharClass {
    $script:IrePos++
    $neg = ((Ire-Peek) -eq 94)
    if ($neg) { $script:IrePos++ }
    $items = New-Object 'System.Collections.Generic.List[int]'
    $first = $true
    while ($true) {
        $c = Ire-Peek
        if ($c -eq -1) { Ire-Err 'unclosed character class' }
        if ($c -eq 93) {
            if ($first) { Ire-Err 'empty character class' }
            $script:IrePos++; break
        }
        if ($c -eq 45) {
            if ($first -or (Ire-Peek 1) -eq 93) { $items.Add(45); $items.Add(45); $script:IrePos++; $first = $false; continue }
            Ire-Err "'-' inside a character class only first or last (no class subtraction)"
        }
        if ($c -eq 92) {
            $n1 = Ire-Peek 1
            if ($n1 -eq 112 -or $n1 -eq 80) {
                $r = Ire-Escape
                foreach ($x in $r) { $items.Add($x) }
                $first = $false; continue }
        }
        $lo = Ire-CcChar
        $p0 = Ire-Peek; $p1 = Ire-Peek 1
        if ($p0 -eq 45 -and $p1 -ne 93 -and $p1 -ne -1) {
            $script:IrePos++
            $hi = Ire-CcChar
            if ($hi -lt $lo) { Ire-Err 'character range out of order' }
            $items.Add($lo); $items.Add($hi)
        } else { $items.Add($lo); $items.Add($lo) }
        $first = $false
    }
    if ($neg) { $rs = Ire-Compl $items } else { $rs = Ire-Norm $items }
    return ,$rs
}
function Ire-Atom {
    $c = Ire-Peek
    if ($c -eq 40) {
        $script:IrePos++
        $r = Ire-Regexp
        if ((Ire-Peek) -ne 41) { Ire-Err 'unclosed group' }
        $script:IrePos++
        return $r
    }
    if ($c -eq 46) { $script:IrePos++; return @{k = 'set'; r = $IRE_DOT} }
    if ($c -eq 92) { $r = Ire-Escape; return @{k = 'set'; r = $r} }
    if ($c -eq 91) { $r = Ire-CharClass; return @{k = 'set'; r = $r} }
    if ($c -ne -1 -and (Ire-Normal $c)) { $script:IrePos++; return @{k = 'set'; r = ([int[]]@($c, $c))} }
    if ($c -eq -1) { Ire-Err 'the pattern ends where an atom is expected' }
    if (Ire-Surrogate $c) { Ire-Err $IRE_SURROGATE }
    Ire-Err 'this character cannot start an atom here'
}
function Ire-Parse($p) {
    if (-not ($p -is [string])) { throw (New-Object System.FormatException 'a pattern is a string') }
    $cps = Ire-CPs $p
    if ($cps.Count -gt $IRE_MAX_PATTERN) {
        throw (New-Object System.FormatException "pattern is $($cps.Count) characters long; the limit is $IRE_MAX_PATTERN") }
    $script:IreP = $cps; $script:IrePos = 0; $script:IreSrc = $p
    $ast = Ire-Regexp
    if ($script:IrePos -ne $cps.Count) { Ire-Err 'unbalanced character' }
    return $ast
}
# a state is kind 0 (code-point set R, then A) | 1 (split to A and B) | 2 (match)
function Ire-New([int]$k, $r, [int]$a, [int]$b) {
    $script:IreK.Add($k); $script:IreR.Add($r); $script:IreA.Add($a); $script:IreB.Add($b)
    if ($script:IreK.Count -gt $IRE_MAX_STATES) {
        throw (New-Object System.FormatException "pattern '$($script:IreSrc)' compiles to more than $IRE_MAX_STATES states") }
    return ($script:IreK.Count - 1)
}
function Ire-Comp($n, [int]$nxt) {
    $k = $n['k']
    if ([string]::Equals($k, 'set', $ORD)) { return (Ire-New 0 ($n['r']) $nxt 0) }
    if ([string]::Equals($k, 'cat', $ORD)) {
        $items = $n['i']
        for ($i = $items.Count - 1; $i -ge 0; $i--) { $nxt = Ire-Comp ($items[$i]) $nxt }
        return $nxt
    }
    if ([string]::Equals($k, 'alt', $ORD)) {
        $starts = New-Object 'System.Collections.Generic.List[int]'
        foreach ($b in $n['b']) { $s0 = Ire-Comp $b $nxt; $starts.Add($s0) }
        $s = $starts[$starts.Count - 1]
        for ($i = $starts.Count - 2; $i -ge 0; $i--) { $s = Ire-New 1 $null ($starts[$i]) $s }
        return $s
    }
    $a = $n['a']; $lo = $n['lo']; $hi = $n['hi']; $t = $nxt
    if ($hi -lt 0) {
        $loop = Ire-New 1 $null (-1) $nxt
        $body = Ire-Comp $a $loop
        $script:IreA[$loop] = $body
        $t = $loop
    } else {
        for ($j = 0; $j -lt ($hi - $lo); $j++) { $x = Ire-Comp $a $t; $t = Ire-New 1 $null $x $nxt }
    }
    for ($j = 0; $j -lt $lo; $j++) { $t = Ire-Comp $a $t }
    return $t
}
function Ire-Compile($p) {
    if (($p -is [string]) -and $script:IreProgs.ContainsKey($p)) { return $script:IreProgs[$p] }
    $ast = Ire-Parse $p
    $script:IreK = New-Object 'System.Collections.Generic.List[int]'
    $script:IreR = New-Object 'System.Collections.Generic.List[object]'
    $script:IreA = New-Object 'System.Collections.Generic.List[int]'
    $script:IreB = New-Object 'System.Collections.Generic.List[int]'
    $end = Ire-New 2 $null 0 0
    $start = Ire-Comp $ast $end
    $prog = @{K = $script:IreK.ToArray(); R = $script:IreR.ToArray(); A = $script:IreA.ToArray(); B = $script:IreB.ToArray(); start = $start}
    $script:IreProgs[$p] = $prog
    return $prog
}
function Ire-In($rs, [int]$o) {
    $lo = 0; $hi = ($rs.Length -shr 1) - 1
    while ($lo -le $hi) {
        $mid = ($lo + $hi) -shr 1
        if ($o -lt $rs[2 * $mid]) { $hi = $mid - 1 }
        elseif ($o -gt $rs[2 * $mid + 1]) { $lo = $mid + 1 }
        else { return $true }
    }
    return $false
}
function Ire-Closure($prog, $seeds) {
    $K = $prog.K; $A = $prog.A; $B = $prog.B
    $seen = New-Object bool[] $K.Length
    $out = New-Object 'System.Collections.Generic.List[int]'
    $stack = New-Object 'System.Collections.Generic.Stack[int]'
    foreach ($s in $seeds) { $stack.Push($s) }
    while ($stack.Count -gt 0) {
        $s = $stack.Pop()
        if ($seen[$s]) { continue }
        $seen[$s] = $true
        if ($K[$s] -eq 1) { $stack.Push($B[$s]); $stack.Push($A[$s]) } else { $out.Add($s) }
    }
    return ,$out
}
function Ire-FullMatch($p, [string]$text) {
    $prog = Ire-Compile $p
    $K = $prog.K; $R = $prog.R; $A = $prog.A
    $seed = New-Object 'System.Collections.Generic.List[int]'
    $seed.Add($prog.start)
    $cur = Ire-Closure $prog $seed
    $cps = Ire-CPs $text
    foreach ($o in $cps) {
        $nxt = New-Object 'System.Collections.Generic.List[int]'
        foreach ($s in $cur) { if ($K[$s] -eq 0 -and (Ire-In ($R[$s]) $o)) { $nxt.Add($A[$s]) } }
        if ($nxt.Count -eq 0) { return $false }
        $cur = Ire-Closure $prog $nxt
    }
    foreach ($s in $cur) { if ($K[$s] -eq 2) { return $true } }
    return $false
}

# -- check-verdict (B.1.10) --
$CHECK_OPS = @{     # which comparators fit which fact (present / absent fit every fact)
    one  = Ord-Table @{ string = @('equals', 'not-equals', 'one-of', 'matches', 'matches-not'); code = @('equals', 'not-equals', 'one-of', 'matches', 'matches-not')
              integer = @('equals', 'not-equals', 'one-of', 'at-least', 'at-most'); decimal = @('equals', 'not-equals', 'one-of', 'at-least', 'at-most')
              boolean = @('equals', 'not-equals') }
    many = Ord-Table @{ string = @('includes-all', 'excludes-all', 'subset-of', 'matches', 'matches-not')
              code = @('includes-all', 'excludes-all', 'subset-of', 'matches', 'matches-not')
              integer = @('includes-all', 'excludes-all', 'subset-of'); decimal = @('includes-all', 'excludes-all', 'subset-of')
              boolean = @() }
}
$CHECK_LIST_OPS = @('one-of', 'includes-all', 'excludes-all', 'subset-of')
$CHECK_PATTERN_OPS = @('matches', 'matches-not')

function Ck-Truthy($v) {    # Python truthiness of a JSON value
    if ($null -eq $v) { return $false }
    if ($v -is [bool]) { return $v }
    if ($v -is [string]) { return ($v.Length -gt 0) }
    if (Is-Map $v) { return ($v.Count -gt 0) }
    if (Is-List $v) { return (@($v).Count -gt 0) }
    return ($v -ne 0)
}
function Ck-SEq($a, $b) { return (($a -is [string]) -and ($b -is [string]) -and [string]::Equals([string]$a, [string]$b, [System.StringComparison]::Ordinal)) }
function Ck-Show($v) { return (Format-Canonical $v) }
function Ck-FactOk([string]$ft, $x) {
    if ([string]::Equals($ft, 'integer', $ORD)) { return (In-Number-Domain $x) }     # NUMBER-1: no verdict from a value two tools read differently
    if ([string]::Equals($ft, 'decimal', $ORD)) { return (($x -is [string]) -and [System.Text.RegularExpressions.Regex]::IsMatch($x, $DECIMAL_RX)) }
    if ([string]::Equals($ft, 'boolean', $ORD)) { return ($x -is [bool]) }
    return ($x -is [string])          # string, code
}
function Ck-FactValueOk($decl, $v) {
    $ft = [string]$decl['type']
    if (Ck-SEq $decl['cardinality'] 'many') {
        if (-not (Is-List $v)) { return $false }
        foreach ($x in $v) { if (-not (Ck-FactOk $ft $x)) { return $false } }
        return $true
    }
    return (Ck-FactOk $ft $v)
}
function Ck-ExpectedOk([string]$op, [string]$ft, $e) {
    if (Str-In $CHECK_LIST_OPS $op) {
        if (-not (Is-List $e)) { return $false }
        foreach ($x in $e) { if (-not (Ck-FactOk $ft $x)) { return $false } }
        return (([string]::Equals($op, 'subset-of', $ORD)) -or (@($e).Count -gt 0))
    }
    if (Str-In $CHECK_PATTERN_OPS $op) { return ($e -is [string]) }
    return (Ck-FactOk $ft $e)
}
# exact decimals: (unscaled BigInteger, scale) - [decimal] stops at 28 digits
function Ck-Dec([string]$s) {
    $s = $s.Trim()
    $neg = $s.StartsWith('-'); if ($neg) { $s = $s.Substring(1) }
    $dot = $s.IndexOf('.'); $frac = ''
    if ($dot -ge 0) { $frac = $s.Substring($dot + 1); $s = $s.Substring(0, $dot) }
    $u = [System.Numerics.BigInteger]::Parse($s + $frac, $INV)
    if ($neg) { $u = [System.Numerics.BigInteger]::Negate($u) }
    return @{u = $u; s = $frac.Length}
}
function Ck-Cmp([string]$ft, $a, $b) {    # -1 / 0 / 1 over two values of one fact type
    if ([string]::Equals($ft, 'decimal', $ORD)) {
        $x = Ck-Dec $a; $y = Ck-Dec $b
        $sc = [Math]::Max($x.s, $y.s)
        $xu = [System.Numerics.BigInteger]::Multiply($x.u, [System.Numerics.BigInteger]::Pow(10, $sc - $x.s))
        $yu = [System.Numerics.BigInteger]::Multiply($y.u, [System.Numerics.BigInteger]::Pow(10, $sc - $y.s))
        return $xu.CompareTo($yu)
    }
    if ([string]::Equals($ft, 'integer', $ORD)) { return ([long]$a).CompareTo([long]$b) }
    if ([string]::Equals($ft, 'boolean', $ORD)) { if ([bool]$a -eq [bool]$b) { return 0 } else { return 1 } }
    return [Math]::Sign([string]::CompareOrdinal([string]$a, [string]$b))
}
function Ck-In([string]$ft, $x, $list) {
    foreach ($y in $list) { if ((Ck-Cmp $ft $x $y) -eq 0) { return $true } }
    return $false
}
function Ck-R([string]$o, [string]$w) { return @{o = $o; w = $w} }
function Ck-Assert($a, $facts, $decls, $params) {
    # -> @{o = outcome; w = reason} of one assertion over one set of facts
    $f = [string]$a['fact']; $op = [string]$a['op']
    if (-not $decls.ContainsKey($f)) { return (Ck-R $CK_INC "fact '$f' is not declared in observes") }
    $d = $decls[$f]
    $has = ((Is-Map $facts) -and $facts.Contains($f))
    if ([string]::Equals($op, 'present', $ORD)) { if ($has) { return (Ck-R $CK_SAT "$f is present") } else { return (Ck-R $CK_NOT "$f is not present") } }
    if ([string]::Equals($op, 'absent', $ORD)) { if (-not $has) { return (Ck-R $CK_SAT "$f is absent") } else { return (Ck-R $CK_NOT "$f is present") } }
    $t = [string]$d['type']; $many = (Ck-SEq $d['cardinality'] 'many')
    $card = 'one'; $lst = ''
    if ($many) { $card = 'many'; $lst = ' list' }
    if (-not $CHECK_OPS[$card].ContainsKey($t) -or (-not (Str-In $CHECK_OPS[$card][$t] $op))) {
        return (Ck-R $CK_INC "$op does not fit a $t$lst fact") }
    if (-not $has) { return (Ck-R $CK_INC "fact '$f' was not observed") }
    $v = $facts[$f]
    if (-not (Ck-FactValueOk $d $v)) { return (Ck-R $CK_INC "fact '$f' is not a $t${lst}: $(Ck-Show $v)") }
    $e = $a['expected']; $src = 'the literal'
    if (Is-Map $e) {
        $pn = $e['param']
        if (-not ($pn -is [string]) -or -not (Is-Map $params) -or -not $params.Contains($pn)) {
            return (Ck-R $CK_INC "parameter '$pn' is unbound - a default is never substituted (D9)") }
        $e = $params[$pn]; $src = "parameter '$pn'"
    }
    if (-not (Ck-ExpectedOk $op $t $e)) { return (Ck-R $CK_INC "$src $(Ck-Show $e) does not fit $op on a $t fact") }
    $hit = $false
    if ([string]::Equals($op, 'equals', $ORD)) { $hit = ((Ck-Cmp $t $v $e) -eq 0) }
    elseif ([string]::Equals($op, 'not-equals', $ORD)) { $hit = ((Ck-Cmp $t $v $e) -ne 0) }
    elseif ([string]::Equals($op, 'one-of', $ORD)) { $hit = (Ck-In $t $v $e) }
    elseif ([string]::Equals($op, 'at-least', $ORD)) { $hit = ((Ck-Cmp $t $v $e) -ge 0) }
    elseif ([string]::Equals($op, 'at-most', $ORD)) { $hit = ((Ck-Cmp $t $v $e) -le 0) }
    elseif ([string]::Equals($op, 'includes-all', $ORD)) { $hit = $true; foreach ($x in $e) { if (-not (Ck-In $t $x $v)) { $hit = $false; break } } }
    elseif ([string]::Equals($op, 'excludes-all', $ORD)) { $hit = $true; foreach ($x in $e) { if (Ck-In $t $x $v) { $hit = $false; break } } }
    elseif ([string]::Equals($op, 'subset-of', $ORD)) { $hit = $true; foreach ($x in $v) { if (-not (Ck-In $t $x $e)) { $hit = $false; break } } }
    else {                              # matches / matches-not: whole value, every element of a list
        $vals = New-Object System.Collections.ArrayList
        if ($many) { foreach ($x in $v) { [void]$vals.Add($x) } } else { [void]$vals.Add($v) }
        foreach ($x in $vals) {
            if ((Ire-CPs $x).Count -gt $IRE_MAX_INPUT) {
                return (Ck-R $CK_INC "a value of '$f' is longer than $IRE_MAX_INPUT characters - not matched") } }
        $all = $true; $any = $false
        try {
            foreach ($x in $vals) { if (Ire-FullMatch $e $x) { $any = $true } else { $all = $false } }
        } catch [System.FormatException] {
            return (Ck-R $CK_INC "pattern rejected: $($_.Exception.Message)")
        }
        if ([string]::Equals($op, 'matches', $ORD)) { $hit = $all } else { $hit = (-not $any) }
    }
    $o = $CK_NOT; if ($hit) { $o = $CK_SAT }
    return (Ck-R $o "$f $op $(Ck-Show $e): observed $(Ck-Show $v)")
}
function Ck-Kleene($results) {
    # list of @{o; w = list of reasons} -> @{o; w}: strong Kleene AND
    foreach ($want in @($CK_NOT, $CK_INC)) {
        $hit = $false; $why = New-Object System.Collections.ArrayList
        foreach ($r in $results) {
            if (Str-Eq $r.o $want) { $hit = $true; foreach ($x in $r.w) { [void]$why.Add($x) } } }
        if ($hit) { return @{o = $want; w = $why} }
    }
    return @{o = $CK_SAT; w = (New-Object System.Collections.ArrayList)}
}
function Ck-Run($assertions, $facts, $decls, $params) {
    $res = New-Object System.Collections.ArrayList
    foreach ($a in $assertions) {
        $r = Ck-Assert $a $facts $decls $params
        $w = New-Object System.Collections.ArrayList; [void]$w.Add($r.w)
        [void]$res.Add(@{o = $r.o; w = $w})
    }
    return (Ck-Kleene $res)
}
function Ck-On($check, $facts, $decls, $params) {
    if (Ck-Truthy $check['applies-when']) {
        $aw = Ck-Run $check['applies-when'] $facts $decls $params
        $w = New-Object System.Collections.ArrayList
        if ([string]::Equals($aw.o, $CK_NOT, $ORD)) { [void]$w.Add('applies-when does not hold: ' + (@($aw.w) -join '; ')); return @{o = $CK_NA; w = $w} }
        if ([string]::Equals($aw.o, $CK_INC, $ORD)) { [void]$w.Add('applicability unknown: ' + (@($aw.w) -join '; ')); return @{o = $CK_INC; w = $w} }
    }
    return (Ck-Run $check['criteria'] $facts $decls $params)
}
function Ck-One([string]$o, [string]$w) {
    $l = New-Object System.Collections.ArrayList; [void]$l.Add($w)
    return @{o = $o; w = $l}
}
function Ck-Percent([long]$part, [long]$whole) {
    # a share as a whole percentage, in integer arithmetic so that every
    # implementation prints the same number: rounded half up, but never 0
    # while part > 0 and never 100 while part < whole
    if ($whole -le 0 -or $part -le 0) { return 0 }
    if ($part -ge $whole) { return 100 }
    $p = [long][math]::Floor([decimal](200 * $part + $whole) / [decimal](2 * $whole))
    if ($p -lt 1) { $p = 1 }
    if ($p -gt 99) { $p = 99 }
    return $p
}
function Check-Each($check, $observation, $params) {
    # B.1.10 step 5, for a per-resource Check: EVERY resource is evaluated,
    # none is skipped after the first failure. -> @{results = list of
    # @{id; o; w}; applicable; 'not-satisfied'; inconclusive;
    # 'not-applicable'; 'percent-not-satisfied'}, or $null when the Check is
    # not per-resource or the observation carries no resources. The outcome
    # stays for-all; the counts say how far from it a run is.
    if (-not (Ck-Truthy $check['each'])) { return $null }
    if (-not (Is-Map $observation)) { return $null }
    $res = $observation['resources']
    if (-not (Is-List $res)) { return $null }
    if (-not (Is-Map $params)) { $params = (New-OMap) }
    $decls = (New-Map)
    foreach ($d in @($check['observes'])) { if ($null -ne $d) { $decls[[string]$d['name']] = $d } }
    $results = New-Object System.Collections.ArrayList
    $nNot = 0; $nInc = 0; $nNa = 0
    foreach ($r in $res) {
        $rf = $null; $rid = $null
        if ((Is-Map $r) -and $r.Contains('facts') -and (Is-Map $r['facts'])) { $rf = $r['facts'] } else { $rf = (New-OMap) }
        if (Is-Map $r) { $rid = $r['id'] }
        $one = Ck-On $check $rf $decls $params
        if ([string]::Equals($one.o, $CK_NOT, $ORD)) { $nNot++ } elseif ([string]::Equals($one.o, $CK_INC, $ORD)) { $nInc++ } elseif ([string]::Equals($one.o, $CK_NA, $ORD)) { $nNa++ }
        [void]$results.Add(@{id = $rid; o = $one.o; w = $one.w})
    }
    $applicable = $results.Count - $nNa
    return @{ results = $results; applicable = $applicable; 'not-satisfied' = $nNot; inconclusive = $nInc
              'not-applicable' = $nNa; 'percent-not-satisfied' = (Ck-Percent $nNot $applicable) }
}
function Ck-EachSummary($kind, $each) {
    # one line a person reads first: how many resources, and what share, fail
    if ($each['not-satisfied'] -gt 0) {
        return "$($each['not-satisfied']) of $($each['applicable']) applicable $kind resources not satisfied ($($each['percent-not-satisfied']) %)" }
    if ($each['inconclusive'] -gt 0) { return "$($each['inconclusive']) of $($each['applicable']) applicable $kind resources inconclusive" }
    return "all $($each['applicable']) applicable $kind resources satisfied"
}
function Check-Verdict($check, $observation, $params) {
    # B.1.10 check-verdict: @{o = outcome; w = reasons} of one Check over one
    # recorded observation, with the parameter values the run was bound to
    if (-not (Is-Map $params)) { $params = (New-OMap) }
    if ($null -eq $observation) { return (Ck-One $CK_INC 'no observation: the collector did not report') }
    $decls = (New-Map)
    foreach ($d in @($check['observes'])) { if ($null -ne $d) { $decls[[string]$d['name']] = $d } }
    if (Ck-Truthy $check['each']) {
        $kind = $check['each']['resource']
        $each = Check-Each $check $observation $params
        if ($null -eq $each) { return (Ck-One $CK_INC "the check runs per $kind, but the observation carries no resources") }
        if ($each['applicable'] -eq 0) {
            if ($check['each']['allow-empty'] -eq $true) { return (Ck-One $CK_SAT "no applicable $kind observed, and allow-empty holds") }
            return (Ck-One $CK_INC "no applicable $kind observed, and allow-empty is false")
        }
        $outs = New-Object System.Collections.ArrayList
        foreach ($one in $each['results']) {
            if (-not [string]::Equals($one.o, $CK_NA, $ORD)) {
                $w = New-Object System.Collections.ArrayList
                foreach ($x in $one.w) { [void]$w.Add("$($one.id): $x") }
                [void]$outs.Add(@{o = $one.o; w = $w}) }
        }
        $got = Ck-Kleene $outs
        if (-not [string]::Equals($got.o, $CK_SAT, $ORD)) { $got.w.Insert(0, (Ck-EachSummary $kind $each)) }
        return $got
    }
    $facts = $null; if (Is-Map $observation) { $facts = $observation['facts'] }
    if (-not (Is-Map $facts)) { return (Ck-One $CK_INC 'the observation carries no facts') }
    return (Ck-On $check $facts $decls $params)
}
function Check-Aggregate($outcomes) {
    $n = 0; $hasNot = $false; $hasInc = $false
    foreach ($o in $outcomes) {
        if ([string]::Equals($o, $CK_NA, $ORD)) { continue }
        $n++
        if ([string]::Equals($o, $CK_NOT, $ORD)) { $hasNot = $true }
        if ([string]::Equals($o, $CK_INC, $ORD)) { $hasInc = $true }
    }
    if ($n -eq 0) { return $CK_INC }
    if ($hasNot) { return $CK_NOT }
    if ($hasInc) { return $CK_INC }
    return $CK_SAT
}
function Ck-Obj($objs, $ref) {      # the bundle entry a ref names, or $null
    if (($ref -is [string]) -and $objs.Contains($ref)) { return $objs[$ref] }
    return $null
}
function Ck-ParamDecls($check, $objs) {
    # -> map name -> list of @{sid; pd} over the covered clauses, or $null
    # when the requirement is not in the bundle
    $req = Ck-Obj $objs $check['requirement-ref']
    if ($null -eq $req -or -not [string]::Equals($req.t, 'requirement', $ORD)) { return $null }
    $cover = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    if (Ck-Truthy $check['statement-ids']) { foreach ($x in $check['statement-ids']) { [void]$cover.Add([string]$x) } }
    else { foreach ($s in $req.o['statements']) { [void]$cover.Add([string]$s['id']) } }
    $out = (New-Map)
    foreach ($s in $req.o['statements']) {
        if (-not $cover.Contains([string]$s['id'])) { continue }
        foreach ($pd in @($s['parameters'])) {
            if ($null -eq $pd) { continue }
            $pn = [string]$pd['name']
            if (-not $out.ContainsKey($pn)) { $out[$pn] = New-Object System.Collections.ArrayList }
            [void]$out[$pn].Add(@{sid = [string]$s['id']; pd = $pd})
        }
    }
    return $out
}
function Ck-ParamFits($pd, $fdecl, [string]$op) {
    $pt = [string]$pd['type']; $ft = [string]$fdecl['type']
    $pmany = (Ck-SEq $pd['cardinality'] 'many')
    if (Str-In $CHECK_LIST_OPS $op) { return (([string]::Equals($pt, 'list', $ORD)) -or ([string]::Equals($pt, 'choice', $ORD) -and $pmany)) }
    if ([string]::Equals($ft, 'integer', $ORD) -or [string]::Equals($ft, 'decimal', $ORD) -or [string]::Equals($ft, 'boolean', $ORD)) { return (Str-Eq $pt $ft) }
    return (([string]::Equals($pt, 'string', $ORD)) -or ([string]::Equals($pt, 'code', $ORD)) -or ([string]::Equals($pt, 'choice', $ORD) -and -not $pmany))
}
function Ck-Bad($errList, [string]$rule, [string]$oid, [string]$msg) {
    [void]$errList.Add(@{rule = $rule; msg = "${oid}: $msg (${rule}: $($CHECK_RULES[$rule]))"})
}
function Check-Object-Errors([string]$oid, $o, $objs) {
    # CHECK-1..7 over one Check -> list of @{rule; msg}
    $errList = New-Object System.Collections.ArrayList
    $rref = $o['requirement-ref']
    $req = Ck-Obj $objs $rref
    if ($null -ne $req -and -not [string]::Equals($req.t, 'requirement', $ORD)) {
        Ck-Bad $errList 'CHECK-1' $oid "requirement-ref resolves to a $($req.t), not a Requirement: $rref"
    } elseif ($null -ne $req) {
        $sids = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
        foreach ($s in $req.o['statements']) { [void]$sids.Add([string]$s['id']) }
        foreach ($sid in @($o['statement-ids'])) {
            if ($null -eq $sid) { continue }
            if (-not $sids.Contains([string]$sid)) { Ck-Bad $errList 'CHECK-1' $oid "statement-id '$sid' names no statement of $rref" } }
    }
    $count = (New-Map); $decls = (New-Map)
    foreach ($d in $o['observes']) {
        $n = [string]$d['name']
        if (-not $count.ContainsKey($n)) { $count[$n] = 0 }
        $count[$n]++; $decls[$n] = $d
    }
    $names = New-Object System.Collections.ArrayList
    foreach ($n in $count.Keys) { if ($count[$n] -gt 1) { [void]$names.Add([string]$n) } }
    foreach ($n in (Sorted-Ordinal $names)) { Ck-Bad $errList 'CHECK-2' $oid "fact '$n' is declared twice" }
    $params = Ck-ParamDecls $o $objs
    foreach ($where in @('criteria', 'applies-when')) {
        $i = -1
        foreach ($a in @($o[$where])) {
            if ($null -eq $a) { continue }
            $i++
            $at = "$where[$i]"; $op = [string]$a['op']; $fn = [string]$a['fact']
            if (-not $decls.ContainsKey($fn)) {
                Ck-Bad $errList 'CHECK-2' $oid "$at reads fact '$fn', which observes does not declare"; continue }
            $d = $decls[$fn]
            $card = 'one'; $lst = ''
            if (Ck-SEq $d['cardinality'] 'many') { $card = 'many'; $lst = ' list' }
            $t = [string]$d['type']
            if ([string]::Equals($op, 'present', $ORD) -or [string]::Equals($op, 'absent', $ORD)) { continue }
            if (-not $CHECK_OPS[$card].ContainsKey($t) -or (-not (Str-In $CHECK_OPS[$card][$t] $op))) {
                Ck-Bad $errList 'CHECK-3' $oid "${at}: $op does not fit a $t$lst fact"; continue }
            $e = $a['expected']
            if (Is-Map $e) {
                $pn = [string]$e['param']
                if (Str-In $CHECK_PATTERN_OPS $op) {
                    Ck-Bad $errList 'CHECK-4' $oid "${at}: binds parameter '$pn' as a pattern"; continue }
                if ($null -eq $params) {
                    Ck-Bad $errList 'CHECK-4' $oid "${at}: binds parameter '$pn', but requirement $rref is not in the bundle, so the binding cannot be checked"; continue }
                $found = $null; if ($params.ContainsKey($pn)) { $found = $params[$pn] }
                $nf = 0; if ($null -ne $found) { $nf = $found.Count }
                if ($nf -ne 1) {
                    Ck-Bad $errList 'CHECK-4' $oid "${at}: parameter '$pn' is declared $nf times on the covered statements"; continue }
                $pd = $found[0].pd
                if (-not (Ck-ParamFits $pd $d $op)) {
                    Ck-Bad $errList 'CHECK-4' $oid "${at}: parameter '$pn' is a $($pd['type']), which does not fit $op on a $t fact" }
                $tg = $pd['tightening']
                if (([string]::Equals($op, 'at-most', $ORD) -and (Ck-SEq $tg 'higher')) -or ([string]::Equals($op, 'at-least', $ORD) -and (Ck-SEq $tg 'lower'))) {
                    Ck-Bad $errList 'CHECK-5' $oid "${at}: $op against parameter '$pn', which tightens $tg - tightening it would loosen the check" }
            } elseif ((Str-In $CHECK_PATTERN_OPS $op) -and ($e -is [string])) {
                try { [void](Ire-Compile $e) }
                catch [System.FormatException] { Ck-Bad $errList 'CHECK-6' $oid "${at}: $($_.Exception.Message)" }
            } elseif (-not (Ck-ExpectedOk $op $t $e)) {
                Ck-Bad $errList 'CHECK-3' $oid "${at}: $(Ck-Show $e) does not fit $op on a $t$lst fact"
            }
        }
    }
    $col = $null
    if ((Is-Map $o['facets']) -and $o['facets'].Contains("$COLLECTOR_FACET@1")) { $col = $o['facets']["$COLLECTOR_FACET@1"] }
    if ($null -ne $col) {
        if ($STDLIB.ContainsKey($COLLECTOR_FACET) -and -not (Test-Schema $STDLIB[$COLLECTOR_FACET] $col)) {
            Ck-Bad $errList 'CHECK-7' $oid 'collector@1 payload violates its schema'
        } elseif (Is-Map $col) {
            $cc = (New-Map)
            foreach ($c in @($col['collectors'])) {
                if ($null -eq $c) { continue }
                $n = [string]$c['id']
                if (-not $cc.ContainsKey($n)) { $cc[$n] = 0 }
                $cc[$n]++ }
            $dups = New-Object System.Collections.ArrayList
            foreach ($n in $cc.Keys) { if ($cc[$n] -gt 1) { [void]$dups.Add([string]$n) } }
            foreach ($n in (Sorted-Ordinal $dups)) { Ck-Bad $errList 'CHECK-7' $oid "collector id '$n' is used twice" }
        }
    }
    return ,$errList
}
function Ck-Reads($check) {
    # -> the parameter names the check's assertions bind with {"param": ...}
    $out = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($key in @('criteria', 'applies-when')) {
        foreach ($a in @($check[$key])) {
            if (($null -ne $a) -and (Is-Map $a['expected'])) { [void]$out.Add([string]$a['expected']['param']) } }
    }
    return ,$out
}
$CK_MISSING = New-Object object    # "this Tailoring binds no value" - distinct from any JSON value
function Ck-TailoringBindings($check, $tail, $objs) {
    # -> ordered map parameter -> value or $CK_MISSING, for the parameters this check reads
    $out = (New-OMap)
    $decls = Ck-ParamDecls $check $objs
    if ($null -eq $decls) { return $out }
    $asserts = New-Object System.Collections.ArrayList
    foreach ($a in @($check['criteria'])) { if ($null -ne $a) { [void]$asserts.Add($a) } }
    foreach ($a in @($check['applies-when'])) { if ($null -ne $a) { [void]$asserts.Add($a) } }
    foreach ($a in $asserts) {
        $e = $a['expected']
        if (-not (Is-Map $e)) { continue }
        $pn = [string]$e['param']
        if (-not $decls.ContainsKey($pn) -or $decls[$pn].Count -ne 1) { continue }
        $sid = $decls[$pn][0].sid
        $val = $CK_MISSING
        foreach ($op in @($tail['operations'])) {
            if ($null -eq $op) { continue }
            if ((Ck-SEq $op['op'] 'set-parameter') -and (Ck-SEq $op['requirement-ref'] $check['requirement-ref']) -and
                (Ck-SEq $op['parameter'] $pn) -and (($null -eq $op['statement-id']) -or (Ck-SEq $op['statement-id'] $sid))) {
                $val = $op['value'] }
        }
        $out[$pn] = $val
    }
    return $out
}
# The evidence store: @{dir = folder beside the manifest} or @{map = ref -> text}
# (the vectors). -> the bytes, or $null when the store does not hold the ref.
function Store-Read($store, [string]$ref) {
    if ($store.ContainsKey('map')) {
        $m = $store['map']
        if ((Is-Map $m) -and $m.Contains($ref)) { return ,([System.Text.Encoding]::UTF8.GetBytes([string]$m[$ref])) }
        return $null
    }
    $fp = Join-Path $store['dir'] ($ref.Replace('/', '\'))
    if (Test-Path -LiteralPath $fp -PathType Leaf) { return ,([System.IO.File]::ReadAllBytes($fp)) }
    return $null
}
function Ck-Json-Bytes([byte[]]$raw) {     # throws when the bytes are not UTF-8 JSON
    $txt = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($raw)
    $v = Parse-Json $txt
    return ,$v
}
function Ck-Load($ctx, $dref, [string]$what) {
    # one link of the chain -> the bytes, or $null (with an error or a note recorded)
    $ref = [string]$dref['ref']; $want = [string]$dref['digest']
    $pre = "$($ctx.oid): $($ctx.at): "
    if ([System.Text.RegularExpressions.Regex]::IsMatch($ref, '^[A-Za-z][A-Za-z0-9+.-]*:')) {
        [void]$ctx.notes.Add("$pre$what $ref is a URI - not resolvable offline"); return $null }
    if ($ref.StartsWith('/') -or (Str-In ($ref.Replace('\', '/').Split('/')) '..')) {
        Ck-Bad $ctx.E 'CHECK-15' $ctx.oid "$($ctx.at): $what ref $ref leaves the bundle"; return $null }
    # the store has one layout: a file is named by the SHA-256 of its bytes. A
    # relative ref anywhere else is refused before it is read, so no tool that
    # walks the store can miss a blob another tool accepted.
    $m = [System.Text.RegularExpressions.Regex]::Match($ref, '^evidence/sha256/([0-9a-f]{64})\z')
    if (-not $m.Success) {
        Ck-Bad $ctx.E 'CHECK-15' $ctx.oid "$($ctx.at): $what ref $ref is outside the store - a ref is evidence/sha256/<the 64 hex digits of its digest>"; return $null }
    if (-not (Ck-SEq ('sha256:' + $m.Groups[1].Value) $want)) {
        Ck-Bad $ctx.E 'CHECK-15' $ctx.oid "$($ctx.at): $what $ref is stored under another digest than the recorded $want"; return $null }
    $raw = Store-Read $ctx.store $ref
    if ($null -eq $raw) {
        [void]$ctx.notes.Add("$pre$what $ref withheld - not in the bundle's store"); return $null }
    if (-not (Ck-SEq (Sha256-Hex $raw) $want)) {
        Ck-Bad $ctx.E 'CHECK-15' $ctx.oid "$($ctx.at): $what $ref does not match its digest"; return $null }
    return ,$raw
}
function Ck-Numbers($ctx, $raw, $value, [string]$what) {
    # NUMBER-1 on an evidence file -> $true when it holds; a file that breaks it is not used
    $bad = Number-Problems $raw $value
    if ($bad.Count -eq 0) { return $true }
    [void]$ctx.E.Add(@{rule = 'NUMBER-1'; msg = "$($ctx.oid): $($ctx.at): ${what}: $($bad[0]) (NUMBER-1: $NUMBER_RULE)"})
    return $false
}
function Ck-Named($v, [string]$what) { if (Ck-Truthy $v) { return "$what '$v'" }; return "no $what" }
function Evidence-Chain([string]$oid, [string]$at, $a, $row, $store, $errList, $notes) {
    # CHECK-15: row -> evidence record -> raw outputs, and observation-ref.
    # -> the observation loaded from observation-ref, or $null
    $ctx = @{oid = $oid; at = $at; store = $store; E = $errList; notes = $notes}
    $obs = $null
    if (Ck-Truthy $row['observation-ref']) {
        $raw = Ck-Load $ctx $row['observation-ref'] 'observation'
        if ($null -ne $raw) {
            try { $obs = Ck-Json-Bytes $raw }
            catch { Ck-Bad $errList 'CHECK-15' $oid "${at}: observation file unreadable: $($_.Exception.Message)"; $obs = $null }
            if ($null -ne $obs -and -not (Ck-Numbers $ctx $raw $obs 'observation file')) { $obs = $null }
            if ($null -ne $obs -and -not (Test-Schema $DEFS['checkObservation'] $obs)) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the observation file is not an observation"; $obs = $null }
        }
    }
    if (Ck-Truthy $row['evidence-record']) {
        $raw = Ck-Load $ctx $row['evidence-record'] 'evidence record'
        $rec = $null
        if ($null -ne $raw) {
            try { $rec = Ck-Json-Bytes $raw }
            catch { Ck-Bad $errList 'CHECK-15' $oid "${at}: evidence record unreadable: $($_.Exception.Message)"; $rec = $null }
        }
        if ($null -ne $rec -and -not (Ck-Numbers $ctx $raw $rec 'evidence record')) { $rec = $null }
        if ($null -ne $rec -and -not (Test-Schema $DEFS['evidenceRecord'] $rec)) {
            Ck-Bad $errList 'CHECK-15' $oid "${at}: evidence record violates its schema"; $rec = $null }
        if ($null -ne $rec) {
            if (-not (Ck-SEq $rec['check-ref'] $row['check-ref']) -or -not (Ck-SEq $rec['check-digest'] $row['check-digest'])) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the evidence record is about another check, or another version of it" }
            # row and record are two statements about one run: what one says of
            # the collector and of the observation, the other says too. A field
            # left out on one side is a difference, never a reason to skip.
            $rc = $rec['collector-id']; $wc = $row['collector-id']
            if (((Ck-Truthy $rc) -or (Ck-Truthy $wc)) -and -not (Ck-SEq $rc $wc)) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the evidence record names $(Ck-Named $rc 'collector'), the row $(Ck-Named $wc 'collector')" }
            $isSubject = $false
            foreach ($s in @($a['subject-refs'])) { if (Ck-SEq $s $rec['subject-ref']) { $isSubject = $true } }
            if (-not $isSubject) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the evidence record's subject $($rec['subject-ref']) is not a subject of the assessment" }
            $seen = $obs; if ($null -ne $row['observation']) { $seen = $row['observation'] }
            $rowHas = ($null -ne $row['observation']) -or ($null -ne $row['observation-ref'])
            $bound = Ck-Truthy $rec['observation-digest']
            if ($rowHas -and -not $bound) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the row records an observation, the evidence record binds none (no observation-digest)"
            } elseif ($bound -and -not $rowHas) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the evidence record binds an observation, the row records none"
            } elseif ($bound -and $null -eq $seen) {
                [void]$notes.Add("${oid}: ${at}: the observation is not available here - the evidence record's binding to it is not verified")
            } elseif ($bound -and -not (Ck-SEq (SDig $seen) $rec['observation-digest'])) {
                Ck-Bad $errList 'CHECK-15' $oid "${at}: the evidence record binds another observation than the row records" }
            foreach ($out in $rec['outputs']) {
                $dg = [string]$out['digest']
                $dref = @{ref = ('evidence/sha256/' + $dg.Substring($dg.IndexOf(':') + 1)); digest = $dg}
                [void](Ck-Load $ctx $dref "output '$($out['name'])'")
            }
        }
    }
    return ,$obs
}
function Check-Errors($objs, $store) {
    # CHECK-1..15 over a bundle -> @{errs = list of @{rule; msg}; notes = list}.
    # $store: the evidence store (CHECK-15); $null skips the chain.
    $errList = New-Object System.Collections.ArrayList
    $notes = New-Object System.Collections.ArrayList
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { [void]$ids.Add([string]$oid) }
    foreach ($oid in (Sorted-Ordinal $ids)) {
        $t = $objs[$oid].t; $o = $objs[$oid].o
        if ([string]::Equals($t, 'check', $ORD)) {
            foreach ($x in (Check-Object-Errors $oid $o $objs)) { [void]$errList.Add($x) }
        } elseif ([string]::Equals($t, 'finding', $ORD) -and (Ck-Truthy $o['check-ref'])) {
            $c = Ck-Obj $objs $o['check-ref']
            if ($null -ne $c -and -not [string]::Equals($c.t, 'check', $ORD)) {
                Ck-Bad $errList 'CHECK-14' $oid "check-ref resolves to a $($c.t), not a Check: $($o['check-ref'])"
            } elseif ($null -ne $c) {
                if (-not (Ck-SEq $c.o['requirement-ref'] $o['requirement-ref'])) {
                    Ck-Bad $errList 'CHECK-14' $oid "check $($o['check-ref']) discharges $($c.o['requirement-ref']), the Finding is against $($o['requirement-ref'])" }
                $sids = $c.o['statement-ids']
                if ((Ck-Truthy $sids) -and (Ck-Truthy $o['statement-ref'])) {
                    $in = $false
                    foreach ($s in $sids) { if (Ck-SEq $s $o['statement-ref']) { $in = $true } }
                    if (-not $in) { Ck-Bad $errList 'CHECK-14' $oid "statement-ref '$($o['statement-ref'])' is not a clause check $($o['check-ref']) covers" }
                }
            }
        } elseif ([string]::Equals($t, 'assessment', $ORD) -and ((Ck-Truthy $o['check-results']) -or (Ck-Truthy $o['tailoring-ref']))) {
            $tail = $null
            if (Ck-Truthy $o['tailoring-ref']) {
                $tg = Ck-Obj $objs $o['tailoring-ref']
                if ($null -eq $tg) { Ck-Bad $errList 'CHECK-12' $oid "tailoring-ref does not resolve in-bundle: $($o['tailoring-ref'])" }
                elseif (-not [string]::Equals($tg.t, 'tailoring', $ORD)) { Ck-Bad $errList 'CHECK-12' $oid "tailoring-ref resolves to a $($tg.t), not a Tailoring" }
                else { $tail = $tg.o }
            }
            $outcomes = New-Object System.Collections.ArrayList
            $seenRefs = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
            $i = -1
            foreach ($row in @($o['check-results'])) {
                if ($null -eq $row) { continue }
                $i++
                $at = "check-results[$i]"; $cref = [string]$row['check-ref']
                if (-not $seenRefs.Add($cref)) { Ck-Bad $errList 'CHECK-10' $oid "${at}: check $cref has a second row" }
                [void]$outcomes.Add([string]$row['outcome'])
                $obs = $row['observation']
                if ($null -eq $obs -and $null -eq $row['observation-ref'] -and
                    (-not (Ck-SEq $row['outcome'] $CK_INC) -or -not (Ck-Truthy $row['reason']))) {
                    $nr = ''; if (-not (Ck-Truthy $row['reason'])) { $nr = ' and no reason is given' }
                    Ck-Bad $errList 'CHECK-11' $oid "${at}: no observation, yet the outcome is $($row['outcome'])$nr" }
                if ($null -ne $store) {
                    $o2 = Evidence-Chain $oid $at $o $row $store $errList $notes
                    if ($null -eq $obs) { $obs = $o2 }
                }
                $c = Ck-Obj $objs $cref
                if ($null -eq $c) {
                    [void]$notes.Add("${oid}: ${at}: check $cref is not in this bundle - verdict not recomputed"); continue }
                if (-not [string]::Equals($c.t, 'check', $ORD)) {
                    Ck-Bad $errList 'CHECK-8' $oid "${at}: check-ref resolves to a $($c.t), not a Check"; continue }
                if (-not (Ck-SEq $row['check-digest'] (SDig $c.o))) {
                    Ck-Bad $errList 'CHECK-8' $oid "${at}: check-digest does not match $cref - the check changed after the run" }
                $cols = $null
                if ((Is-Map $c.o['facets']) -and (Is-Map $c.o['facets']["$COLLECTOR_FACET@1"])) { $cols = $c.o['facets']["$COLLECTOR_FACET@1"]['collectors'] }
                # a check without the collector facet declares no collector, so any
                # collector-id on its rows names code the check's digest does not cover
                $declared = New-Object System.Collections.ArrayList
                if (Is-List $cols) { foreach ($x in $cols) { if (Is-Map $x) { [void]$declared.Add($x['id']) } } }
                if (Ck-Truthy $row['collector-id']) {
                    $known = $false
                    foreach ($x in $declared) { if (Ck-SEq $x $row['collector-id']) { $known = $true } }
                    if (-not $known) {
                        $none = ''; if ($declared.Count -eq 0) { $none = ' - the check declares none' }
                        Ck-Bad $errList 'CHECK-13' $oid "${at}: collector-id '$($row['collector-id'])' names no collector of $cref$none" }
                }
                # a name no assertion reads cannot be verified, with or without a
                # Tailoring - and the row is inside the digest an Attestation signs
                $have = $row['parameters']; if (-not (Is-Map $have)) { $have = (New-OMap) }
                $reads = Ck-Reads $c.o
                $extra = New-Object 'System.Collections.Generic.List[string]'
                foreach ($k in @($have.Keys)) { if (-not $reads.Contains([string]$k)) { $extra.Add([string]$k) } }
                $extra.Sort([System.StringComparer]::Ordinal)
                foreach ($pn in $extra) { Ck-Bad $errList 'CHECK-12' $oid "${at}: the row records parameter '$pn', which $cref does not read" }
                if ($null -ne $tail) {
                    $bind = Ck-TailoringBindings $c.o $tail $objs
                    foreach ($pn in @($bind.Keys)) {
                        $want = $bind[[string]$pn]
                        $isMissing = [object]::ReferenceEquals($want, $CK_MISSING)
                        if ($isMissing -and $have.Contains($pn)) {
                            Ck-Bad $errList 'CHECK-12' $oid "${at}: the run used $pn=$(Ck-Show ($have[$pn])), but $($o['tailoring-ref']) binds no value for it"
                        } elseif (-not $isMissing -and (-not $have.Contains($pn) -or -not (Ck-SEq (Canonical ($have[$pn])) (Canonical $want)))) {
                            $used = '(unbound)'; if ($have.Contains($pn)) { $used = Ck-Show ($have[$pn]) }
                            Ck-Bad $errList 'CHECK-12' $oid "${at}: the run used $pn=$used, $($o['tailoring-ref']) binds $(Ck-Show $want)" }
                    }
                } elseif (Ck-Truthy $row['parameters']) {
                    [void]$notes.Add("${oid}: ${at}: parameter values are the performer's statement - no tailoring-ref to hold them to")
                }
                if ($null -eq $obs -and (Ck-Truthy $row['observation-ref'])) {
                    [void]$notes.Add("${oid}: ${at}: observation not available here - verdict not recomputed"); continue }
                $got = Check-Verdict $c.o $obs $row['parameters']
                $each = Check-Each $c.o $obs $row['parameters']
                if (($null -ne $each) -and ($each['applicable'] -gt 0)) {
                    $eachKind = $c.o['each']['resource']
                    [void]$notes.Add("${oid}: ${at}: $(Ck-EachSummary $eachKind $each)") }
                if (-not (Ck-SEq $got.o $row['outcome'])) {
                    $why = (@($got.w) -join '; ')
                    if ($why.Length -gt 200) { $why = $why.Substring(0, 200) }
                    if ($why.Length -gt 0) { $why = " ($why)" }
                    Ck-Bad $errList 'CHECK-9' $oid "${at}: recorded $($row['outcome']), check-verdict computes $($got.o)$why" }
            }
            if (Ck-Truthy $o['check-results']) {
                $agg = Check-Aggregate $outcomes
                if (-not (Ck-SEq $o['result'] $agg)) {
                    Ck-Bad $errList 'CHECK-10' $oid "result is $($o['result']), the aggregate of its check results is $agg" }
            }
        }
    }
    return @{errs = $errList; notes = $notes}
}
function Run-Check {
    $v = Load-Vectors 'check-vectors.json'
    foreach ($case in $v['regex-vectors']) {
        $valid = $true; $why = ''
        # a pattern that no JSON text may carry (a lone surrogate) is given as code points
        $pat = $case['pattern']
        if ($case.Contains('pattern-codepoints')) {
            $sb = New-Object System.Text.StringBuilder
            foreach ($cp in $case['pattern-codepoints']) {
                $n = [int]$cp
                if ($n -lt 0x10000) { [void]$sb.Append([char]$n) } else { [void]$sb.Append([char]::ConvertFromUtf32($n)) }
            }
            $pat = $sb.ToString()
        }
        try { [void](Ire-Compile $pat) }
        catch [System.FormatException] { $valid = $false; $why = $_.Exception.Message }
        $badM = New-Object System.Collections.ArrayList; $badN = New-Object System.Collections.ArrayList
        if ($case.Contains('match')) {
            foreach ($s in $case['match']) { if (-not ($valid -and (Ire-FullMatch $pat $s))) { [void]$badM.Add($s) } } }
        if ($case.Contains('no-match')) {
            foreach ($s in $case['no-match']) { if ($valid -and (Ire-FullMatch $pat $s)) { [void]$badN.Add($s) } } }
        if ([bool]$valid -eq [bool]$case['valid'] -and $badM.Count -eq 0 -and $badN.Count -eq 0) { OK 'check' }
        else { FAIL 'check' "regex '$($case['pattern'])': expected valid=$($case['valid']), got $valid $why; should match but did not [$(@($badM) -join ' | ')]; should not match but did [$(@($badN) -join ' | ')]" }
    }
    foreach ($case in $v['verdict-vectors']) {
        $got = Check-Verdict $case['check'] $case['observation'] $case['parameters']
        $okc = (Ck-SEq $got.o $case['expected'])
        $want = $case['expected-resources']     # a per-resource check: every resource is evaluated and counted
        if ($okc -and (Is-Map $want)) {
            $each = Check-Each $case['check'] $case['observation'] $case['parameters']
            if ($null -eq $each) { $okc = $false }
            else {
                foreach ($k in @('applicable', 'not-satisfied', 'inconclusive', 'not-applicable', 'percent-not-satisfied')) {
                    if (-not $want.Contains($k) -or ([long]$want[$k] -ne [long]$each[$k])) { $okc = $false } }
            }
        }
        if ($okc) { OK 'check' }
        else { FAIL 'check' "verdict $($case['name']): expected $($case['expected']), got $($got.o) $(@($got.w) -join '; ')" }
    }
    foreach ($case in $v['share-vectors']) {
        $got = Ck-Percent ([long]$case['part']) ([long]$case['whole'])
        if ([long]$got -eq [long]$case['expected']) { OK 'check' }
        else { FAIL 'check' "share $($case['part']) of $($case['whole']): expected $($case['expected']) %, got $got %" }
    }
    foreach ($case in $v['aggregate-vectors']) {
        $got = Check-Aggregate $case['outcomes']
        if (Ck-SEq $got $case['expected']) { OK 'check' }
        else { FAIL 'check' "aggregate [$(@($case['outcomes']) -join ',')]: expected $($case['expected']), got $got" }
    }
    foreach ($case in $v['object-vectors']) {
        $m = Infer-Types $case['object']
        $okc = $false
        if ([string]::Equals($case['expected'], 'valid', $ORD)) { $okc = (@($m).Count -eq 1 -and (Ck-SEq $m[0] $case['type'])) }
        else { $okc = (@($m).Count -eq 0) }
        if ($okc) { OK 'check' }
        else { FAIL 'check' "object $($case['name']): expected $($case['expected']) $($case['type']), matched [$(@($m) -join ',')]" }
    }
    foreach ($case in $v['bundle-vectors']) {
        $objs = (New-OMap); $untyped = New-Object System.Collections.ArrayList
        foreach ($o in $case['objects']) {
            $t = Infer-Single $o
            if ($null -ne $t) { $objs[[string]$o['id']] = @{t = $t; o = $o} } else { [void]$untyped.Add([string]$o['id']) }
        }
        $store = $null
        if ($case.Contains('store')) { $store = @{map = $case['store']} }
        $res = Check-Errors $objs $store
        $named = New-Object 'System.Collections.Generic.SortedSet[string]' ([System.StringComparer]::Ordinal)
        foreach ($e in $res.errs) { [void]$named.Add($e.rule) }
        $wantSet = New-Object 'System.Collections.Generic.SortedSet[string]' ([System.StringComparer]::Ordinal)
        foreach ($r in @($case['expected-rules'])) { if ($null -ne $r) { [void]$wantSet.Add([string]$r) } }
        $okc = ($untyped.Count -eq 0 -and $named.SetEquals($wantSet))
        foreach ($frag in @($case['expected-notes'])) {
            if ($null -eq $frag) { continue }
            $hit = $false
            foreach ($n in $res.notes) { if ($n.Contains($frag)) { $hit = $true } }
            if (-not $hit) { $okc = $false } }
        if ($okc) { OK 'check' }
        else {
            $msgs = New-Object System.Collections.ArrayList
            foreach ($e in $res.errs) { $m1 = $e.msg; if ($m1.Length -gt 150) { $m1 = $m1.Substring(0, 150) }; [void]$msgs.Add($m1) }
            FAIL 'check' "bundle $($case['name']): expected rules [$(@($case['expected-rules']) -join ',')] notes [$(@($case['expected-notes']) -join ' | ')], got [$(@($named) -join ',')] untyped [$(@($untyped) -join ',')] $(@($msgs) -join ' ~ ') notes $(@($res.notes) -join ' ~ ')" }
    }
}

# ---------------- ADVICE (CP-ADVICE-1, kernel 2.0.0) ----------------
# An advice pack is a bundle whose manifest carries a pack header and whose
# objects are Components: a vendor's recommendations as one published file.
# A capability is a CLAIM; the only statement that a requirement is met
# stays the Implementation in the user's namespace, which cites it.
# ADVICE-1..3 hold a pack to being advice; 4..7 hold capabilities and the
# edges that cite them, in every bundle; 8..10 hold the vendor's manifest a
# set keeps (packs/sha256/<hex>, beside the manifest like an envelope) to
# the objects in the set; 11 is import.
$PACK_STORE = 'packs/sha256/'
$ADVICE_RULES = @{
    'ADVICE-1' = 'advice must not be able to change what is required or how it is assessed - a pack holds Components and nothing else'
    'ADVICE-2' = "a pack cannot carry an object under someone else's identity, and so cannot replace one: its ids, its own id and its publisher share one origin"
    'ADVICE-3' = "advice must not reach a computation through a facet: no facet on a pack's object declares a semantics class"
    'ADVICE-4' = 'a capability-ref must name one thing: capability ids are unique within a Component'
    'ADVICE-5' = 'a recommendation is about a requirement; when that requirement is in the bundle the edge is typed and the clauses it names exist'
    'ADVICE-6' = "a suggested value the catalog cannot accept is the publisher's defect, found before a user adopts it"
    'ADVICE-7' = "an edge that leans on a capability nobody declared proves nothing, and advice applies to a system because the system contains the product - the cited component is in the bundle, declares the capability, and is the edge's own or one of its members"
    'ADVICE-8' = "a kept pack manifest is content-addressed and lives beside the manifest: its name is the SHA-256 of its bytes, it carries a pack header, and the bundle's manifest does not list it"
    'ADVICE-9' = 'the advice in the set is what the vendor published: every object a kept pack manifest lists is in the bundle at that version with that semantic digest'
    'ADVICE-10' = 'one release of a pack in a set, and one pack per object'
    'ADVICE-11' = 'import never overwrites what the pack does not own: it adds ids the bundle does not hold and replaces ids an earlier release of the same pack brought'
}
function Adv-Bad($errList, [string]$rule, [string]$where, [string]$msg) {
    [void]$errList.Add(@{rule = $rule; msg = "${where}: $msg (${rule}: $($ADVICE_RULES[$rule]))"})
}
function Adv-Ids($objs) {
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { [void]$ids.Add([string]$oid) }
    return ,(Sorted-Ordinal $ids)
}
function Adv-CapIds($comp) {       # the capability ids a Component declares
    $s = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($c in @($comp['capabilities'])) { if ($null -ne $c) { [void]$s.Add([string]$c['id']) } }
    return ,$s
}
function Pack-Errors($manifest, $objs, $pinnedDecl) {
    # ADVICE-1..3 over a published pack -> list of @{rule; msg}. A manifest
    # without a pack header is not a pack and is held to nothing here.
    $errList = New-Object System.Collections.ArrayList
    if (-not (Is-Map $manifest) -or -not (Ck-Truthy $manifest['pack'])) { return ,$errList }
    $pack = $manifest['pack']; $pid0 = [string]$pack['id']
    $origin = Uri-Origin $pid0
    $ids = Adv-Ids $objs
    foreach ($oid in $ids) {
        $t = $objs[$oid].t
        if (-not [string]::Equals($t, 'component', $ORD)) {
            $hint = ''
            if ([string]::Equals($t, 'attestation', $ORD)) { $hint = ' (an attestation travels beside the manifest, D3.1)' }
            Adv-Bad $errList 'ADVICE-1' $pid0 "$oid is a $t - an advice pack holds components only$hint"
        }
    }
    $pub = [string]$pack['publisher']['ref']
    if (-not (Str-Eq (Uri-Origin $pub) $origin)) { Adv-Bad $errList 'ADVICE-2' $pid0 "publisher $pub is not under the pack's origin $origin" }
    foreach ($oid in $ids) {
        if (-not (Str-Eq (Uri-Origin $oid) $origin)) { Adv-Bad $errList 'ADVICE-2' $pid0 "$oid is not under the pack's origin $origin" }
    }
    foreach ($oid in $ids) {
        $facets = $objs[$oid].o['facets']
        if ($null -eq $facets) { continue }
        $keys = New-Object System.Collections.ArrayList
        foreach ($k in $facets.Keys) { [void]$keys.Add([string]$k) }
        foreach ($key in (Sorted-Ordinal $keys)) {
            if ($key.StartsWith('private:')) { continue }     # declares [] by definition (D10)
            $base = $key
            if ($key.LastIndexOf('@') -ge 0) { $base = $key.Substring(0, $key.LastIndexOf('@')) }
            $decl = $null
            if ($STDLIB_DECL.ContainsKey($base)) { $decl = $STDLIB_DECL[$base] }
            elseif ($null -ne $pinnedDecl -and $pinnedDecl.Contains($base)) { $decl = $pinnedDecl[$base] }
            $classes = New-Object System.Collections.ArrayList
            foreach ($c in @($decl)) { if ($null -ne $c) { [void]$classes.Add([string]$c) } }
            if ($classes.Count -gt 0) {      # unregistered is Facet-Errors' failure, not ours
                Adv-Bad $errList 'ADVICE-3' $oid "facet $key declares modifies-semantics ['$((Sorted-Ordinal $classes) -join "', '")'] - not allowed in an advice pack"
            }
        }
    }
    return ,$errList
}
function Capability-Errors($objs) {
    # ADVICE-4..6 over every Component -> @{errs; notes}
    $errList = New-Object System.Collections.ArrayList
    $notes = New-Object System.Collections.ArrayList
    foreach ($oid in (Adv-Ids $objs)) {
        if (-not [string]::Equals($objs[$oid].t, 'component', $ORD)) { continue }
        $o = $objs[$oid].o
        $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
        $dups = New-Object 'System.Collections.Generic.SortedSet[string]' ([System.StringComparer]::Ordinal)
        foreach ($c in @($o['capabilities'])) {
            if ($null -eq $c) { continue }
            if (-not $seen.Add([string]$c['id'])) { [void]$dups.Add([string]$c['id']) }
        }
        foreach ($n in $dups) { Adv-Bad $errList 'ADVICE-4' $oid "capability id '$n' is used twice" }
        $untyped = 0
        foreach ($c in @($o['capabilities'])) {
            if ($null -eq $c) { continue }
            $at = "$oid#$($c['id'])"
            $rref = $c['requirement-ref']
            if ($null -eq $rref) {
                if (Ck-Truthy $c['statement-ids']) { Adv-Bad $errList 'ADVICE-5' $at 'statement-ids without a requirement-ref' }
                continue
            }
            $req = Ck-Obj $objs $rref
            if ($null -eq $req) { $untyped++; continue }
            if (-not [string]::Equals($req.t, 'requirement', $ORD)) {
                Adv-Bad $errList 'ADVICE-5' $at "requirement-ref resolves to a $($req.t), not a Requirement: $rref"; continue }
            $sids = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
            foreach ($s in $req.o['statements']) { [void]$sids.Add([string]$s['id']) }
            $cover = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
            if (Ck-Truthy $c['statement-ids']) {
                foreach ($sid in $c['statement-ids']) {
                    if (-not $sids.Contains([string]$sid)) { Adv-Bad $errList 'ADVICE-5' $at "statement-id '$sid' names no statement of $rref" }
                    [void]$cover.Add([string]$sid)
                }
            } else { foreach ($sid in $sids) { [void]$cover.Add($sid) } }
            $decls = (New-Map)
            foreach ($s in $req.o['statements']) {
                if (-not $cover.Contains([string]$s['id'])) { continue }
                foreach ($pd in @($s['parameters'])) {
                    if ($null -eq $pd) { continue }
                    $pn = [string]$pd['name']
                    if (-not $decls.ContainsKey($pn)) { $decls[$pn] = New-Object System.Collections.ArrayList }
                    [void]$decls[$pn].Add($pd)
                }
            }
            $binds = $c['parameter-bindings']
            if (Is-Map $binds) {
                $names = New-Object System.Collections.ArrayList
                foreach ($k in $binds.Keys) { [void]$names.Add([string]$k) }
                foreach ($pn in (Sorted-Ordinal $names)) {
                    $found = 0
                    if ($decls.ContainsKey($pn)) { $found = $decls[$pn].Count }
                    if ($found -ne 1) {
                        Adv-Bad $errList 'ADVICE-6' $at "binds parameter '$pn', which is declared $found times on the covered statements of $rref"; continue }
                    $verdict = Param-Check $decls[$pn][0] $binds[$pn]
                    if (-not [string]::Equals($verdict, 'valid', $ORD)) {
                        $how = 'outside the declared space'
                        if ([string]::Equals($verdict, 'invalid', $ORD)) { $how = 'of the wrong kind' }
                        Adv-Bad $errList 'ADVICE-6' $at "binds parameter '$pn' to a value $how"
                    }
                }
            }
        }
        if ($untyped -gt 0) { [void]$notes.Add("${oid}: $untyped capability requirement-ref(s) outside the bundle - not typed (resolves-if-present)") }
    }
    return @{errs = $errList; notes = $notes}
}
function Split-CapRef([string]$ref, [string]$own) {
    # a bare id names a capability of the edge's own component;
    # <component-id>#<capability-id> names one of that component
    $i = $ref.LastIndexOf('#')
    if ($i -ge 0) { return @($ref.Substring(0, $i), $ref.Substring($i + 1)) }
    return @($own, $ref)
}
function Capability-Ref-Errors($objs) {
    # ADVICE-7 over every Implementation -> list of @{rule; msg}
    $errList = New-Object System.Collections.ArrayList
    foreach ($oid in (Adv-Ids $objs)) {
        if (-not [string]::Equals($objs[$oid].t, 'implementation', $ORD)) { continue }
        $o = $objs[$oid].o
        $own = [string]$o['component-ref']
        foreach ($sb in @($o['satisfied-by'])) {
            if ($null -eq $sb -or -not (Is-Map $sb) -or -not $sb.Contains('capability-ref')) { continue }
            $ref = [string]$sb['capability-ref']
            $sp = Split-CapRef $ref $own
            $cid = $sp[0]; $cap = $sp[1]
            $comp = Ck-Obj $objs $cid
            if ($null -eq $comp) {
                if (-not (Str-Eq $cid $own)) {      # the edge's own component is Closure-Errors' failure
                    $shown = $cid; if (Str-Eq $cid '') { $shown = '(none)' }
                    Adv-Bad $errList 'ADVICE-7' $oid "cites $ref, but component $shown is not in the bundle"
                }
                continue
            }
            if (-not [string]::Equals($comp.t, 'component', $ORD)) {
                Adv-Bad $errList 'ADVICE-7' $oid "cites $ref, which resolves to a $($comp.t), not a Component"; continue }
            if (-not (Adv-CapIds $comp.o).Contains($cap)) {
                Adv-Bad $errList 'ADVICE-7' $oid "cites capability '$cap', which $cid does not declare"; continue }
            if (-not (Str-Eq $cid $own)) {
                $owner = Ck-Obj $objs $own
                if ($null -ne $owner -and [string]::Equals($owner.t, 'component', $ORD)) {
                    $isMember = $false
                    foreach ($m in @($owner.o['members'])) { if ($null -ne $m -and (Ck-SEq $m['component-ref'] $cid)) { $isMember = $true } }
                    if (-not $isMember) { Adv-Bad $errList 'ADVICE-7' $oid "cites $ref, but $cid is not a member of $own" }
                }
            }
        }
    }
    return ,$errList
}
function Read-Kept-Packs([string]$bdir) {
    # -> list of @{name; raw} for the pack manifests a bundle keeps
    $out = New-Object System.Collections.ArrayList
    $d = Join-Path $bdir ($PACK_STORE.TrimEnd('/').Replace('/', '\'))
    if (-not (Test-Path $d -PathType Container)) { return ,$out }
    foreach ($f in (Get-ChildItem $d -File | Sort-Object Name)) {
        [void]$out.Add(@{name = $f.Name; raw = [System.IO.File]::ReadAllBytes($f.FullName)}) }
    return ,$out
}
function Kept-Pack-Errors($kept, $manifest, $objs) {
    # ADVICE-8..10 -> @{errs; packs} ; packs: the well-formed ones, @{name; km}
    $errList = New-Object System.Collections.ArrayList
    $packs = New-Object System.Collections.ArrayList
    $names = New-Object System.Collections.ArrayList
    $byName = (New-Map)
    foreach ($k in @($kept)) { if ($null -ne $k) { [void]$names.Add([string]$k.name); $byName[[string]$k.name] = $k } }
    foreach ($name in (Sorted-Ordinal $names)) {
        $raw = [byte[]]$byName[$name].raw
        $where = $PACK_STORE + $name
        if (-not (Str-Eq ((Sha256-Hex $raw).Substring(7)) $name)) { Adv-Bad $errList 'ADVICE-8' $where 'does not match its name'; continue }
        $km = $null
        try { $km = Parse-Json ([System.Text.Encoding]::UTF8.GetString($raw)) }
        catch { Adv-Bad $errList 'ADVICE-8' $where 'is not readable JSON'; continue }
        if (-not (Is-Map $km) -or -not (Test-Schema $DEFS['contentManifest'] $km) -or -not $km.Contains('pack')) {
            Adv-Bad $errList 'ADVICE-8' $where 'is not a content manifest with a pack header'; continue }
        [void]$packs.Add(@{name = $name; km = $km})
    }
    if (Is-Map $manifest) {
        foreach ($e in @($manifest['objects'])) {
            if ($null -eq $e -or -not (Is-Map $e)) { continue }
            $p = [string]$e['path']
            if ($p.StartsWith($PACK_STORE)) { Adv-Bad $errList 'ADVICE-8' $p "is listed in the bundle's manifest" }
        }
    }
    $release = (New-Map); $owner = (New-Map)
    foreach ($pk in $packs) {
        $km = $pk.km
        $pid0 = [string]$km['pack']['id']; $rel = [string]$km['pack']['version']
        if ($release.ContainsKey($pid0)) {
            Adv-Bad $errList 'ADVICE-10' $pid0 "releases $($release[$pid0]) and $rel are both in the bundle"; continue }
        $release[$pid0] = $rel
        foreach ($e in @($km['objects'])) {
            if ($null -eq $e) { continue }
            $eid = [string]$e['id']
            if ($owner.ContainsKey($eid)) {
                Adv-Bad $errList 'ADVICE-10' $eid "is listed by two kept manifests: $($owner[$eid]) and $pid0"; continue }
            $owner[$eid] = $pid0
            $tgt = Ck-Obj $objs $eid
            if ($null -eq $tgt) {
                Adv-Bad $errList 'ADVICE-9' $eid "is listed by release $rel of $pid0 and is not in the bundle" }
            elseif (-not (Ck-SEq $tgt.o['version'] $e['version'])) {
                Adv-Bad $errList 'ADVICE-9' $eid "is at version $($tgt.o['version']), release $rel of $pid0 lists $($e['version'])" }
            elseif (-not (Str-Eq (SDig $tgt.o) ([string]$e['semantic-digest']))) {
                Adv-Bad $errList 'ADVICE-9' $eid "differs from release $rel of $pid0 (semantic digest) - the vendor's advice was edited after import" }
        }
    }
    return @{errs = $errList; packs = $packs}
}
function Pack-Publisher($pack, [string]$mdigest, $objs, $envelopes, $trusted, $notes) {
    # claimed | proven: the same two words, and the same envelope check, as
    # the Tailoring tier (Derive-Tier). Proven needs an Attestation whose
    # signer has the pack's origin and which binds this manifest's digest;
    # in verification mode its envelope must verify under a trusted key.
    $origin = Uri-Origin ([string]$pack['id'])
    foreach ($oid in (Adv-Ids $objs)) {
        $o = $objs[$oid].o
        if (-not [string]::Equals($objs[$oid].t, 'attestation', $ORD)) { continue }
        if (-not (Str-Eq (Uri-Origin ([string]$o['signer'])) $origin)) { continue }
        if (-not (Ck-SEq $o['content-manifest-digest'] $mdigest)) { continue }
        if ($null -ne $trusted) {
            $env = $null
            if ($null -ne $envelopes -and $o.Contains('envelope-ref')) { $env = $envelopes[$o['envelope-ref']] }
            $st = 'error'; $why = 'unsigned attestation (no envelope) cannot prove in verification mode'
            if ($null -ne $env) { $r = Verify-Envelope $env $o $trusted; $st = $r[0]; $why = $r[1] }
            if (-not [string]::Equals($st, 'verified', $ORD)) {
                if ($null -ne $notes) { [void]$notes.Add("${oid}: $why") }
                continue
            }
        }
        return 'proven'
    }
    return 'claimed'
}
function Compose-Advice($aObjs, $aKept, $bManifest, [string]$bDigest, $bObjs, $pinnedDecl) {
    # ADVICE-11: what importing pack B into bundle A does. Nothing is
    # written; the result is the plan and its receipt.
    $R = @{result = 'refused'; added = (New-Object System.Collections.ArrayList); replaced = (New-Object System.Collections.ArrayList)
           removed = (New-Object System.Collections.ArrayList); dangling = (New-Object System.Collections.ArrayList)
           capabilities = (New-OMap); unchanged = $aObjs.Count; errors = (New-Object System.Collections.ArrayList)}
    $pack = $null
    if ((Is-Map $bManifest) -and (Ck-Truthy $bManifest['pack'])) { $pack = $bManifest['pack'] }
    if ($null -eq $pack) {
        Adv-Bad $R.errors 'ADVICE-11' '(import)' 'the manifest carries no pack header - this is not an advice pack'
        return $R
    }
    foreach ($e in (Pack-Errors $bManifest $bObjs $pinnedDecl)) { [void]$R.errors.Add($e) }
    foreach ($k in $aKept) { if (Str-Eq $k.name $bDigest) { $R.result = 'already-imported'; $R.errors.Clear(); return $R } }
    $packId = [string]$pack['id']
    $prev = 0
    $owned = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    $other = (New-Map)
    foreach ($k in $aKept) {
        $samePack = (Str-Eq ([string]$k.km['pack']['id']) $packId)
        if ($samePack) { $prev++ }
        foreach ($e in @($k.km['objects'])) {
            if ($null -eq $e) { continue }
            if ($samePack) { [void]$owned.Add([string]$e['id']) } else { $other[[string]$e['id']] = [string]$k.km['pack']['id'] }
        }
    }
    foreach ($oid in (Adv-Ids $bObjs)) {
        if (-not $aObjs.Contains($oid)) { [void]$R.added.Add($oid) }
        elseif ($owned.Contains($oid)) { [void]$R.replaced.Add($oid) }
        else {
            $whose = "not part of $packId"
            if ($other.ContainsKey($oid)) { $whose = "belongs to $($other[$oid])" }
            Adv-Bad $R.errors 'ADVICE-11' $oid "is already in the set and $whose"
        }
    }
    $gone = New-Object System.Collections.ArrayList
    foreach ($oid in $owned) { if ($aObjs.Contains($oid) -and -not $bObjs.Contains($oid)) { [void]$gone.Add($oid) } }
    foreach ($oid in (Sorted-Ordinal $gone)) { [void]$R.removed.Add($oid) }
    foreach ($oid in $R.replaced) {
        $old = (New-Map); $new = (New-Map)
        foreach ($c in @($aObjs[$oid].o['capabilities'])) { if ($null -ne $c) { $old[[string]$c['id']] = $c } }
        foreach ($c in @($bObjs[$oid].o['capabilities'])) { if ($null -ne $c) { $new[[string]$c['id']] = $c } }
        $d = @{added = (New-Object System.Collections.ArrayList); removed = (New-Object System.Collections.ArrayList); changed = (New-Object System.Collections.ArrayList)}
        foreach ($k in (Adv-Ids $new)) { if (-not $old.ContainsKey($k)) { [void]$d.added.Add($k) } }
        foreach ($k in (Adv-Ids $old)) {
            if (-not $new.ContainsKey($k)) { [void]$d.removed.Add($k) }
            elseif (-not (Str-Eq (Canonical $old[$k]) (Canonical $new[$k]))) { [void]$d.changed.Add($k) }
        }
        if (($d.added.Count + $d.removed.Count + $d.changed.Count) -gt 0) { $R.capabilities[$oid] = $d }
    }
    foreach ($iid in (Adv-Ids $aObjs)) {
        if (-not [string]::Equals($aObjs[$iid].t, 'implementation', $ORD)) { continue }
        $o = $aObjs[$iid].o
        foreach ($sb in @($o['satisfied-by'])) {
            if ($null -eq $sb -or -not (Is-Map $sb) -or -not $sb.Contains('capability-ref')) { continue }
            $ref = [string]$sb['capability-ref']
            $sp = Split-CapRef $ref ([string]$o['component-ref'])
            $cid = $sp[0]; $cap = $sp[1]
            $dropped = (Str-In $R.removed $cid)
            if (-not $dropped -and (Str-In $R.replaced $cid)) { $dropped = -not (Adv-CapIds $bObjs[$cid].o).Contains($cap) }
            if ($dropped) { [void]$R.dangling.Add("$iid -> $ref") }
        }
    }
    if ($R.errors.Count -gt 0) { return $R }
    if ($prev -gt 0) { $R.result = 'replace' } else { $R.result = 'import' }
    $R.unchanged = $aObjs.Count - $R.replaced.Count - $R.removed.Count
    return $R
}
function Advice-Errors($manifest, $objs, $pinnedDecl, $kept) {
    # everything ADVICE-1..10 says about one bundle -> @{errs; notes; packs}
    $errList = New-Object System.Collections.ArrayList
    $listed = (New-OMap)
    if (Is-Map $manifest) {
        foreach ($e in @($manifest['objects'])) {
            if ($null -ne $e -and (Is-Map $e) -and $objs.Contains([string]$e['id'])) { $listed[[string]$e['id']] = $objs[[string]$e['id']] } }
    }
    foreach ($e in (Pack-Errors $manifest $listed $pinnedDecl)) { [void]$errList.Add($e) }
    $ce = Capability-Errors $objs
    foreach ($e in $ce.errs) { [void]$errList.Add($e) }
    foreach ($e in (Capability-Ref-Errors $objs)) { [void]$errList.Add($e) }
    $ke = Kept-Pack-Errors $kept $manifest $objs
    foreach ($e in $ke.errs) { [void]$errList.Add($e) }
    return @{errs = $errList; notes = $ce.notes; packs = $ke.packs}
}
function Adv-Typed($objects) {
    $objs = (New-OMap); $untyped = New-Object System.Collections.ArrayList
    foreach ($o in @($objects)) {
        if ($null -eq $o) { continue }
        $t = Infer-Single $o
        if ($null -ne $t) { $objs[[string]$o['id']] = @{t = $t; o = $o} } else { [void]$untyped.Add([string]$o['id']) }
    }
    return @{objs = $objs; untyped = $untyped}
}
function Adv-Fill($manifest, $published) {
    # a vector's manifest lists its objects by id; version and digests are
    # COMPUTEd from the objects as published, so no literal goes stale
    $byId = (New-Map)
    foreach ($o in @($published)) { if ($null -ne $o) { $byId[[string]$o['id']] = $o } }
    $m = Copy-Deep $manifest
    foreach ($e in @($m['objects'])) {
        if ($null -eq $e) { continue }
        $src = $null
        if ($byId.ContainsKey([string]$e['id'])) { $src = $byId[[string]$e['id']] }
        if ((Ck-SEq $e['semantic-digest'] 'COMPUTE') -and $null -ne $src) { $e['semantic-digest'] = SDig $src }
        if (-not $e.Contains('version')) { if ($null -ne $src) { $e['version'] = $src['version'] } else { $e['version'] = '1' } }
        if (-not $e.Contains('package-digest')) { $e['package-digest'] = 'sha256:' + ('0' * 64) }
        if (-not $e.Contains('path')) {
            $id0 = [string]$e['id']
            $e['path'] = 'objects/' + $id0.Substring($id0.LastIndexOf('/') + 1) + '.json' }
    }
    return $m
}
function Adv-Kept($caseKept) {
    # -> list of @{name; raw} for a vector's kept manifests; the bytes are
    # the manifest's canonical form, `name` overrides the computed name
    $out = New-Object System.Collections.ArrayList
    foreach ($k in @($caseKept)) {
        if ($null -eq $k) { continue }
        if ($k.Contains('raw')) { $raw = [System.Text.Encoding]::UTF8.GetBytes([string]$k['raw']) }
        else { $raw = [System.Text.Encoding]::UTF8.GetBytes((Canonical (Adv-Fill $k['manifest'] $k['published']))) }
        $name = (Sha256-Hex $raw).Substring(7)
        if ($k.Contains('name')) { $name = [string]$k['name'] }
        [void]$out.Add(@{name = $name; raw = $raw})
    }
    return ,$out
}
function Adv-Judge([string]$kind, $case, $errs, $notes, [bool]$extraOk, $untyped) {
    $named = New-Object 'System.Collections.Generic.SortedSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($e in $errs) { [void]$named.Add($e.rule) }
    $wantSet = New-Object 'System.Collections.Generic.SortedSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($r in @($case['expected-rules'])) { if ($null -ne $r) { [void]$wantSet.Add([string]$r) } }
    $okc = ($extraOk -and @($untyped).Count -eq 0 -and $named.SetEquals($wantSet))
    foreach ($frag in @($case['expected-frags'])) {
        if ($null -eq $frag) { continue }
        $hit = $false
        foreach ($e in $errs) { if ($e.msg.Contains($frag)) { $hit = $true } }
        if (-not $hit) { $okc = $false } }
    foreach ($frag in @($case['expected-notes'])) {
        if ($null -eq $frag) { continue }
        $hit = $false
        foreach ($n in @($notes)) { if ($null -ne $n -and $n.Contains($frag)) { $hit = $true } }
        if (-not $hit) { $okc = $false } }
    if ($okc) { OK 'advice' }
    else {
        $msgs = New-Object System.Collections.ArrayList
        foreach ($e in $errs) { $m1 = $e.msg; if ($m1.Length -gt 150) { $m1 = $m1.Substring(0, 150) }; [void]$msgs.Add($m1) }
        FAIL 'advice' "$kind $($case['name']): expected rules [$(@($case['expected-rules']) -join ',')] frags [$(@($case['expected-frags']) -join ' | ')], got [$(@($named) -join ',')] untyped [$(@($untyped) -join ',')] $(@($msgs) -join ' ~ ') notes $(@($notes) -join ' ~ ')" }
}
function Adv-SameList($got, $want) {
    return (Str-Eq (@($got) -join "`n") (@($want) -join "`n")) -and (@($got).Count -eq @($want).Count)
}
function Run-Advice {
    $v = Load-Vectors 'advice-vectors.json'
    $none = New-Object System.Collections.ArrayList
    foreach ($case in $v['shape-vectors']) {
        $got = 'invalid'
        if ([string]::Equals($case['kind'], 'manifest', $ORD)) { if (Test-Schema $DEFS['contentManifest'] $case['document']) { $got = 'valid' } }
        else {
            $m = Infer-Types $case['document']
            if (@($m).Count -eq 1 -and (Ck-SEq $m[0] $case['kind'])) { $got = 'valid' }
        }
        if (Str-Eq $got $case['expected']) { OK 'advice' } else { FAIL 'advice' "shape $($case['name']): expected $($case['expected']), got $got" }
    }
    foreach ($case in $v['pack-vectors']) {
        $ty = Adv-Typed $case['objects']
        $m = Adv-Fill $case['manifest'] $case['objects']
        $errs = New-Object System.Collections.ArrayList
        if (-not (Test-Schema $DEFS['contentManifest'] $m)) { [void]$errs.Add(@{rule = 'SCHEMA'; msg = 'manifest schema violation'}) }
        else {
            foreach ($e in (Pack-Errors $m $ty.objs $case['declared'])) { [void]$errs.Add($e) }
            foreach ($e in (Kernel-Pin-Errors $m $ty.objs)) { [void]$errs.Add(@{rule = 'KERNEL-1'; msg = [string]$e}) }
        }
        Adv-Judge 'pack' $case $errs $none $true $ty.untyped
    }
    foreach ($case in $v['graph-vectors']) {
        $ty = Adv-Typed $case['objects']
        $ce = Capability-Errors $ty.objs
        $errs = New-Object System.Collections.ArrayList
        foreach ($e in $ce.errs) { [void]$errs.Add($e) }
        foreach ($e in (Capability-Ref-Errors $ty.objs)) { [void]$errs.Add($e) }
        Adv-Judge 'graph' $case $errs $ce.notes $true $ty.untyped
    }
    foreach ($case in $v['kept-vectors']) {
        $ty = Adv-Typed $case['objects']
        $ke = Kept-Pack-Errors (Adv-Kept $case['kept']) $case['manifest'] $ty.objs
        $extra = $true
        if ($case.Contains('expected-packs')) { $extra = ($ke.packs.Count -eq $case['expected-packs']) }
        Adv-Judge 'kept' $case $ke.errs $none $extra $ty.untyped
    }
    foreach ($case in $v['publisher-vectors']) {
        $m = Adv-Fill $case['manifest'] $case['published']
        $mdig = Sha256-Hex ([System.Text.Encoding]::UTF8.GetBytes((Canonical $m)))
        $subjects = Copy-Deep $case['objects']
        foreach ($o in @($subjects)) { if ($null -ne $o -and (Ck-SEq $o['content-manifest-digest'] 'COMPUTE')) { $o['content-manifest-digest'] = $mdig } }
        $ty = Adv-Typed $subjects
        $got = Pack-Publisher $m['pack'] $mdig $ty.objs $case['envelopes'] $case['trusted-keys'] $null
        if ((Str-Eq $got $case['expected']) -and $ty.untyped.Count -eq 0) { OK 'advice' }
        else { FAIL 'advice' "publisher $($case['name']): expected $($case['expected']), got $got untyped [$(@($ty.untyped) -join ',')]" }
    }
    foreach ($case in $v['import-vectors']) {
        $a = Adv-Typed $case['a']['objects']
        $aPacks = (Kept-Pack-Errors (Adv-Kept $case['a']['kept']) $null (New-OMap)).packs
        $b = Adv-Typed $case['b']['objects']
        $bm = Adv-Fill $case['b']['manifest'] $case['b']['objects']
        $bdig = (Sha256-Hex ([System.Text.Encoding]::UTF8.GetBytes((Canonical $bm)))).Substring(7)
        $R = Compose-Advice $a.objs $aPacks $bm $bdig $b.objs $null
        $exp = $case['expected']
        $same = $true
        if ($exp.Contains('result') -and -not (Ck-SEq $R.result $exp['result'])) { $same = $false }
        foreach ($k in @('added', 'replaced', 'removed', 'dangling')) {
            if ($exp.Contains($k) -and -not (Adv-SameList $R[$k] $exp[$k])) { $same = $false } }
        if ($exp.Contains('unchanged') -and ([int]$R.unchanged -ne [int]$exp['unchanged'])) { $same = $false }
        $unt = New-Object System.Collections.ArrayList
        foreach ($x in $a.untyped) { [void]$unt.Add($x) }; foreach ($x in $b.untyped) { [void]$unt.Add($x) }
        Adv-Judge 'import' $case $R.errors $none $same $unt
    }
}
function Advice-Report([string]$section, [string]$bdir, $manifest, [byte[]]$rawManifest, $objs, $pinnedDecl, $envelopes, [switch]$Flat) {
    # CP-ADVICE-1 for one bundle: ADVICE-1..10, and who published what
    $ae = Advice-Errors $manifest $objs $pinnedDecl (Read-Kept-Packs $bdir)
    foreach ($e in $ae.errs) { FAIL $section $e.msg }
    foreach ($n in $ae.notes) { Write-Host "    note: $n" }
    $atts = (New-OMap)
    foreach ($oid in $objs.Keys) { if ([string]::Equals($objs[$oid].t, 'attestation', $ORD)) { $atts[[string]$oid] = $objs[$oid] } }
    $isPack = ((Is-Map $manifest) -and (Ck-Truthy $manifest['pack']) -and (Test-Schema $DEFS['contentManifest'] $manifest))
    if (($isPack -or (@($ae.packs).Count -gt 0)) -and -not $Flat) {
        # a pack's own Attestation, and the vendor's beside a set that kept a pack's manifest
        $listedPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
        foreach ($e in @($manifest['objects'])) { if ($null -ne $e) { [void]$listedPaths.Add([string]$e['path']) } }
        foreach ($bf in (Beside-Attestation-Files $bdir $listedPaths)) { $atts[[string]$bf.o['id']] = @{t = 'attestation'; o = $bf.o} }
    }
    $envs = (New-Map)
    if ($null -ne $envelopes) { foreach ($k in $envelopes.Keys) { $envs[[string]$k] = $envelopes[$k] } }
    foreach ($oid in $atts.Keys) {
        $a = $atts[$oid].o
        if (-not $a.Contains('envelope-ref')) { continue }
        $ref = [string]$a['envelope-ref']
        $ep = Join-Path $bdir $ref
        if (-not $envs.ContainsKey($ref) -and (Test-Path $ep -PathType Leaf)) { try { $envs[$ref] = Read-Json $ep } catch { } }
    }
    $jobs = New-Object System.Collections.ArrayList
    if ($isPack) { [void]$jobs.Add(@{pack = $manifest['pack']; mdig = (Sha256-Hex $rawManifest); where = 'pack'}) }
    foreach ($pk in $ae.packs) {
        [void]$jobs.Add(@{pack = $pk.km['pack']; mdig = ('sha256:' + $pk.name); where = "kept pack ($(@($pk.km['objects']).Count) object(s))"}) }
    foreach ($j in $jobs) {
        $pn = New-Object System.Collections.ArrayList
        $st = Pack-Publisher $j.pack $j.mdig $atts $envs $TRUSTED $pn
        $tag = 'publisher CLAIMED [header and prefix - UNPROVEN]'
        if ([string]::Equals($st, 'proven', $ORD)) {
            if ($null -ne $TRUSTED) { $tag = 'publisher PROVEN [attestation binds the manifest + signature VERIFIED]' }
            else { $tag = 'publisher ATTESTED, NOT VERIFIED [an attestation binds the manifest; no proof without --trusted-keys]' }
        }
        Write-Host "    $($j.where): $($j.pack['id']) release $($j.pack['version']) by $($j.pack['publisher']['ref']) = $tag"
        foreach ($n in $pn) { Write-Host "          $n" }
    }
}

# ---------------- attestation-binds, applied to a bundle (Appendix B.1.7; backlog #46) ----------------
# The port of the section of the same name in validate_core.py. The
# primitive is (attestation, bundle) -> Full Match | Semantic Match | fail.
# Until 2026-11-14 this file did not apply it to a bundle: an Attestation
# was read for its envelope, for a Tailoring's tier and for a pack's
# publisher, and never held to its subjects.
#
# Each subject is judged against the objects the manifest lists:
#   match    an object carries the signed semantic digest - the object of
#            that id where the subject names one, any object where it is a
#            bare digest;
#   differs  the object of that id carries another digest: its normative
#            content changed after signing;
#   absent   no object of that id, or no object with that digest: what is
#            not delivered cannot be recomputed.
# The manifest the Attestation binds is `this` one (the digest of its bytes
# as delivered), a `kept-pack` (a vendor's manifest the bundle keeps under
# packs/sha256/, D25) or an `other`.
#   Full Match      every subject matches, and the manifest is this one or a
#                   kept pack's;
#   Semantic Match  every subject matches, and the manifest is another: the
#                   content is proven, the packaging was altered (D7) -
#                   reported, never a failure and never Full;
#   fail            anything else, an Attestation without a subject included.
# The verdict is about digests. Whether the signature is valid is the
# envelope's matter and is reported beside it.
#
# A `fail` verdict fails the bundle when the Attestation is still claimed:
# lifecycle `active`. A draft is not issued yet, and a deprecated or
# withdrawn one is kept for the record; each is reported with its verdict
# and fails nothing (validate_core.py: argued there, the primitive does not
# speak of lifecycle).
function Beside-Attestation-Files([string]$bdir, $listedPaths) {
    # -> list of @{name; raw; o}: the Attestations BESIDE the manifest (D3.1) -
    # JSON files in the manifest's own folder that it does not list and that
    # type as an Attestation, in the order of their names (by code point, as
    # validate_core.py sorts them). An Attestation binds the digest of the
    # manifest's bytes, so the manifest cannot list it; this is where every
    # bundle keeps one. A file that is not UTF-8 JSON is no Attestation and
    # is passed over, as validate_core.py passes over it. A hidden file is
    # read like any other (-Force), as os.listdir() lists it there.
    $out = New-Object System.Collections.ArrayList
    $byName = (New-Map)
    foreach ($f in (Get-ChildItem $bdir -File -Filter *.json -Force)) {
        # the provider's filter folds case on Windows; the reference asks for the ending as written
        if (-not $f.Name.EndsWith('.json', $ORD)) { continue }
        if ([string]::Equals($f.Name, 'content-manifest.json', $ORD) -or $listedPaths.Contains($f.Name)) { continue }
        $byName[$f.Name] = $f.FullName
    }
    foreach ($name in (Sorted-CodePoint $byName.Keys)) {
        try {
            $raw = [System.IO.File]::ReadAllBytes($byName[$name])
            $o = Ck-Json-Bytes $raw
        } catch { continue }
        if ((Is-Map $o) -and [string]::Equals((Infer-Single $o), 'attestation', $ORD)) { [void]$out.Add(@{name = $name; raw = $raw; o = $o}) }
    }
    return ,$out
}
function Attestation-Binds($att, $manifestDigest, $objs, $keptPacks) {
    # -> @{verdict; manifest; subjects; fails}. subjects: one @{st; id; signed;
    # have} per subject, in the Attestation's order - the status, the id it
    # names or $null, the signed digest, the delivered digest or $null.
    # objs: id -> @{t; o}, the objects the manifest lists. keptPacks: the
    # digests of the pack manifests the bundle keeps.
    $delivered = (New-Map)
    $carried = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($oid in $objs.Keys) {
        $d = SDig $objs[$oid].o
        $delivered[[string]$oid] = $d
        [void]$carried.Add($d)
    }
    $subjects = New-Object System.Collections.ArrayList
    if (Is-List $att['subject-semantic-digests']) {
        foreach ($sj in $att['subject-semantic-digests']) {
            if (Is-Map $sj) {
                # a subject that names an id is compared with the object of that id, and with no other
                $sid = $sj['id']; $signed = $sj['semantic-digest']
                $have = $null
                if (($sid -is [string]) -and $delivered.ContainsKey($sid)) { $have = $delivered[$sid] }
                $st = 'differs'
                if ($null -eq $have) { $st = 'absent' } elseif (Str-Eq $have $signed) { $st = 'match' }
                [void]$subjects.Add(@{st = $st; id = $sid; signed = $signed; have = $have})
            }
            elseif (($sj -is [string]) -and $carried.Contains($sj)) { [void]$subjects.Add(@{st = 'match'; id = $null; signed = $sj; have = $sj}) }
            else { [void]$subjects.Add(@{st = 'absent'; id = $null; signed = $sj; have = $null}) }
        }
    }
    $bound = $att['content-manifest-digest']
    $manifest = 'other'
    if (Str-Eq $bound $manifestDigest) { $manifest = 'this' }
    elseif (Str-In $keptPacks $bound) { $manifest = 'kept-pack' }
    $allMatch = ($subjects.Count -gt 0)
    foreach ($s in $subjects) { if (-not [string]::Equals($s.st, 'match', $ORD)) { $allMatch = $false } }
    $verdict = 'fail'
    if ($allMatch) {
        if ([string]::Equals($manifest, 'other', $ORD)) { $verdict = 'semantic-match' } else { $verdict = 'full-match' }
    }
    $fails = ([string]::Equals($verdict, 'fail', $ORD) -and [string]::Equals($att['lifecycle'], 'active', $ORD))
    return @{verdict = $verdict; manifest = $manifest; subjects = $subjects; fails = $fails}
}
$BINDS_MANIFEST = Ord-Table @{'this' = 'this manifest'; 'kept-pack' = 'a pack manifest this bundle keeps'; 'other' = 'another manifest'}
function Binds-Report([string]$section, $atts, $manifestDigest, $objs, $kept) {
    # One line per Attestation read with a bundle, in the ordinal order of
    # the ids; a `fail` verdict fails the bundle, in the words of Appendix
    # B.1.7. atts: id -> object. kept: what Read-Kept-Packs returns - a kept
    # manifest is known by its name, as in validate_core.py.
    $packs = New-Object System.Collections.ArrayList
    foreach ($k in @($kept)) { if ($null -ne $k) { [void]$packs.Add('sha256:' + [string]$k.name) } }
    foreach ($aid in (Sorted-Ordinal $atts.Keys)) {
        $r = Attestation-Binds $atts[$aid] $manifestDigest $objs $packs
        $n = $r.subjects.Count; $what = $BINDS_MANIFEST[$r.manifest]
        if ([string]::Equals($r.verdict, 'full-match', $ORD)) {
            Write-Host "    binds: $aid = FULL MATCH [$n subject(s) of this bundle; $what]" }
        elseif ([string]::Equals($r.verdict, 'semantic-match', $ORD)) {
            Write-Host "    binds: $aid = SEMANTIC MATCH [$n subject(s) of this bundle; ${what}: the content is proven, the packaging was altered]" }
        else {
            $lines = New-Object System.Collections.ArrayList
            foreach ($s in $r.subjects) {
                if ([string]::Equals($s.st, 'match', $ORD)) { continue }
                $named = Ck-Truthy $s.id
                $who = $s.signed; if ($named) { $who = $s.id }
                if ([string]::Equals($s.st, 'differs', $ORD)) { $why = "recomputed semantic digest $($s.have), signed $($s.signed)" }
                elseif ($named) { $why = 'not an object of this bundle' }
                else { $why = 'no object of this bundle carries it' }
                [void]$lines.Add("subject ${who}: $why")
            }
            if ($lines.Count -eq 0) { [void]$lines.Add('it names no subject') }
            $detail = @($lines) -join '; '
            if ($r.fails) {
                FAIL $section "[attestation-binds] ${aid}: $detail - $what (B.1.7: an Attestation binds what is delivered, or it fails; a changed subject is normative content changed after signing)" }
            else {
                Write-Host "    binds: $aid = DOES NOT BIND [lifecycle $($atts[$aid]['lifecycle']): reported, not a failure] $detail - $what" }
        }
    }
}

# ---------------- bundle validation ----------------
$TRUSTED = $null
if (-not (Str-Eq $TrustedKeys '')) { $TRUSTED = Read-Json $TrustedKeys }
function Validate-Object([string]$section, [string]$path, $obj) {
    Number-Failures $section $path $null $obj
    $m = Infer-Types $obj
    if (@($m).Count -ne 1) {
        $why = ''
        if (@($m).Count -eq 0 -and (Is-Map $obj) -and ($obj.Contains('scenario') -or $obj.Contains('owner-ref'))) {
            $rv = Risk-Rule-Violations $obj     # the Risk signature: name the violated rule(s)
            if (@($rv).Count -gt 0) { $why = " - FAIL [$(@($rv) -join '] [')]" }
        }
        if (@($m).Count -eq 0) {
            $dv = Date-Rule-Violations $obj      # fields that 1.0.0 left as free text and 2.0.0 types (DATE-1..5)
            if (@($dv).Count -gt 0) { $why = "$why - FAIL [$(@($dv) -join '] [')] a date field of 1.0.0 is typed in 2.0.0" }
        }
        FAIL $section "${path}: matches [$(@($m) -join ',')]$why"
        return $null
    }
    OK $section
    $t = $m[0]
    $viol = Optional-Empty-Violations $obj
    if (@($viol).Count -gt 0) { FAIL $section "${path}: optional empty containers present: $(@($viol) -join ',')" }
    if ([string]::Equals($t, 'requirement', $ORD)) {
        $sids = New-Object System.Collections.ArrayList
        foreach ($s in $obj['statements']) {
            if (Str-In $sids $s['id']) { FAIL $section "${path}: duplicate statement ids (unique-within, B.1.3)" }
            [void]$sids.Add($s['id'])
        }
        foreach ($s in $obj['statements']) {
            $declared = New-Object System.Collections.ArrayList
            foreach ($p in @($s['parameters'])) { if ($null -ne $p) { [void]$declared.Add($p['name']) } }
            foreach ($lang in $s['prose'].Keys) {
                $txt = $s['prose'][$lang]
                if (Is-List $txt) { $txt = ($txt -join ' ') }
                foreach ($mt in [System.Text.RegularExpressions.Regex]::Matches($txt, '\{param:([^}]+)\}')) {
                    if (-not (Str-In $declared $mt.Groups[1].Value)) {
                        FAIL $section "${path}: unbound {param:$($mt.Groups[1].Value)} in statement $($s['id']) (prose-params-resolve)" } } }
        }
        if ($null -ne $obj['facets']) {
            foreach ($fid in $obj['facets'].Keys) {
                $payload = $obj['facets'][$fid]
                if ((Is-Map $payload) -and $payload.Contains('by-statement') -and (Is-Map $payload['by-statement'])) {
                    foreach ($sid in $payload['by-statement'].Keys) {
                        if (-not (Str-In $sids $sid)) {
                            FAIL $section "${path}: facet $fid by-statement key '$sid' names no statement (D10 rev)" } } } } }
    }
    return $t
}
# The envelope of one Attestation: envelope-ref resolves to a file BESIDE
# the manifest (nothing signed contains its own signature, D3). A ref that
# does not resolve fails, and so does a file that is not JSON. -> $true
# when the envelope was read into $envelopes.
function Read-Envelope([string]$section, [string]$bdir, [string]$oid, $att, $envelopes) {
    $ref = [string]$att['envelope-ref']
    $ep = Join-Path $bdir $ref
    if (-not (Test-Path $ep)) { FAIL $section "${oid}: envelope-ref '$ref' does not resolve beside the manifest"; return $false }
    try { $envelopes[$ref] = Read-Json $ep }
    catch { FAIL $section "${ref}: envelope unreadable: $($_.Exception.Message)"; return $false }
    return $true
}
function Validate-Bundle([string]$bdir, [switch]$Flat) {
    $bdir = $bdir.TrimEnd('\', '/')        # one spelling of the folder for everything below
    $section = $bdir.Replace($ROOT, '').TrimStart('\').Replace('\', '/')
    Write-Host "  -> $section"   # sign of life: big bundles run minutes with no output (P10 user report)
    $mpath = Join-Path $bdir 'content-manifest.json'
    if (-not (Test-Path $mpath)) { FAIL $section 'no content-manifest.json'; return }
    $manifest = Read-Json $mpath
    $rawManifest = [System.IO.File]::ReadAllBytes($mpath)
    Number-Failures $section 'content-manifest.json' $rawManifest $manifest
    if (Test-Schema $DEFS['contentManifest'] $manifest) { OK $section } else { FAIL $section 'manifest schema violation' }
    $typec = (New-Map)
    $seenIds = (New-Map)
    $bundleObjs = (New-OMap)
    foreach ($entry in $manifest['objects']) {
        $fp = Join-Path $bdir $entry['path']
        if (-not (Test-Path $fp)) { FAIL $section "$($entry['path']): listed but missing"; continue }
        $raw = [System.IO.File]::ReadAllBytes($fp)
        if (-not (Str-Eq (Sha256-Hex $raw) $entry['package-digest'])) { FAIL $section "$($entry['path']): package-digest mismatch" }
        $obj = Read-Json $fp
        Number-Failures $section $entry['path'] $raw $null      # the spelling; Validate-Object holds the value
        if (-not (Str-Eq (SDig $obj) $entry['semantic-digest'])) { FAIL $section "$($entry['path']): semantic-digest mismatch" }
        $t = Validate-Object $section $entry['path'] $obj
        if ($null -ne $t) {
            if (-not $typec.ContainsKey($t)) { $typec[$t] = 0 }
            $typec[$t]++
        }
        if (-not (Str-Eq $obj['id'] $entry['id'])) { FAIL $section "$($entry['path']): manifest id != object id" }
        if ($seenIds.ContainsKey($obj['id'])) { FAIL $section "$($entry['path']): object id already used (unique-within)" }
        $seenIds[$obj['id']] = $entry['path']
        if ($null -ne $t) { $bundleObjs[$obj['id']] = @{t = $t; o = $obj} }
    }
    # $listedObjs is what the manifest lists, and what attestation-binds
    # judges a subject against. In a bundle that is $bundleObjs; in a flat
    # folder $bundleObjs goes on to take the unlisted Attestations as well,
    # as `exobjs` does in validate_examples().
    $listedObjs = $bundleObjs
    # A flat folder (jascon\examples) keeps its objects beside the manifest,
    # as validate_examples() in validate_core.py reads it: every other .json
    # there is an object; an Attestation may stay unlisted (D3.1: it lives
    # BESIDE the manifest), anything else unlisted fails.
    if ($Flat) {
        $listedObjs = (New-OMap)
        foreach ($oid in $bundleObjs.Keys) { $listedObjs[$oid] = $bundleObjs[$oid] }
        $skip = New-Object 'System.Collections.Generic.HashSet[string]'
        [void]$skip.Add('content-manifest.json')
        foreach ($entry in $manifest['objects']) { [void]$skip.Add($entry['path']) }
        foreach ($fe in @($manifest['facet-schemas'])) { if ($null -ne $fe) { [void]$skip.Add($fe['path']) } }
        foreach ($sp in @($manifest['scales'])) { if ($null -ne $sp) { [void]$skip.Add($sp['path']) } }
        foreach ($f in (Get-ChildItem $bdir -File -Filter *.json | Sort-Object Name)) {
            if ($skip.Contains($f.Name)) { continue }
            $obj = Read-Json $f.FullName
            Number-Failures $section $f.Name ([System.IO.File]::ReadAllBytes($f.FullName)) $null
            $t = Validate-Object $section $f.Name $obj
            if (-not [string]::Equals($t, 'attestation', $ORD)) {
                if ($null -ne $t) { FAIL $section "$($f.Name): on disk but not in manifest" }
                continue
            }
            if (-not $typec.ContainsKey($t)) { $typec[$t] = 0 }
            $typec[$t]++
            if ($seenIds.ContainsKey($obj['id'])) { FAIL $section "$($f.Name): object id already used (unique-within)" }
            $seenIds[$obj['id']] = $f.Name
            $bundleObjs[$obj['id']] = @{t = $t; o = $obj}
        }
    }
    $pinned = (New-Map)
    $pinnedDecl = (New-Map)
    foreach ($fe in @($manifest['facet-schemas'])) {
        if ($null -eq $fe) { continue }
        $fp = Join-Path $bdir $fe['path']
        if (-not (Test-Path $fp)) { FAIL $section "$($fe['path']): pinned facet schema listed but missing"; continue }
        $raw = [System.IO.File]::ReadAllBytes($fp)
        if (-not (Str-Eq (Sha256-Hex $raw) $fe['digest'])) { FAIL $section "$($fe['path']): pinned facet schema digest mismatch" }
        $sd = Read-Json $fp
        Number-Failures $section $fe['path'] $raw $sd
        $sch = $sd['schema']; if ($null -eq $sch) { $sch = [ordered]@{type = 'object'} }
        $pinned[$sd['id']] = $sch
        # P10 #29: the pin's declaration feeds the attach/detach op-law; a
        # pin that omits it is dangerous-by-default (D10: all four classes)
        $md = $sd['modifies-semantics']
        if ($null -eq $md) { $md = @('assessment', 'tailoring', 'selection', 'rendering') }
        $pinnedDecl[$sd['id']] = $md
        # #26 (D26 final): stdlib pins must equal the descriptor VERBATIM
        if ($STDLIB.ContainsKey($sd['id'])) {
            if (-not (Str-Eq (Format-Canonical $sch) (Format-Canonical $STDLIB[$sd['id']]))) {
                FAIL $section "$($fe['path']): pin of stdlib facet $($sd['id']) DIVERGES from the normative descriptor (D26)" } }
    }
    # Attestations BESIDE the manifest (D3.1) are read with every bundle
    # (backlog #46). Until 2026-11-14 they were read for a pack only, in
    # Advice-Report, so a bundle's own Attestation - which cannot be listed,
    # because it binds the manifest's digest - was not typed, not held to its
    # envelope and never seen by the tier derivation. They are objects the run
    # validates and counts; they are not objects of the manifest, so
    # $bundleObjs stays what the manifest lists and $withAtts adds them where
    # a rule asks who attested what. A flat folder has read them already.
    $listedPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::Ordinal)
    foreach ($entry in $manifest['objects']) { [void]$listedPaths.Add($entry['path']) }
    $withAtts = $bundleObjs
    if (-not $Flat) {
        $withAtts = (New-OMap)
        foreach ($oid in $bundleObjs.Keys) { $withAtts[$oid] = $bundleObjs[$oid] }
        foreach ($bf in (Beside-Attestation-Files $bdir $listedPaths)) {
            Number-Failures $section $bf.name $bf.raw $null     # the spelling; Validate-Object holds the value
            $t = Validate-Object $section $bf.name $bf.o
            if (-not [string]::Equals($t, 'attestation', $ORD)) { continue }
            if (-not $typec.ContainsKey($t)) { $typec[$t] = 0 }
            $typec[$t]++
            $bid = $bf.o['id']
            if ($seenIds.ContainsKey($bid)) { FAIL $section "$($bf.name): object id already used by $($seenIds[$bid])" }
            $seenIds[$bid] = $bf.name
            $withAtts[$bid] = @{t = $t; o = $bf.o}
        }
    }
    # DSSE envelopes (#24), of every Attestation read with the bundle and not
    # only of the ones a tier derivation happens to consult. A flat folder is
    # held to them as a bundle is (backlog #46; until 2026-11-14 a ref that
    # did not resolve there was a note, as validate_examples() read none).
    # The two readers of validate_core.py differ in the order, and this
    # follows each: validate_bundle() resolves every envelope in the order
    # the objects were read and then verifies in the order of the ids by code
    # point; validate_examples() does both for one Attestation after the
    # other, in the order of the ids by UTF-16 code unit.
    $envelopes = (New-Map)
    $attIds = New-Object System.Collections.ArrayList
    foreach ($oid in $withAtts.Keys) { if ([string]::Equals($withAtts[$oid].t, 'attestation', $ORD)) { [void]$attIds.Add([string]$oid) } }
    $attOrder = Sorted-Ordinal $attIds
    if (-not $Flat) {
        $attOrder = Sorted-CodePoint $attIds
        foreach ($oid in $attIds) {
            if (Ck-Truthy $withAtts[$oid].o['envelope-ref']) { [void](Read-Envelope $section $bdir $oid $withAtts[$oid].o $envelopes) } }
    }
    foreach ($oid in $attOrder) {
        $att = $withAtts[$oid].o
        if (-not (Ck-Truthy $att['envelope-ref'])) { Write-Host "    dsse: $oid = no envelope (unsigned attestation)"; continue }
        if ($Flat) { if (-not (Read-Envelope $section $bdir $oid $att $envelopes)) { continue } }
        elseif ($null -eq $envelopes[[string]$att['envelope-ref']]) { continue }
        $vr = Verify-Envelope $envelopes[[string]$att['envelope-ref']] $att $TRUSTED
        if ([string]::Equals($vr[0], 'error', $ORD)) { FAIL $section "${oid}: dsse: $($vr[1])"; Write-Host "    dsse: $oid = FAIL - $($vr[1])" }
        elseif ([string]::Equals($vr[0], 'verified', $ORD)) { Write-Host "    dsse: $oid = signature VERIFIED (Ed25519)" }
        else { Write-Host "    dsse: $oid = signature UNVERIFIED - $($vr[1])" }
    }
    # attestation-binds (B.1.7): every Attestation read with the bundle is
    # held to its subjects and to the manifest it binds
    $atts = (New-OMap)
    foreach ($oid in $attIds) { $atts[$oid] = $withAtts[$oid].o }
    Binds-Report $section $atts (Sha256-Hex $rawManifest) $listedObjs (Read-Kept-Packs $bdir)
    foreach ($e in (Closure-Errors $bundleObjs)) { FAIL $section $e }
    foreach ($e in (Duty-Errors $withAtts $pinnedDecl $envelopes $TRUSTED)) { FAIL $section $e }
    foreach ($e in (Kernel-Pin-Errors $manifest $bundleObjs)) { FAIL $section $e }
    # pinned scale definitions: SCALE-1 on each pin, SCALE-2/3 on the Risks
    $scaleDefs = (New-Map)
    foreach ($sp in @($manifest['scales'])) {
        if ($null -eq $sp) { continue }
        $sfp = Join-Path $bdir $sp['path']
        if (-not (Test-Path $sfp)) { FAIL $section "$($sp['path']): pinned scale definition listed but missing"; continue }
        $sraw = [System.IO.File]::ReadAllBytes($sfp)
        if (-not (Str-Eq (Sha256-Hex $sraw) $sp['digest'])) { FAIL $section "$($sp['path']): pinned scale definition digest mismatch" }
        $sdef = Read-Json $sfp
        Number-Failures $section $sp['path'] $sraw $sdef
        $sde = Scale-Definition-Errors $sdef $sp
        foreach ($e in $sde) { FAIL $section $e }
        if ($sde.Count -eq 0) { $scaleDefs[[string]$sdef['id']] = $sdef }
    }
    foreach ($e in (Matrix-Errors $scaleDefs)) { FAIL $section $e }
    $se = Scale-Errors $scaleDefs $bundleObjs
    foreach ($e in $se.errs) { FAIL $section $e }
    foreach ($n in $se.notes) { Write-Host "    note: $n" }
    # CP-RISK-1: B.1.9 risk-coverage report (+ RISK-11 errors), RISK-9/10 notes
    $rc = Risk-Coverage $withAtts $envelopes $TRUSTED
    foreach ($e in $rc.errs) { FAIL $section $e }
    foreach ($n in $rc.notes) { Write-Host "    note: $n" }
    foreach ($n in (Risk-Link-Notes $bundleObjs)) { Write-Host "    note: $n" }
    # CP-AUTHOR-1: AUTHOR-1..4 (notes, or failures under -RequireAuthors) and REVIEW-1 (always notes)
    Report-Authors-And-Reviews $section $withAtts $envelopes
    # the policy switch applies even where the bundle carries no Risk at all
    if ($rc.risks -gt 0 -or $RequireRiskBasis) {
        foreach ($tid in @($rc.report.Keys)) {
            $r = $rc.report[$tid]
            if ([string]::Equals($tid, '*', $ORD)) { $tid = '(no Tailoring: every requirement is in play)' }
            $openTag = ''
            if ($r.isOpen) { $openTag = '+ (open: predicate select)' }
            Write-Host "    risk-coverage: $tid [$($r.tier)] selected=$($r.selected)$openTag justified=$($r.covered.Count) uncovered=$($r.uncovered.Count)"
            foreach ($q in $r.uncovered) {
                if ($RequireRiskBasis) { FAIL $section (Risk-Basis-Fail $tid $q) }
                else { Write-Host "      uncovered: $q" } }
        }
    }
    $pairs = New-Object System.Collections.ArrayList
    foreach ($oid in $bundleObjs.Keys) { [void]$pairs.Add(@($oid, $bundleObjs[$oid].o)) }
    foreach ($e in (Facet-Errors $pairs $pinned)) { FAIL $section $e }
    # CP-CHECK-1: check shapes, recomputed verdicts, the evidence chain in
    # the store beside the manifest
    $ce = Check-Errors $bundleObjs @{dir = $bdir}
    foreach ($e in $ce.errs) { FAIL $section $e.msg }
    foreach ($n in $ce.notes) { Write-Host "    note: $n" }
    # CP-ADVICE-1: pack rules, capabilities and the edges that cite them, kept manifests
    Advice-Report $section $bdir $manifest $rawManifest $bundleObjs $pinnedDecl $envelopes -Flat:$Flat
    foreach ($oid in $bundleObjs.Keys) {
        if ([string]::Equals($bundleObjs[$oid].t, 'tailoring', $ORD)) {
            $tier = Derive-Tier $bundleObjs[$oid].o $withAtts $envelopes $TRUSTED
            Write-Host "    tier: $oid = $tier"
        }
    }
    # on-disk vs manifest (a flat folder was checked above); one set lookup
    # per file ($listedPaths) - the nested loop was quadratic, 2.9 M compares on the ISM bundle
    # The path of a file below the bundle is taken from the enumeration itself,
    # never by cutting the bundle's path off a full path. Until 2026-11-14 it
    # was cut off at the LENGTH of the folder as the caller had spelled it, so a
    # folder named with a trailing separator, or by a short (8.3) path that
    # Windows spells out when it lists files, had every object reported as "on
    # disk but not in manifest". The workflow's runner names its temporary
    # folder that way; the end-to-end test of attestation-binds found it.
    # .NET returns each name as the path it was given plus what lies below it.
    $objRoot = Join-Path $bdir 'objects'
    $below = @()
    if ([System.IO.Directory]::Exists($objRoot)) {
        $below = @([System.IO.Directory]::GetFiles($objRoot, '*.json', [System.IO.SearchOption]::AllDirectories))
        [Array]::Sort($below, [System.StringComparer]::Ordinal)
    }
    foreach ($full in $below) {
        $rel = ('objects' + $full.Substring($objRoot.Length)).Replace('\', '/')
        if (-not $listedPaths.Contains($rel)) { FAIL $section "${rel}: on disk but not in manifest" }
    }
    $summary = @()
    foreach ($k in ($typec.Keys | Sort-Object)) { $summary += "$k=$($typec[$k])" }
    $passK = 0; if ($COUNTS.ContainsKey($section)) { $passK = $COUNTS[$section] }
    $failK = 0; if ($COUNTS.ContainsKey("${section}:FAIL")) { $failK = $COUNTS["${section}:FAIL"] }
    Write-Host "  ${section}: $passK pass, $failK fail  {$($summary -join ', ')}"
}

# ---------------- run ----------------
$SW = [System.Diagnostics.Stopwatch]::StartNew()
Write-Host '== conformance corpus (validate_core.ps1 - the weekend implementation) =='
Run-Jcs; Run-Modality; Run-Parameters; Run-Tailoring; Run-Attestation; Run-Facets
Run-References; Run-Lifecycle; Run-Tiers; Run-Dsse; Run-Composition; Run-Conditional
Run-Risk; Run-Kernel; Run-Scale; Run-Check; Run-Advice; Run-Author
$FAMILIES = @('jcs', 'modality', 'parameter', 'tailoring', 'attestation', 'facet',
              'reference', 'lifecycle', 'tier', 'dsse', 'composition', 'conditional', 'risk', 'kernel', 'scale', 'check', 'advice', 'author')
foreach ($k in $FAMILIES) {
    $p = 0; if ($COUNTS.ContainsKey($k)) { $p = $COUNTS[$k] }
    $f = 0; if ($COUNTS.ContainsKey("${k}:FAIL")) { $f = $COUNTS["${k}:FAIL"] }
    Write-Host "  ${k}: $p pass, $f fail"
}
Write-Host ("  vectors wall-clock: " + $SW.Elapsed.TotalSeconds.ToString('F1', $INV) + " s")

if (-not $VectorsOnly) {
    Write-Host '== bundles =='
    $targets = $Bundles
    $defaultRun = (@($targets).Count -eq 0)
    if ($defaultRun) {
        $targets = @()
        $ce = Join-Path $ROOT 'converted_examples'
        foreach ($corpus in (Get-ChildItem $ce -Directory | Sort-Object Name)) {
            foreach ($d in (Get-ChildItem $corpus.FullName -Directory | Sort-Object Name)) {
                if ($d.Name.EndsWith('-bundle')) { $targets += $d.FullName } } }
        # CP-ADVICE-1: the worked advice pack(s) of the skill
        $ep = Join-Path $SKILL 'example-packs'
        if (Test-Path $ep -PathType Container) {
            foreach ($d in (Get-ChildItem $ep -Directory | Sort-Object Name)) { $targets += $d.FullName } }
    }
    foreach ($t in $targets) { Validate-Bundle (Resolve-Path $t).Path }
    # The skill's example bundle belongs to the default run, as it does in
    # validate_core.py ("skill-examples"). It was absent here, so a pin in
    # jascon\examples that diverged from its stdlib descriptor (D26) was
    # seen only by an explicit bundle argument. It goes through
    # Validate-Bundle - the ONE pin loop of this file - so the default run
    # and an explicit run cannot give two verdicts on the folder.
    # -Flat reads the folder as validate_examples() does: the Attestation
    # beside the manifest is validated, any other unlisted .json fails.
    if ($defaultRun) { Validate-Bundle (Join-Path $SKILL 'examples') -Flat }
}
$SW.Stop()
Write-Host ("total wall-clock: " + $SW.Elapsed.TotalSeconds.ToString('F1', $INV) + " s")
$nfail = 0
foreach ($k in $COUNTS.Keys) { if ($k.EndsWith(':FAIL')) { $nfail += $COUNTS[$k] } }
if ($nfail -gt 0) {
    Write-Host "$nfail FAILURES:"
    foreach ($f in $FAILURES | Select-Object -First 40) { Write-Host "  - $f" }
    exit 1
}
Write-Host 'ALL GREEN'
exit 0
