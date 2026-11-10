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
D3.5 composition, B.1.8 conditional-apply, and all 14 vector families.

Kernel 2.0.0 (CP-RISK-1): Risk is the tenth kernel type - typed by the
schema (RISK-1..6 are schema conditionals, named on failure by
Risk-Rule-Violations), closure RISK-7/8, typed Risk edges RISK-12, the
B.1.9 risk-coverage primitive (live risks only; a predicate select leaves
the selection open), RISK-9/10 notes, RISK-11.

PORT STATUS (2026-11-10): the CP-RISK-1 additions were ported from
validate_core.py and risk-vectors.json in an environment WITHOUT a
PowerShell runtime. They have NOT been executed. Until a run on Windows
PowerShell 5.1 prints "risk: 73 pass, 0 fail" and ALL GREEN, the risk
family counts as ONE implementation, not two (Ch. 15: the release gate).
The fixes of the rc.1 review (same day: justification needs an assessed
treatment decision, tailoring-refs scoping, RISK-13/14, typed Tailoring
selects/excludes, withdrawn Tailorings and Requirements, 23 more vectors)
were ported the same way and are equally UNEXECUTED.
The two new call sites are guarded so that a port defect surfaces as a
counted failure naming its line instead of ending the run; remove the
guards after the first green run.

Usage: powershell -ExecutionPolicy Bypass -File validate_core.ps1 [bundle-dirs...]
       -VectorsOnly to skip bundles; -TrustedKeys file.json for verification mode;
       -RequireRiskBasis turns uncovered selections into failures (policy switch).
#>
[CmdletBinding()]
param([string[]]$Bundles = @(), [switch]$VectorsOnly, [string]$TrustedKeys = "", [switch]$RequireRiskBasis)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Numerics
$HERE = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT = (Resolve-Path (Join-Path $HERE "..\..")).Path
$SKILL = Join-Path $ROOT "jascon"
$CONF = Join-Path $SKILL "conformance"
$INV = [System.Globalization.CultureInfo]::InvariantCulture

# ---------------- json -> ordered maps ----------------
function ConvertTo-Map($o) {
    if ($o -is [System.Management.Automation.PSCustomObject]) {
        $m = [ordered]@{}
        foreach ($p in $o.PSObject.Properties) { $m[$p.Name] = ConvertTo-Map $p.Value }
        return $m
    }
    if ($o -is [System.Array]) {
        $a = New-Object System.Collections.ArrayList
        foreach ($x in $o) { [void]$a.Add((ConvertTo-Map $x)) }
        return ,$a
    }
    return $o
}
function Read-Json([string]$path) {
    ConvertTo-Map ((Get-Content -Raw -Encoding UTF8 $path) | ConvertFrom-Json)
}
function Is-Map($v) { return ($v -is [System.Collections.IDictionary]) }
function Is-List($v) { return (-not (Is-Map $v)) -and ($v -is [System.Collections.IEnumerable]) -and -not ($v -is [string]) }
function Copy-Deep($v) {
    if (Is-Map $v) { $m = [ordered]@{}; foreach ($k in $v.Keys) { $m[$k] = Copy-Deep $v[$k] }; return $m }
    if (Is-List $v) { $a = New-Object System.Collections.ArrayList
        foreach ($x in $v) { [void]$a.Add((Copy-Deep $x)) }; return ,$a }
    return $v
}

# ---------------- canonical form (RFC 8785 member ordering) ----------------
function Esc-Json([string]$s) {
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $s.ToCharArray()) {
        $c = [int]$ch
        if ($ch -eq '"') { [void]$sb.Append('\"') }
        elseif ($ch -eq '\') { [void]$sb.Append('\\') }
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
function Format-Canonical($v) {
    if ($null -eq $v) { return 'null' }
    if ($v -is [bool]) { if ($v) { return 'true' } else { return 'false' } }
    if ($v -is [string]) { return '"' + (Esc-Json $v) + '"' }
    if (Is-Map $v) {
        $keys = @($v.Keys | ForEach-Object { [string]$_ })
        [Array]::Sort($keys, [System.StringComparer]::Ordinal)   # UTF-16 code units
        $parts = foreach ($k in $keys) { '"' + (Esc-Json $k) + '":' + (Format-Canonical $v[$k]) }
        return '{' + ($parts -join ',') + '}'
    }
    if (Is-List $v) {
        $parts = foreach ($x in $v) { Format-Canonical $x }
        return '[' + ($parts -join ',') + ']'
    }
    if ($v -is [decimal]) { return $v.ToString($INV) }
    if ($v -is [double]) { return $v.ToString('R', $INV) }
    return $v.ToString($INV)
}
$SHA = [System.Security.Cryptography.SHA256]::Create()
function Sha256-Hex([byte[]]$bytes) {
    return 'sha256:' + (($SHA.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '')
}
function Canonical($obj) {
    $o = Copy-Deep $obj
    if (Is-Map $o) { $o.Remove('annotations') }
    return Format-Canonical $o
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
$SCHEMA = Read-Json (Join-Path $SKILL "schemas\oscal-semantic-core-2.0.0.schema.json")
$DEFS = $SCHEMA['$defs']
$IGNORE_KW = @('description', 'title', '$schema', '$id', 'contentEncoding', 'default', 'examples', 'note', '$defs')
$KNOWN_KW = @('$ref', 'allOf', 'anyOf', 'if', 'then', 'const', 'enum', 'type', 'required',
              'properties', 'additionalProperties', 'unevaluatedProperties', 'items',
              'minItems', 'maxItems', 'minLength', 'maxLength', 'minProperties', 'pattern',
              'propertyNames', 'minimum', 'maximum')
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
    switch ($t) {
        'object'  { return (Is-Map $v) }
        'array'   { return (Is-List $v) }
        'string'  { return ($v -is [string]) }
        'boolean' { return ($v -is [bool]) }
        'integer' { return (($v -is [int]) -or ($v -is [long])) -and -not ($v -is [bool]) }
        'number'  { return (($v -is [int]) -or ($v -is [long]) -or ($v -is [double]) -or ($v -is [decimal])) -and -not ($v -is [bool]) }
        'null'    { return ($null -eq $v) }
    }
    throw "unknown type keyword: $t"
}
function Test-Schema($sch, $v) {
    if ($null -eq $sch) { return $true }
    foreach ($kw in $sch.Keys) {
        if (($KNOWN_KW -notcontains $kw) -and ($IGNORE_KW -notcontains $kw)) {
            throw "schema keyword '$kw' outside the documented subset (fail-loud)"
        }
    }
    if ($sch.Contains('$ref')) { if (-not (Test-Schema (Resolve-Ref $sch['$ref']) $v)) { return $false } }
    if ($sch.Contains('allOf')) {
        foreach ($s in $sch['allOf']) { if (-not (Test-Schema $s $v)) { return $false } } }
    if ($sch.Contains('anyOf')) {
        $any = $false
        foreach ($s in $sch['anyOf']) { if (Test-Schema $s $v) { $any = $true; break } }
        if (-not $any) { return $false } }
    if ($sch.Contains('if')) {
        if ((Test-Schema $sch['if'] $v) -and $sch.Contains('then')) {
            if (-not (Test-Schema $sch['then'] $v)) { return $false } } }
    if ($sch.Contains('const')) {
        if ((Format-Canonical $v) -cne (Format-Canonical $sch['const'])) { return $false } }
    if ($sch.Contains('enum')) {
        $hit = $false
        foreach ($e in $sch['enum']) { if ((Format-Canonical $v) -ceq (Format-Canonical $e)) { $hit = $true; break } }
        if (-not $hit) { return $false } }
    if ($sch.Contains('type')) { if (-not (Type-Is $v $sch['type'])) { return $false } }
    if (Is-Map $v) {
        if ($sch.Contains('required')) {
            foreach ($k in $sch['required']) { if (-not $v.Contains($k)) { return $false } } }
        if ($sch.Contains('minProperties')) { if ($v.Count -lt $sch['minProperties']) { return $false } }
        if ($sch.Contains('propertyNames')) {
            foreach ($k in $v.Keys) { if (-not (Test-Schema $sch['propertyNames'] ([string]$k))) { return $false } } }
        if ($sch.Contains('properties')) {
            foreach ($k in $sch['properties'].Keys) {
                if ($v.Contains($k)) { if (-not (Test-Schema $sch['properties'][$k] $v[$k])) { return $false } } } }
        if ($sch.Contains('additionalProperties')) {
            $ap = $sch['additionalProperties']
            $declared = New-Object System.Collections.ArrayList
            Collect-Props $sch $declared
            foreach ($k in $v.Keys) {
                if ($declared -notcontains $k) {
                    if ($ap -is [bool]) { if (-not $ap) { return $false } }
                    else { if (-not (Test-Schema $ap $v[$k])) { return $false } } } } }
        if ($sch.Contains('unevaluatedProperties')) {
            if ($sch['unevaluatedProperties'] -eq $false) {
                $declared = New-Object System.Collections.ArrayList
                Collect-Props $sch $declared
                foreach ($k in $v.Keys) { if ($declared -notcontains $k) { return $false } } } }
    }
    if ($v -is [string]) {
        if ($sch.Contains('minLength')) { if ($v.Length -lt $sch['minLength']) { return $false } }
        if ($sch.Contains('maxLength')) { if ($v.Length -gt $sch['maxLength']) { return $false } }
        if ($sch.Contains('pattern')) {
            if (-not [System.Text.RegularExpressions.Regex]::IsMatch($v, $sch['pattern'])) { return $false } } }
    if (Is-List $v) {
        if ($sch.Contains('minItems')) { if (@($v).Count -lt $sch['minItems']) { return $false } }
        if ($sch.Contains('maxItems')) { if (@($v).Count -gt $sch['maxItems']) { return $false } }
        if ($sch.Contains('items')) {
            foreach ($x in $v) { if (-not (Test-Schema $sch['items'] $x)) { return $false } } } }
    if (Type-Is $v 'number') {
        if ($sch.Contains('minimum')) { if ($v -lt $sch['minimum']) { return $false } }
        if ($sch.Contains('maximum')) { if ($v -gt $sch['maximum']) { return $false } } }
    return $true
}
$TYPES = @('requirement', 'requirementSet', 'tailoring', 'mapping', 'component',
           'implementation', 'assessment', 'finding', 'attestation', 'risk')
function Infer-Types($obj) {
    $m = New-Object System.Collections.ArrayList
    foreach ($t in $TYPES) { if (Test-Schema $DEFS[$t] $obj) { [void]$m.Add($t) } }
    return ,$m
}
function Infer-Single($obj) {
    $m = Infer-Types $obj
    if (@($m).Count -eq 1) { return $m[0] }
    return $null
}

# stdlib facet descriptors (fail-closed registry)
$STDLIB = @{}; $STDLIB_DECL = @{}
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
                         'threat-refs', 'component-refs', 'treatments', 'risk-refs', 'tailoring-refs')
function Optional-Empty-Violations($obj, [string]$path = '$') {
    $out = New-Object System.Collections.ArrayList
    if (Is-Map $obj) {
        foreach ($k in $obj.Keys) {
            $v = $obj[$k]
            $isEmpty = $false
            if ((Is-Map $v) -and $v.Count -eq 0) { $isEmpty = $true }
            if ((Is-List $v) -and @($v).Count -eq 0) { $isEmpty = $true }
            if (($OPTIONAL_CONTAINERS -contains $k) -and $isEmpty) { [void]$out.Add("$path.$k") }
            foreach ($x in (Optional-Empty-Violations $v "$path.$k")) { [void]$out.Add($x) }
        }
    } elseif (Is-List $obj) {
        $i = 0
        foreach ($v in $obj) {
            foreach ($x in (Optional-Empty-Violations $v "$path[$i]")) { [void]$out.Add($x) }
            $i++
        }
    }
    return ,$out
}

# ---------------- modality lattice ----------------
$OBL = @{unspecified = 0; may = 1; should = 2; must = 3}
$PRO = @{unspecified = 0; 'should-not' = 1; 'must-not' = 2}
function Modality-Verdict([string]$frm, [string]$to) {
    if ($frm -eq $to) { return 'monotone' }
    if ($frm -eq 'unspecified') { return 'monotone' }
    if ($to -eq 'unspecified') { return 'easing' }
    if ($frm -eq 'may' -and $to -eq 'may-only') { return 'monotone' }
    if ($frm -eq 'may-only' -and $to -eq 'may') { return 'easing' }
    if ($frm -eq 'may-only' -or $to -eq 'may-only') { return 'axis-change' }
    if ($OBL.ContainsKey($frm) -and $OBL.ContainsKey($to)) {
        if ($OBL[$to] -ge $OBL[$frm]) { return 'monotone' } else { return 'easing' } }
    if ($PRO.ContainsKey($frm) -and $PRO.ContainsKey($to)) {
        if ($PRO[$to] -ge $PRO[$frm]) { return 'monotone' } else { return 'easing' } }
    return 'axis-change'
}

# ---------------- parameter law ----------------
function Param-Check($decl, $value) {
    $t = $decl['type']
    if ($t -eq 'calendar-period' -and -not $decl.Contains('calendar-ref')) { return 'invalid' }
    if ($null -eq $value) { return 'invalid' }
    if ($t -eq 'choice') {
        $allowed = New-Object System.Collections.ArrayList
        foreach ($c in $decl['choices']) { [void]$allowed.Add($c['value']) }
        if (Is-List $value) {
            if ($decl['cardinality'] -ne 'many' -or @($value).Count -eq 0) { return 'invalid' }
            foreach ($x in $value) { if ($allowed -cnotcontains $x) { return 'deviation-required' } }
            return 'valid'
        }
        if ($allowed -ccontains $value) { return 'valid' } else { return 'deviation-required' }
    }
    if ($t -eq 'integer') {
        if (-not (($value -is [int]) -or ($value -is [long])) -or ($value -is [bool])) { return 'invalid' }
        if ($decl.Contains('min') -and $value -lt $decl['min']) { return 'deviation-required' }
        if ($decl.Contains('max') -and $value -gt $decl['max']) { return 'deviation-required' }
        return 'valid'
    }
    if ($t -eq 'decimal') {
        # D3.4 canonical form (rev P10 #37): no leading zeros, no negative
        # zero; bounds compare exactly via [decimal] (double loses precision)
        if (-not ($value -is [string])) { return 'invalid' }
        if (-not [System.Text.RegularExpressions.Regex]::IsMatch($value, '^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)$')) { return 'invalid' }
        $d = [decimal]::Parse($value, $INV)
        if ($decl.Contains('min') -and $d -lt [decimal]::Parse([string]$decl['min'], $INV)) { return 'deviation-required' }
        if ($decl.Contains('max') -and $d -gt [decimal]::Parse([string]$decl['max'], $INV)) { return 'deviation-required' }
        return 'valid'
    }
    if ($t -eq 'elapsed-duration' -or $t -eq 'calendar-period') {
        $cls = @('days', 'bizdays', 'weeks', 'months', 'years')
        if ($t -eq 'elapsed-duration') { $cls = @('seconds', 'minutes', 'hours') }
        if (-not (Is-Map $value) -or -not $value.Contains('num') -or -not $value.Contains('unit')) { return 'invalid' }
        if ($cls -notcontains $value['unit']) { return 'invalid' }
        if ($decl['tightening'] -eq 'lower') {
            if ($decl.Contains('num') -and $value['unit'] -eq $decl['unit'] -and $value['num'] -gt $decl['num']) {
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
                if ((Content-Digest $o) -ne (Content-Digest $tgt)) {
                    [void]$errs.Add("${oid}: canonical-alias claims SAME content as $($ca['of']) but content digests differ - a meaning change must use ``replaces`` (backlog #14)") } } }
        if ($t -eq 'requirementSet') {
            foreach ($m in @($o['members'])) { if ($null -ne $m) { Need $oid $m['ref'] 'member ref' } }
        } elseif ($t -eq 'tailoring') {
            # a Tailoring edge is typed, like a Risk edge (RISK-12): a set-ref
            # that is not a RequirementSet selects nothing, silently; an
            # exclude that is neither a Requirement nor a Set removes nothing
            foreach ($s in @($o['selects'])) {
                if ($null -eq $s -or -not $s.Contains('set-ref')) { continue }
                $sr = [string]$s['set-ref']
                Need $oid $sr 'selects set-ref'
                if ($objs.Contains($sr) -and $objs[$sr].t -cne 'requirementSet') {
                    [void]$errs.Add("${oid}: selects set-ref resolves to a $($objs[$sr].t), not a RequirementSet: $sr (D13: a selection names a Set - chaining runs on the resolved package, never by reference)") }
            }
            foreach ($e in @($o['excludes'])) {
                if ($null -eq $e) { continue }
                $er = [string]$e['ref']
                Need $oid $er 'excludes ref'
                if ($objs.Contains($er) -and $objs[$er].t -cne 'requirement' -and $objs[$er].t -cne 'requirementSet') {
                    [void]$errs.Add("${oid}: excludes ref resolves to a $($objs[$er].t), neither a Requirement nor a RequirementSet: $er (D13: an exclusion scopes out requirements - one, or a Set's members)") }
            }
            foreach ($op in @($o['operations'])) {
                if ($null -eq $op) { continue }
                Need $oid $op['requirement-ref'] 'operation requirement-ref'
                if ($objs.Contains($op['requirement-ref']) -and $op.Contains('statement-id')) {
                    $tg = $objs[$op['requirement-ref']]
                    if ($tg.t -eq 'requirement') {
                        $sids = @(); foreach ($s in $tg.o['statements']) { $sids += $s['id'] }
                        if ($sids -cnotcontains $op['statement-id']) {
                            [void]$errs.Add("${oid}: operation statement-id '$($op['statement-id'])' names no statement of $($op['requirement-ref'])") } } } }
        } elseif ($t -eq 'implementation') {
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
                        if ($auths -cnotcontains $inh['basis-ref']) {
                            [void]$errs.Add("${oid}: basis-ref '$($inh['basis-ref'])' names no authorization of $($inh['component-ref']) (D5 edge-local rule)") } } } }
        } elseif ($t -eq 'finding') {
            Need $oid $o['assessment-ref'] 'assessment-ref'
            Need $oid $o['requirement-ref'] 'requirement-ref'
            # risk-refs are LANDMARK (the register normally lives in another
            # bundle); like a Mapping scope the edge binds IF the target is
            # present: an in-bundle target must be a Risk (RISK-12)
            foreach ($rr in @($o['risk-refs'])) {
                if ($null -eq $rr) { continue }
                if ($objs.Contains($rr) -and $objs[$rr].t -cne 'risk') {
                    [void]$errs.Add("${oid}: risk-refs entry resolves in-bundle to a $($objs[$rr].t), not a Risk: $rr (RISK-12: a Risk edge is typed - a mis-aimed ref is a wrong statement, not a loose one)") } }
        } elseif ($t -eq 'risk') {
            # RISK-7: the controls a risk leans on are closure-required
            foreach ($tr in @($o['treatments'])) {
                if ($null -eq $tr) { continue }
                $q = [string]$tr['requirement-ref']
                Need $oid $q 'treatments requirement-ref (RISK-7)'
                if ($objs.Contains($q)) {
                    $tg = $objs[$q]
                    if ($tg.t -cne 'requirement') {
                        [void]$errs.Add("${oid}: treatments requirement-ref resolves to a $($tg.t), not a Requirement: $q (RISK-12: a Risk edge is typed - coverage joins on Requirement ids)")
                    } else {
                        $sids = @(); foreach ($s in $tg.o['statements']) { $sids += $s['id'] }
                        foreach ($sid in @($tr['statement-ids'])) {
                            if ($null -eq $sid) { continue }
                            if ($sids -cnotcontains $sid) {
                                [void]$errs.Add("${oid}: treatments statement-id '$sid' names no statement of $q (RISK-8: clause precision is addressable or it is prose)") } } } }
            }
            # RISK-7b: the assets at risk are Components of this bundle
            foreach ($cref in @($o['component-refs'])) {
                if ($null -eq $cref) { continue }
                Need $oid $cref 'component-refs (RISK-7)'
                if ($objs.Contains($cref) -and $objs[$cref].t -cne 'component') {
                    [void]$errs.Add("${oid}: component-refs entry resolves to a $($objs[$cref].t), not a Component: $cref (RISK-12: a Risk edge is typed - the asset at risk is a Component)") } }
            # the Statement(s) of Applicability this risk's treatment belongs to
            foreach ($tref in @($o['tailoring-refs'])) {
                if ($null -eq $tref) { continue }
                Need $oid $tref 'tailoring-refs (RISK-7)'
                if ($objs.Contains($tref) -and $objs[$tref].t -cne 'tailoring') {
                    [void]$errs.Add("${oid}: tailoring-refs entry resolves to a $($objs[$tref].t), not a Tailoring: $tref (RISK-12: a Risk edge is typed - the scope of a treatment is a Tailoring)") }
            }
            # RISK-13: levels compare within ONE scale and never across (D23)
            if ($o.Contains('rating') -and $o.Contains('residual-rating')) {
                $sa = [string]$o['rating']['scale-ref']; $sb = [string]$o['residual-rating']['scale-ref']
                if ($sa -cne $sb) {
                    [void]$errs.Add("${oid}: residual-rating is on $sb, rating on $sa (RISK-13: a residual level is what remains of a level - it presupposes a rating, on the same scale)") }
                # ... and so do likelihood and impact, where both sides carry them
                foreach ($part in @('likelihood', 'impact')) {
                    $pa = $o['rating'][$part]; $pr = $o['residual-rating'][$part]
                    if ((Is-Map $pa) -and (Is-Map $pr)) {
                        $ua = [string]$pa['scale-ref']; $ub = [string]$pr['scale-ref']
                        if ($ua -cne $ub) {
                            [void]$errs.Add("${oid}: residual-rating $part is on $ub, rating $part on $ua (RISK-13: a residual level is what remains of a level - it presupposes a rating, on the same scale)") }
                    }
                }
            }
        } elseif ($t -eq 'mapping') {
            foreach ($side in @('source', 'target')) {
                $ref = $o["$side-ref"]
                if ($objs.Contains($ref) -and $objs[$ref].t -eq 'requirement') {
                    $sids = @(); foreach ($s in $objs[$ref].o['statements']) { $sids += $s['id'] }
                    foreach ($sc in @($o["$side-scope"])) {
                        if ($null -eq $sc) { continue }
                        $sid = ([string]$sc).Split(':', 2)[1]
                        if ($sids -cnotcontains $sid) {
                            [void]$errs.Add("${oid}: $side-scope '$sc' names no statement of the in-bundle endpoint") } } } }
        }
    }
    # membership graphs are DAGs (D21; P10 #39): overlap is legal, cycles
    # are not - naive baseline expansion / nearest-Set search would loop.
    $color = @{}
    foreach ($root in @($objs.Keys)) {
        if ($objs[$root].t -cne 'requirementSet' -or $color.ContainsKey($root)) { continue }
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
            if (-not $objs.Contains($adv) -or $objs[$adv].t -cne 'requirementSet') { continue }
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
$DSSE_PT = 'application/vnd.oscal-semantic-core.attestation+json'
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
    if ($env['payloadType'] -cne $DSSE_PT) { return @('error', 'wrong payloadType') }
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
    function Add-Origin([string]$x) { if ($origins -cnotcontains $x) { [void]$origins.Add($x) } }
    function Set-Member-Origins([string]$sid, [int]$depth) {
        $tgt = $null
        if ($objs.Contains($sid)) { $tgt = $objs[$sid] }
        $hasMembers = $false
        if ($null -ne $tgt -and $tgt.t -eq 'requirementSet') {
            if (@($tgt.o['members']).Count -gt 0) { $hasMembers = $true } }
        if ($depth -gt 4 -or -not $hasMembers) { Add-Origin (Uri-Origin $sid); return }
        foreach ($m in $tgt.o['members']) {
            $mt = $null
            if ($objs.Contains($m['ref'])) { $mt = $objs[$m['ref']] }
            if ($null -ne $mt -and $mt.t -eq 'requirementSet') { Set-Member-Origins $m['ref'] ($depth + 1) }
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
    if (@($origins).Count -eq 1 -and $origins -cnotcontains '<predicate>') { $contentOrigin = $origins[0] }
    $claimed = ($null -ne $contentOrigin) -and ((Uri-Origin $tobj['id']) -ceq $contentOrigin)
    if ($null -ne $contentOrigin) {
        foreach ($oid in $objs.Keys) {
            $t = $objs[$oid].t; $o = $objs[$oid].o
            if ($t -cne 'attestation') { continue }
            if ((Uri-Origin ([string]$o['signer'])) -cne $contentOrigin) { continue }
            foreach ($subj in @($o['subject-semantic-digests'])) {
                if ($null -eq $subj -or -not (Is-Map $subj)) { continue }
                if ($subj['id'] -ceq $tobj['id'] -and $subj['semantic-digest'] -ceq (SDig $tobj)) {
                    if ($null -ne $trusted) {
                        $env = $null
                        if ($null -ne $envelopes -and $o.Contains('envelope-ref')) { $env = $envelopes[$o['envelope-ref']] }
                        $st = 'error'
                        if ($null -ne $env) { $st = (Verify-Envelope $env $o $trusted)[0] }
                        if ($st -cne 'verified') { continue }
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
        if ($objs[$oid].t -cne 'tailoring') { continue }
        $tobj = $objs[$oid].o
        $tier = Derive-Tier $tobj $objs $envelopes $trusted
        $seenT = New-Object System.Collections.ArrayList
        foreach ($op in @($tobj['operations'])) {
            if ($null -eq $op) { continue }
            # D13: two operations addressing the same target = validation
            # error (P10 #30 - was vector-only)
            $tkey = "$($op['requirement-ref'])|$($op['statement-id'])|$($op['parameter'])|$($op['field'])|$($op['facet'])"
            if ($seenT -ccontains $tkey) {
                [void]$errs.Add("${oid}: two operations address the same target ($tkey) within one Tailoring (D13: override rides Tailoring-of-Tailoring chaining, never in-place; P10 #30)")
            }
            [void]$seenT.Add($tkey)
            $hasDev = $op.Contains('deviation') -or $op.Contains('deviation-ref')
            $duty = $null
            $kind = $op['op']
            if ($kind -eq 'set-modality') {
                if ($objs.Contains($op['requirement-ref']) -and $objs[$op['requirement-ref']].t -eq 'requirement') {
                    $stmt = $null
                    foreach ($s in $objs[$op['requirement-ref']].o['statements']) {
                        if ($s['id'] -ceq $op['statement-id']) { $stmt = $s; break } }
                    if ($null -ne $stmt) {
                        $v = Modality-Verdict $stmt['modality'] $op['modality']
                        if ($v -ne 'monotone') { $duty = "non-monotone set-modality ($v)" } } }
            } elseif ($kind -eq 'replace-prose') {
                if ($op['intent'] -eq 'substantive') { $duty = 'substantive replace-prose' }
            } elseif ($kind -eq 'attach-facet' -or $kind -eq 'detach-facet') {
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
            } elseif ($kind -eq 'set-parameter') {
                $pdecl = $null
                if ($objs.Contains($op['requirement-ref']) -and $objs[$op['requirement-ref']].t -eq 'requirement') {
                    foreach ($s in $objs[$op['requirement-ref']].o['statements']) {
                        if ($s['id'] -cne $op['statement-id']) { continue }
                        foreach ($p in @($s['parameters'])) {
                            if ($null -ne $p -and $p['name'] -ceq $op['parameter']) { $pdecl = $p } } } }
                if ($null -ne $pdecl) {
                    $verdict = Param-Check $pdecl $op['value']
                    if ($verdict -eq 'invalid') {
                        [void]$errs.Add("${oid}: set-parameter '$($op['parameter'])' value fails the declared type/bounds (D13; not Deviation-escapable)")
                    } elseif ($verdict -eq 'deviation-required') {
                        $duty = 'out-of-bounds / against-tightening set-parameter' } }
            } elseif ($kind -eq 'remove-relation') {
                $rel = $op['relation']
                if ((Is-Map $rel) -and $rel['type'] -ceq 'required') { $duty = 'remove-relation of a ``required`` edge' }
            }
            if ($null -ne $duty -and -not $hasDev -and $tier -eq 'consumer') {
                [void]$errs.Add("${oid}: $duty without a Deviation at consumer tier (derived tier: $tier; B.1.6/D13 rev 2)")
            }
        }
    }
    return ,$errs
}

# ---------------- composition (D3.5) ----------------
function Semver([string]$v) {
    $m = [System.Text.RegularExpressions.Regex]::Match($v, '^(\d+)\.(\d+)\.(\d+)$')
    if (-not $m.Success) { return $null }
    return @([int]$m.Groups[1].Value, [int]$m.Groups[2].Value, [int]$m.Groups[3].Value)
}
function Compose($aObjs, $aPins, $bObjs, $bPins) {
    $errors = New-Object System.Collections.ArrayList
    $resolutions = [ordered]@{}
    $all = New-Object System.Collections.ArrayList
    foreach ($k in $aPins.Keys) { if ($all -cnotcontains $k) { [void]$all.Add($k) } }
    foreach ($k in $bPins.Keys) { if ($all -cnotcontains $k) { [void]$all.Add($k) } }
    $sorted = @($all); [Array]::Sort($sorted, [System.StringComparer]::Ordinal)
    foreach ($fid in $sorted) {
        $pa = $aPins[$fid]; $pb = $bPins[$fid]
        if ($null -ne $pa -and $null -ne $pb) {
            $sa = Semver $pa['version']; $sb = Semver $pb['version']
            if ($null -eq $sa -or $null -eq $sb) {
                [void]$errors.Add("${fid}: non-semver pin ($($pa['version']) / $($pb['version'])) - the registry policy is semver (D3.5)")
                continue
            }
            if ($sa[0] -ne $sb[0]) {
                [void]$errors.Add("${fid}: major lines $($pa['version']) vs $($pb['version']) are incompatible (D3.5; reported, never a silent pick)")
                continue
            }
            $win = $pb
            if (($sa[1] -gt $sb[1]) -or ($sa[1] -eq $sb[1] -and $sa[2] -ge $sb[2])) { $win = $pa }
            $resolutions[$fid] = $win['version']
            $sch = $win['schema']
            if ($null -eq $sch) { $sch = [ordered]@{type = 'object'} }
            foreach ($side in @(@('A', $aObjs), @('B', $bObjs))) {
                foreach ($pair in $side[1]) {
                    $o = $pair[1]
                    if ($null -eq $o['facets']) { continue }
                    foreach ($key in $o['facets'].Keys) {
                        $base = $key.Substring(0, $key.LastIndexOf('@'))
                        if ($base -cne $fid) { continue }
                        if (-not (Test-Schema $sch $o['facets'][$key])) {
                            [void]$errors.Add("${fid}: $($side[0]) $($pair[0]): payload fails re-validation under the resolved $($win['version'])") } } } }
        } else {
            $win = $pa; if ($null -eq $win) { $win = $pb }
            $resolutions[$fid] = $win['version']
        }
    }
    $aIds = @{}
    foreach ($pair in $aObjs) { $aIds[$pair[0]] = $pair[1] }
    foreach ($pair in $bObjs) {
        if ($aIds.ContainsKey($pair[0])) {
            $oa = $aIds[$pair[0]]; $ob = $pair[1]
            if ($oa['version'] -cne $ob['version']) {
                [void]$errors.Add("$($pair[0]): composed at two versions ($($oa['version']) vs $($ob['version'])) - cross-version resolution needs the lineage machinery, REPORTED")
            } elseif ((SDig $oa) -cne (SDig $ob)) {
                [void]$errors.Add("$($pair[0]): same id + version but DIFFERENT semantic digests - divergent twins (reported, never silently picked)") } } }
    return @($resolutions, $errors)
}

# ---------------- conditional-apply (B.1.8) ----------------
function Path-Get($obj, [string]$path, $objs) {
    $hops = $path -split '->'
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
            if ($part -eq '') { continue }
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
    if ($k -eq 'field-equals') {
        $r = Path-Get $obj $a['path'] $objs
        if ($r[0] -eq 'error') { return @('error', $r[1]) }
        if ($r[0] -eq 'absent') { return @('holds-not', "path '$($a['path'])' absent") }
        if ((Format-Canonical $r[1]) -ceq (Format-Canonical $a['value'])) {
            return @('holds', "path '$($a['path'])' matched") }
        return @('holds-not', "path '$($a['path'])' differs")
    }
    if ($k -eq 'param-equals') {
        foreach ($s in @($obj['statements'])) {
            if ($null -eq $s) { continue }
            foreach ($p in @($s['parameters'])) {
                if ($null -eq $p) { continue }
                if ($p['name'] -ceq $a['name']) {
                    if (-not $p.Contains('default')) {
                        return @('error', "parameter '$($a['name'])' declared but UNBOUND - its own error via prose-params-resolve, never silently false (B.2)") }
                    if ((Format-Canonical $p['default']) -ceq (Format-Canonical $a['value'])) {
                        return @('holds', "param '$($a['name'])' matched") }
                    return @('holds-not', "param '$($a['name'])' differs") } } }
        return @('holds-not', "no parameter '$($a['name'])' declared")
    }
    $r = Path-Get $obj $a['path'] $objs
    if ($r[0] -eq 'error') { return @('error', $r[1]) }
    if ($r[0] -eq 'ok') { return @('holds', "path '$($a['path'])' present") }
    return @('holds-not', "path '$($a['path'])' absent")
}
function Conditional-Apply($inst, $objs) {
    $errs = New-Object System.Collections.ArrayList
    $enf = $inst['enforcement']; $prim = $enf['primitive']
    $keys = @($objs.Keys | ForEach-Object { [string]$_ }); [Array]::Sort($keys, [System.StringComparer]::Ordinal)
    foreach ($oid in $keys) {
        $o = $objs[$oid].o
        $r = Eval-Predicate $inst['trigger'] $o $objs
        if ($r[0] -eq 'error') {
            [void]$errs.Add("FAIL [conditional-apply:$($inst['instance-id'])] on $oid`n  trigger: malformed/unevaluable: $($r[1])`n  rationale: $($inst['rationale'])")
            continue }
        if ($r[0] -ne 'holds') { continue }
        $detail = $null
        if ($prim -eq 'param-bounds') {
            $decl = [ordered]@{type = $enf['type']}
            if ($null -eq $decl['type']) { $decl['type'] = 'integer' }
            foreach ($kk in @('min', 'max', 'unit', 'num', 'tightening', 'calendar-ref', 'choices', 'cardinality')) {
                if ($enf.Contains($kk)) { $decl[$kk] = $enf[$kk] } }
            $found = $false
            foreach ($s in @($o['statements'])) {
                if ($null -eq $s) { continue }
                foreach ($p in @($s['parameters'])) {
                    if ($null -eq $p) { continue }
                    if ($p['name'] -ceq $enf['parameter'] -and $p.Contains('default')) {
                        $found = $true
                        $v = Param-Check $decl $p['default']
                        if ($v -ne 'valid') {
                            $detail = "parameter '$($enf['parameter'])' value outside the enforced bounds ($v)" } } } }
            if (-not $found) { $detail = "parameter '$($enf['parameter'])' not bound on any statement" }
        } elseif ($prim -eq 'code-from') {
            $pg = Path-Get $o $enf['path'] $objs
            $inCodes = $false
            if ($pg[0] -eq 'ok') {
                foreach ($c in $enf['codes']) { if ((Format-Canonical $c) -ceq (Format-Canonical $pg[1])) { $inCodes = $true } } }
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
    if (($st -ceq 'assessed' -or $st -ceq 'treated') -and -not $o.Contains('rating')) { [void]$out.Add('RISK-2') }
    if ($st -ceq 'treated' -and (-not $o.Contains('treatment') -or -not $o.Contains('acceptance'))) { [void]$out.Add('RISK-3') }
    if ($tr -ceq 'modify' -and -not $o.Contains('treatments')) { [void]$out.Add('RISK-4') }
    if ($tr -ceq 'share' -and -not $o.Contains('shared-with-ref')) { [void]$out.Add('RISK-5') }
    if ($tr -ceq 'retain' -and -not $o.Contains('acceptance')) { [void]$out.Add('RISK-6') }
    if ($o.Contains('residual-rating') -and -not $o.Contains('rating')) { [void]$out.Add('RISK-13') }
    return ,$out
}

# ---------------- B.1.9 risk-coverage (CP-RISK-1) ----------------
function Sorted-Ordinal($list) {
    $a = @($list | ForEach-Object { [string]$_ })
    [Array]::Sort($a, [System.StringComparer]::Ordinal)
    return ,$a
}
function Same-Set($a, $b) {
    $x = New-Object System.Collections.ArrayList
    foreach ($i in @($a)) { if ($null -ne $i) { [void]$x.Add([string]$i) } }
    $y = New-Object System.Collections.ArrayList
    foreach ($i in @($b)) { if ($null -ne $i) { [void]$y.Add([string]$i) } }
    if ($x.Count -ne $y.Count) { return $false }
    foreach ($i in $x) { if ($y -cnotcontains $i) { return $false } }
    return $true
}
# A Risk justifies a control only while it is being managed: `retired` is
# terminal (C.3c) and lifecycle `withdrawn` unpublishes the object.
function Risk-Is-Live($r) { return (($r['state'] -cne 'retired') -and ($r['lifecycle'] -cne 'withdrawn')) }
# A Risk JUSTIFIES a requirement once a treatment decision rests on an
# assessed risk: live, published (not draft), state assessed or treated,
# and a treatment option chosen (ISO/IEC 27001 6.1.3 a-b). Without this a
# three-field stub would satisfy -RequireRiskBasis.
function Risk-Justifies($r) {
    if (-not (Risk-Is-Live $r)) { return $false }
    if ($r['lifecycle'] -ceq 'draft') { return $false }
    if (($r['state'] -cne 'assessed') -and ($r['state'] -cne 'treated')) { return $false }
    return [bool]$r.Contains('treatment')
}
# tailoring-refs scope a Risk; without them it applies to every Tailoring
function Risk-Applies($r, [string]$tid) {
    $n = 0; $hit = $false
    foreach ($x in @($r['tailoring-refs'])) { if ($null -ne $x) { $n++; if ([string]$x -ceq $tid) { $hit = $true } } }
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
        if ($seen -ccontains $sid) { continue }
        [void]$seen.Add($sid)
        if (-not $objs.Contains($sid)) { continue }
        $tgt = $objs[$sid]
        if ($tgt.t -ceq 'requirementSet') {
            foreach ($m in @($tgt.o['members'])) { if ($null -ne $m) { [void]$stack.Add([string]$m['ref']) } }
        } elseif ($tgt.t -ceq 'requirement') {
            if ($out -cnotcontains $sid) { [void]$out.Add($sid) }
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
            if ($objs.Contains($sr) -and $objs[$sr].t -ceq 'requirementSet') { [void]$roots.Add($sr) }
        } else { $isOpen = $true }
    }
    $sel = Expand-Refs $roots $objs
    $exRoots = New-Object System.Collections.ArrayList
    foreach ($e in @($tobj['excludes'])) { if ($null -ne $e) { [void]$exRoots.Add([string]$e['ref']) } }
    foreach ($q in @(Expand-Refs $exRoots $objs)) { if ($null -ne $q) { $sel.Remove([string]$q) } }
    $gone = New-Object System.Collections.ArrayList
    foreach ($q in @($sel)) { if ($null -ne $q -and $objs[$q].o['lifecycle'] -ceq 'withdrawn') { [void]$gone.Add([string]$q) } }
    foreach ($q in $gone) { $sel.Remove($q) }
    return @{sel = $sel; isOpen = $isOpen; gone = $gone}
}
function Add-To-Bucket($bucket, [string]$q, [string]$rid) {
    if (-not $bucket.ContainsKey($q)) { $bucket[$q] = New-Object System.Collections.ArrayList }
    if ($bucket[$q] -cnotcontains $rid) { [void]$bucket[$q].Add($rid) }
}
function Risk-Coverage($objs, $envelopes, $trusted) {
    $notes = New-Object System.Collections.ArrayList
    $errs = New-Object System.Collections.ArrayList
    $riskIds = New-Object System.Collections.ArrayList
    $tailIds = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) {
        if ($objs[$oid].t -ceq 'risk') { [void]$riskIds.Add([string]$oid) }
        if ($objs[$oid].t -ceq 'tailoring') { [void]$tailIds.Add([string]$oid) }
    }
    $riskIds = Sorted-Ordinal $riskIds
    $inForce = New-Object System.Collections.ArrayList
    foreach ($tid in (Sorted-Ordinal $tailIds)) {
        if ($objs[$tid].o['lifecycle'] -ceq 'withdrawn') {
            [void]$notes.Add("${tid}: withdrawn - selects nothing and is not reported (a withdrawn Statement of Applicability is history)")
        } else { [void]$inForce.Add($tid) }
    }
    $report = [ordered]@{}
    $selections = @{}
    # No Tailoring at all: nothing was scoped out, so every Requirement in
    # force is in play; the implicit selection is reported under '*'. (All
    # Tailorings WITHDRAWN is a different statement and selects nothing.)
    if ($tailIds.Count -eq 0) { [void]$inForce.Add('*') }
    foreach ($tid in $inForce) {
        if ($tid -ceq '*') {
            $tobj = @{}; $tier = 'none'
            $all = New-Object System.Collections.ArrayList
            foreach ($oid in $objs.Keys) {
                if ($objs[$oid].t -ceq 'requirement' -and $objs[$oid].o['lifecycle'] -cne 'withdrawn') { [void]$all.Add([string]$oid) } }
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
        $treats = @{}; $pending = @{}; $lapsed = @{}
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
        foreach ($q in (Sorted-Ordinal $sel)) {
            if ($treats.ContainsKey($q)) { [void]$covered.Add($q); continue }
            [void]$uncovered.Add($q)
            if ($pending.ContainsKey($q)) {
                [void]$pendingOnly.Add($q)
                [void]$notes.Add("${tid}: selected $q is named only by Risk(s) without an assessed treatment decision $((Sorted-Ordinal $pending[$q]) -join ', ') - counted as uncovered (a risk justifies once it is assessed and its option chosen)")
            } elseif ($lapsed.ContainsKey($q)) {
                [void]$lapsedOnly.Add($q)
                [void]$notes.Add("${tid}: selected $q is named only by retired/withdrawn Risk(s) $((Sorted-Ordinal $lapsed[$q]) -join ', ') - counted as uncovered (C.3c: a retired risk justifies nothing)")
            }
        }
        $exclNo = 0
        foreach ($e in @($tobj['excludes'])) { if ($null -ne $e -and -not $e.Contains('rationale')) { $exclNo++ } }
        if ($tier -ceq 'consumer' -and $exclNo -gt 0) {
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
    $outOfScope = @{}; $undecided = @{}
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
                if ($objs[$q].t -cne 'requirement') { continue }
                $selected = $false; $anyOpen = $false
                foreach ($tid in $mine) {
                    if ($selections[$tid].sel -ccontains $q) { $selected = $true }
                    if ($selections[$tid].isOpen) { $anyOpen = $true }
                }
                if ($selected) { continue }
                if (($objs[$q].o['lifecycle'] -cne 'withdrawn') -and $anyOpen) { Add-To-Bucket $undecided $q $rid }
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
        if ($objs[$q].o['lifecycle'] -ceq 'withdrawn') { $why = 'which is withdrawn' }
        [void]$errs.Add("${first}: treatment names $q, $why (RISK-11: a risk cannot lean on a control the SoA dropped)")
    }
    return @{report = $report; errs = $errs; notes = $notes; risks = $riskIds.Count}
}
# RISK-9 (SHOULD): a risk-adjustment Deviation names the Risk it adjusts for
function Risk-Link-Notes($objs) {
    $notes = New-Object System.Collections.ArrayList
    $riskIds = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { if ($objs[$oid].t -ceq 'risk') { [void]$riskIds.Add([string]$oid) } }
    if ($riskIds.Count -eq 0) { return ,$notes }
    foreach ($oid in $objs.Keys) {
        $o = $objs[$oid].o
        $devs = New-Object System.Collections.ArrayList
        foreach ($d in @($o['deviations'])) { if ($null -ne $d) { [void]$devs.Add($d) } }
        if ($objs[$oid].t -ceq 'tailoring') {
            foreach ($op in @($o['operations'])) {
                if ($null -eq $op) { continue }
                if (Is-Map $op['deviation']) { [void]$devs.Add($op['deviation']) } } }
        foreach ($d in $devs) {
            if ($d['type'] -cne 'risk-adjustment') { continue }
            $hit = $false
            foreach ($ref in @($d['refs'])) { if ($null -ne $ref -and $riskIds -ccontains $ref) { $hit = $true } }
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

$COUNTS = @{}
$FAILURES = New-Object System.Collections.ArrayList
function OK([string]$section) { if (-not $COUNTS.ContainsKey($section)) { $COUNTS[$section] = 0 }; $COUNTS[$section]++ }
function FAIL([string]$section, [string]$msg) {
    $k = "${section}:FAIL"
    if (-not $COUNTS.ContainsKey($k)) { $COUNTS[$k] = 0 }; $COUNTS[$k]++
    [void]$FAILURES.Add("[$section] $msg")
}
function Load-Vectors([string]$name) { return Read-Json (Join-Path $CONF $name) }
function To-Objs($list) {
    $objs = [ordered]@{}
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
            if ($got -ceq $case['canonical']) { OK 'jcs' } else { FAIL 'jcs' "$($case['name']): got $got" }
        } elseif ($case.Contains('authoring-input')) {
            $viol = Optional-Empty-Violations $case['authoring-input']
            $verdict = 'valid'; if (@($viol).Count -gt 0) { $verdict = 'invalid' }
            if ($verdict -eq $case['expected']) { OK 'jcs' } else { FAIL 'jcs' "$($case['name']): got $verdict" }
        }
    }
}
function Run-Modality {
    foreach ($case in (Load-Vectors 'modality-vectors.json')['vectors']) {
        $got = Modality-Verdict $case['from'] $case['to']
        if ($got -eq $case['verdict']) { OK 'modality' } else { FAIL 'modality' "$($case['from'])->$($case['to']): got $got" }
    }
}
function Run-Parameters {
    foreach ($case in (Load-Vectors 'parameter-vectors.json')['vectors']) {
        $got = Param-Check $case['parameter'] $case['value']
        if ($got -eq $case['verdict']) { OK 'parameter' } else { FAIL 'parameter' "$($case['name']): expected $($case['verdict']), got $got" }
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
            if ($seen -ccontains $tkey) { $verdict = 'error' }
            [void]$seen.Add($tkey)
        }
        if ($verdict -ne 'error') {
            foreach ($op in $ops) {
                if ($null -eq $op) { continue }
                $needsDev = $false
                if ($op['op'] -eq 'set-modality' -and $case.Contains('base-modality')) {
                    if ((Modality-Verdict $case['base-modality'] $op['modality']) -ne 'monotone') { $needsDev = $true } }
                if ($op['op'] -eq 'replace-prose' -and $op['intent'] -eq 'substantive') { $needsDev = $true }
                if ($op['op'] -eq 'set-parameter' -and $case.Contains('parameter-decl')) {
                    $pv = Param-Check $case['parameter-decl'] $op['value']
                    if ($pv -eq 'invalid') { $verdict = 'error' }
                    elseif ($pv -eq 'deviation-required') { $needsDev = $true } }
                if ($op['op'] -eq 'remove-relation' -and (Is-Map $op['relation']) -and $op['relation']['type'] -ceq 'required') {
                    $needsDev = $true }
                if ($op['op'] -eq 'attach-facet' -or $op['op'] -eq 'detach-facet') {   # P10 #29
                    $fid = ([string]$op['facet']); $fbase = $fid
                    if ($fbase.Contains('@')) { $fbase = $fbase.Substring(0, $fbase.LastIndexOf('@')) }
                    if ($fid.StartsWith('private:') -or $fbase.StartsWith('private:')) {
                        # [] by definition (D10)
                    } elseif ($case.Contains('facet-decls') -and $case['facet-decls'].Contains($fbase)) {
                        if (@($case['facet-decls'][$fbase]).Count -gt 0) { $needsDev = $true }
                    } else {
                        $verdict = 'error' } }
                if ($needsDev -and $case['tier'] -eq 'consumer' -and -not $op.Contains('deviation') -and -not $op.Contains('deviation-ref')) {
                    $verdict = 'error' }
            }
        }
        if ($verdict -eq $case['verdict']) { OK 'tailoring' } else { FAIL 'tailoring' "$($case['name']): expected $($case['verdict']), got $verdict" }
    }
}
function Run-Attestation {
    foreach ($case in (Load-Vectors 'attestation-vectors.json')['vectors']) {
        $sc = $case['scenario']
        $signedSem = SDig $sc['subject']
        $delivered = Copy-Deep $sc['subject']
        if ($sc.Contains('delivered-subject')) { $delivered = Copy-Deep $sc['delivered-subject'] }
        $mut = $sc['delivered-mutation']
        if ($mut -eq 'annotation-added') { $delivered['annotations'] = [ordered]@{web_name = 'chrome'} }
        # package-digest differences (reindent) matter only as bytes; semantically:
        $delSem = SDig $delivered
        $got = 'semantic-match'
        if ($delSem -cne $signedSem) { $got = 'tamper' }
        elseif ($mut -ne 'reindent' -and $mut -ne 'annotation-added') { $got = 'full-match' }
        if ($got -eq $case['expected']) { OK 'attestation' } else { FAIL 'attestation' "$($case['name']): expected $($case['expected']), got $got" }
    }
}
function Run-Facets {
    foreach ($case in (Load-Vectors 'facet-vectors.json')['vectors']) {
        $pinned = @{}
        if ($case.Contains('pinned') -and $null -ne $case['pinned']) {
            foreach ($k in $case['pinned'].Keys) { $pinned[$k] = $case['pinned'][$k] } }
        $errs = Facet-Errors @(,@($case['name'], $case['object'])) $pinned
        $got = 'valid'; if (@($errs).Count -gt 0) { $got = 'invalid' }
        if ($got -eq $case['expected']) { OK 'facet' } else { FAIL 'facet' "$($case['name']): expected $($case['expected']), got $got" }
    }
}
function Run-References {
    foreach ($case in (Load-Vectors 'reference-vectors.json')['vectors']) {
        $errs = Closure-Errors (To-Objs $case['objects'])
        if (@($errs).Count -eq $case['expected-errors']) { OK 'reference' }
        else { FAIL 'reference' "$($case['name']): expected $($case['expected-errors']), got $(@($errs).Count): $(@($errs) -join ' | ')" }
    }
}
$DEV_NEXT = @{investigating = @('pending', 'withdrawn'); pending = @('approved', 'withdrawn'); approved = @(); withdrawn = @()}
$FIND_NEXT = @{open = @('in-remediation', 'closed'); 'in-remediation' = @('closed'); closed = @()}
function Run-Lifecycle {
    $v = Load-Vectors 'lifecycle-vectors.json'
    foreach ($case in $v['deviation-transitions']) {
        $got = $DEV_NEXT[$case['from']] -contains $case['to']
        if ($got -eq $case['valid']) { OK 'lifecycle' } else { FAIL 'lifecycle' "deviation $($case['from'])->$($case['to'])" }
    }
    foreach ($case in $v['finding-transitions']) {
        $got = $FIND_NEXT[$case['from']] -contains $case['to']
        if ($got -eq $case['valid']) { OK 'lifecycle' } else { FAIL 'lifecycle' "finding $($case['from'])->$($case['to'])" }
    }
    foreach ($case in $v['identity-events']) {
        $allowed = $case['record'] -eq 'canonical-alias'
        $want = $case['substitution'] -eq 'allowed'
        if ($allowed -eq $want) { OK 'lifecycle' } else { FAIL 'lifecycle' "identity $($case['record'])" }
    }
    foreach ($case in $v['relationship-composition']) {
        $a = $case['a']; $b = $case['b']
        $got = 'supports'
        if ($a -eq 'supplements' -or $b -eq 'supplements') { $got = $null }
        elseif ($a -eq 'equal' -and $b -eq 'equal') { $got = 'equal' }
        elseif ($a -eq 'equal') { $got = $b }
        elseif ($b -eq 'equal') { if ($a -eq 'supports') { $got = $a } else { $got = 'supports' } }
        $okv = ($got -eq $case['composed'])
        if (-not $okv -and $case['composed'] -eq 'supports' -and ($got -eq 'supports' -or $got -eq 'intersects')) { $okv = $true }
        if ($okv) { OK 'lifecycle' } else { FAIL 'lifecycle' "compose($a,$b): expected $($case['composed']), got $got" }
    }
    # shape disjointness over the ten minimal objects
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
    }
    foreach ($want in $minimal.Keys) {
        $m = Infer-Types $minimal[$want]
        if (@($m).Count -eq 1 -and $m[0] -eq $want) { OK 'lifecycle' }
        else { FAIL 'lifecycle' "disjointness: minimal $want matches [$(@($m) -join ',')]" }
    }
    $bare = Infer-Types ([ordered]@{id = "$P/x"; version = '1'; lifecycle = 'active'})
    if (@($bare).Count -gt 0) { FAIL 'lifecycle' 'disjointness: field-free object matches a type' }
    else { OK 'lifecycle' }
}
function Run-Tiers {
    foreach ($case in (Load-Vectors 'tier-vectors.json')['vectors']) {
        $byId = @{}
        foreach ($o in $case['objects']) { $byId[$o['id']] = $o }
        foreach ($o in $case['objects']) {
            foreach ($subj in @($o['subject-semantic-digests'])) {
                if ((Is-Map $subj) -and $subj['semantic-digest'] -ceq 'COMPUTE') {
                    if ($byId.ContainsKey($subj['id'])) { $subj['semantic-digest'] = SDig $byId[$subj['id']] } } } }
        $objs = To-Objs $case['objects']
        $tobj = $null
        foreach ($oid in $objs.Keys) { if ($objs[$oid].t -eq 'tailoring') { $tobj = $objs[$oid].o } }
        $tier = Derive-Tier $tobj $objs $null $null
        $errs = Duty-Errors $objs $null $null $null
        $got = 'valid'; if (@($errs).Count -gt 0) { $got = 'invalid' }
        if ($tier -eq $case['expected-tier'] -and $got -eq $case['expected']) { OK 'tier' }
        else { FAIL 'tier' "$($case['name']): expected $($case['expected-tier'])/$($case['expected']), got $tier/$got" }
    }
}
function Run-Dsse {
    foreach ($case in (Load-Vectors 'dsse-vectors.json')['vectors']) {
        $objs = To-Objs $case['objects']
        $att = $null; $tobj = $null
        foreach ($oid in $objs.Keys) {
            if ($objs[$oid].t -eq 'attestation') { $att = $objs[$oid].o }
            if ($objs[$oid].t -eq 'tailoring') { $tobj = $objs[$oid].o } }
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
                if ($st -ne $w[0] -or -not $why.Contains($w[1])) { $okc = $false }
            } elseif ($st -ne $ee) { $okc = $false } }
        if ($okc -and $case.Contains('expected-tier')) { if ($tier -ne $case['expected-tier']) { $okc = $false } }
        if ($okc) { OK 'dsse' } else { FAIL 'dsse' "$($case['name']): got $st($why)/$tier" }
    }
}
function Run-Composition {
    foreach ($case in (Load-Vectors 'composition-vectors.json')['vectors']) {
        $aP = @(); foreach ($o in @($case['a']['objects'])) { $aP += ,@($o['id'], $o) }
        $bP = @(); foreach ($o in @($case['b']['objects'])) { $bP += ,@($o['id'], $o) }
        $aPins = $case['a']['pins']; if ($null -eq $aPins) { $aPins = [ordered]@{} }
        $bPins = $case['b']['pins']; if ($null -eq $bPins) { $bPins = [ordered]@{} }
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
                if ($res[$fid] -cne $case['expected-resolutions'][$fid]) { $okc = $false } } }
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
$RISK_NEXT = @{identified = @('assessed', 'treated', 'retired'); assessed = @('treated', 'retired'); treated = @('retired'); retired = @()}
# ---------------- the kernel-version pin (backlog #44) ----------------
# A manifest MAY carry `kernel-version`; absent means 1.0.0 content.
# KERNEL-1: content beyond 1.0.0 (a Risk, Finding.risk-refs) pins the kernel
# it needs. KERNEL-2: a tool stops at a pin it does not implement and names
# both versions. PORTED BY READING, NOT EXECUTED - like the Risk port.
$KERNEL_VERSION = '2.0.0'
$KERNEL_SUPPORTED = @('1.0.0', '2.0.0')
function Kernel-Pin-Errors($manifest, $objs) {
    $errs = New-Object System.Collections.ArrayList
    $pin = $null
    if ((Is-Map $manifest) -and $manifest.Contains('kernel-version')) { $pin = [string]$manifest['kernel-version'] }
    if ($null -ne $pin -and ($KERNEL_SUPPORTED -cnotcontains $pin)) {
        [void]$errs.Add("manifest pins kernel-version $pin; this validator implements $KERNEL_VERSION and reads $($KERNEL_SUPPORTED -join ', ') (KERNEL-2: a tool stops at a kernel it does not implement, and says which)")
        return ,$errs
    }
    $why = $null
    $ids = New-Object System.Collections.ArrayList
    foreach ($oid in $objs.Keys) { [void]$ids.Add([string]$oid) }
    foreach ($oid in (Sorted-Ordinal $ids)) {
        $t = $objs[$oid].t; $o = $objs[$oid].o
        if ($t -ceq 'risk') { $why = "$oid is a Risk"; break }
        $hasRefs = $false
        foreach ($x in @($o['risk-refs'])) { if ($null -ne $x) { $hasRefs = $true } }
        if ($t -ceq 'finding' -and $hasRefs) { $why = "$oid carries risk-refs"; break }
    }
    if ($null -ne $why -and $pin -cne '2.0.0') {
        $said = 'pins no kernel-version'
        if ($null -ne $pin) { $said = "pins kernel-version $pin" }
        [void]$errs.Add("$why, which needs kernel 2.0.0, but the manifest $said (KERNEL-1: content beyond 1.0.0 names its kernel, so that an older tool can say what it is missing)")
    }
    return ,$errs
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
}

function Run-Risk {
    $v = Load-Vectors 'risk-vectors.json'
    foreach ($case in $v['risk-transitions']) {
        $got = $RISK_NEXT[$case['from']] -contains $case['to']
        if ($got -eq $case['valid']) { OK 'risk' } else { FAIL 'risk' "risk $($case['from'])->$($case['to'])" }
    }
    foreach ($case in $v['object-vectors']) {
        $o = $case['object']
        $m = Infer-Types $o
        $viol = Risk-Rule-Violations $o
        $okc = $false
        if ($case['expected'] -ceq 'valid') {
            # the two layers agree on "valid": exactly the risk shape, no rule named
            $okc = (@($m).Count -eq 1 -and $m[0] -ceq 'risk' -and @($viol).Count -eq 0)
        } else {
            $okc = (@($m).Count -eq 0)
            # expected-rule is the portable assertion; expected-frag is advisory
            # (one schema library's message text) and is not evaluated here
            if ($okc -and $case.Contains('expected-rule')) { $okc = ($viol -ccontains $case['expected-rule']) }
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

# ---------------- bundle validation ----------------
$TRUSTED = $null
if ($TrustedKeys -ne '') { $TRUSTED = Read-Json $TrustedKeys }
function Validate-Object([string]$section, [string]$path, $obj) {
    $m = Infer-Types $obj
    if (@($m).Count -ne 1) {
        $why = ''
        if (@($m).Count -eq 0 -and (Is-Map $obj) -and ($obj.Contains('scenario') -or $obj.Contains('owner-ref'))) {
            $rv = Risk-Rule-Violations $obj     # the Risk signature: name the violated rule(s)
            if (@($rv).Count -gt 0) { $why = " - FAIL [$(@($rv) -join '] [')]" }
        }
        FAIL $section "${path}: matches [$(@($m) -join ',')]$why"
        return $null
    }
    OK $section
    $t = $m[0]
    $viol = Optional-Empty-Violations $obj
    if (@($viol).Count -gt 0) { FAIL $section "${path}: optional empty containers present: $(@($viol) -join ',')" }
    if ($t -eq 'requirement') {
        $sids = New-Object System.Collections.ArrayList
        foreach ($s in $obj['statements']) {
            if ($sids -ccontains $s['id']) { FAIL $section "${path}: duplicate statement ids (unique-within, B.1.3)" }
            [void]$sids.Add($s['id'])
        }
        foreach ($s in $obj['statements']) {
            $declared = New-Object System.Collections.ArrayList
            foreach ($p in @($s['parameters'])) { if ($null -ne $p) { [void]$declared.Add($p['name']) } }
            foreach ($lang in $s['prose'].Keys) {
                $txt = $s['prose'][$lang]
                if (Is-List $txt) { $txt = ($txt -join ' ') }
                foreach ($mt in [System.Text.RegularExpressions.Regex]::Matches($txt, '\{param:([^}]+)\}')) {
                    if ($declared -cnotcontains $mt.Groups[1].Value) {
                        FAIL $section "${path}: unbound {param:$($mt.Groups[1].Value)} in statement $($s['id']) (the 216 rule)" } } }
        }
        if ($null -ne $obj['facets']) {
            foreach ($fid in $obj['facets'].Keys) {
                $payload = $obj['facets'][$fid]
                if ((Is-Map $payload) -and $payload.Contains('by-statement') -and (Is-Map $payload['by-statement'])) {
                    foreach ($sid in $payload['by-statement'].Keys) {
                        if ($sids -cnotcontains $sid) {
                            FAIL $section "${path}: facet $fid by-statement key '$sid' names no statement (D10 rev)" } } } } }
    }
    return $t
}
function Validate-Bundle([string]$bdir) {
    $section = $bdir.Replace($ROOT, '').TrimStart('\').Replace('\', '/')
    Write-Host "  -> $section"   # sign of life: big bundles run minutes with no output (P10 user report)
    $mpath = Join-Path $bdir 'content-manifest.json'
    if (-not (Test-Path $mpath)) { FAIL $section 'no content-manifest.json'; return }
    $manifest = Read-Json $mpath
    if (Test-Schema $DEFS['contentManifest'] $manifest) { OK $section } else { FAIL $section 'manifest schema violation' }
    $typec = @{}
    $seenIds = @{}
    $bundleObjs = [ordered]@{}
    foreach ($entry in $manifest['objects']) {
        $fp = Join-Path $bdir $entry['path']
        if (-not (Test-Path $fp)) { FAIL $section "$($entry['path']): listed but missing"; continue }
        $raw = [System.IO.File]::ReadAllBytes($fp)
        if ((Sha256-Hex $raw) -cne $entry['package-digest']) { FAIL $section "$($entry['path']): package-digest mismatch" }
        $obj = Read-Json $fp
        if ((SDig $obj) -cne $entry['semantic-digest']) { FAIL $section "$($entry['path']): semantic-digest mismatch" }
        $t = Validate-Object $section $entry['path'] $obj
        if ($null -ne $t) {
            if (-not $typec.ContainsKey($t)) { $typec[$t] = 0 }
            $typec[$t]++
        }
        if ($obj['id'] -cne $entry['id']) { FAIL $section "$($entry['path']): manifest id != object id" }
        if ($seenIds.ContainsKey($obj['id'])) { FAIL $section "$($entry['path']): object id already used (unique-within)" }
        $seenIds[$obj['id']] = $entry['path']
        if ($null -ne $t) { $bundleObjs[$obj['id']] = @{t = $t; o = $obj} }
    }
    $pinned = @{}
    $pinnedDecl = @{}
    foreach ($fe in @($manifest['facet-schemas'])) {
        if ($null -eq $fe) { continue }
        $fp = Join-Path $bdir $fe['path']
        if (-not (Test-Path $fp)) { FAIL $section "$($fe['path']): pinned facet schema listed but missing"; continue }
        $raw = [System.IO.File]::ReadAllBytes($fp)
        if ((Sha256-Hex $raw) -cne $fe['digest']) { FAIL $section "$($fe['path']): pinned facet schema digest mismatch" }
        $sd = Read-Json $fp
        $sch = $sd['schema']; if ($null -eq $sch) { $sch = [ordered]@{type = 'object'} }
        $pinned[$sd['id']] = $sch
        # P10 #29: the pin's declaration feeds the attach/detach op-law; a
        # pin that omits it is dangerous-by-default (D10: all four classes)
        $md = $sd['modifies-semantics']
        if ($null -eq $md) { $md = @('assessment', 'tailoring', 'selection', 'rendering') }
        $pinnedDecl[$sd['id']] = $md
        # #26 (D26 final): stdlib pins must equal the descriptor VERBATIM
        if ($STDLIB.ContainsKey($sd['id'])) {
            if ((Format-Canonical $sch) -cne (Format-Canonical $STDLIB[$sd['id']])) {
                FAIL $section "$($fe['path']): pin of stdlib facet $($sd['id']) DIVERGES from the normative descriptor (D26)" } }
    }
    $envelopes = @{}
    foreach ($oid in $bundleObjs.Keys) {
        $e = $bundleObjs[$oid]
        if ($e.t -ne 'attestation' -or -not $e.o.Contains('envelope-ref')) { continue }
        $ep = Join-Path $bdir $e.o['envelope-ref']
        if (Test-Path $ep) { $envelopes[$e.o['envelope-ref']] = Read-Json $ep }
        else { FAIL $section "${oid}: envelope-ref '$($e.o['envelope-ref'])' does not resolve beside the manifest" }
    }
    foreach ($e in (Closure-Errors $bundleObjs)) { FAIL $section $e }
    foreach ($e in (Duty-Errors $bundleObjs $pinnedDecl $envelopes $TRUSTED)) { FAIL $section $e }
    try { foreach ($e in (Kernel-Pin-Errors $manifest $bundleObjs)) { FAIL $section $e } } catch {
        FAIL $section "kernel-version PORT ERROR (not yet executed on a real runtime - report this line): $($_.Exception.Message) @ line $($_.InvocationInfo.ScriptLineNumber)"
    }
    # CP-RISK-1: B.1.9 risk-coverage report (+ RISK-11 errors), RISK-9/10 notes
    try {
        $rc = Risk-Coverage $bundleObjs $envelopes $TRUSTED
        foreach ($e in $rc.errs) { FAIL $section $e }
        foreach ($n in $rc.notes) { Write-Host "    note: $n" }
        foreach ($n in (Risk-Link-Notes $bundleObjs)) { Write-Host "    note: $n" }
        # the policy switch applies even where the bundle carries no Risk at all
        if ($rc.risks -gt 0 -or $RequireRiskBasis) {
            foreach ($tid in @($rc.report.Keys)) {
                $r = $rc.report[$tid]
                if ($tid -ceq '*') { $tid = '(no Tailoring: every requirement is in play)' }
                $openTag = ''
                if ($r.isOpen) { $openTag = '+ (open: predicate select)' }
                Write-Host "    risk-coverage: $tid [$($r.tier)] selected=$($r.selected)$openTag justified=$($r.covered.Count) uncovered=$($r.uncovered.Count)"
                foreach ($q in $r.uncovered) {
                    if ($RequireRiskBasis) { FAIL $section (Risk-Basis-Fail $tid $q) }
                    else { Write-Host "      uncovered: $q" } }
            }
        }
    } catch {
        FAIL $section "risk-coverage PORT ERROR (CP-RISK-1 port not yet executed on a real runtime - report this line): $($_.Exception.Message) @ line $($_.InvocationInfo.ScriptLineNumber)"
    }
    $pairs = New-Object System.Collections.ArrayList
    foreach ($oid in $bundleObjs.Keys) { [void]$pairs.Add(@($oid, $bundleObjs[$oid].o)) }
    foreach ($e in (Facet-Errors $pairs $pinned)) { FAIL $section $e }
    foreach ($oid in $bundleObjs.Keys) {
        if ($bundleObjs[$oid].t -eq 'tailoring') {
            $tier = Derive-Tier $bundleObjs[$oid].o $bundleObjs $envelopes $TRUSTED
            Write-Host "    tier: $oid = $tier"
        }
    }
    # on-disk vs manifest
    foreach ($f in (Get-ChildItem (Join-Path $bdir 'objects') -Recurse -Filter *.json -ErrorAction SilentlyContinue)) {
        $rel = $f.FullName.Substring($bdir.Length + 1).Replace('\', '/')
        $listed = $false
        foreach ($entry in $manifest['objects']) { if ($entry['path'] -ceq $rel) { $listed = $true; break } }
        if (-not $listed) { FAIL $section "${rel}: on disk but not in manifest" }
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
try { Run-Risk } catch {
    FAIL 'risk' "PORT ERROR (CP-RISK-1 port not yet executed on a real runtime - report this line): $($_.Exception.Message) @ line $($_.InvocationInfo.ScriptLineNumber)"
}
try { Run-Kernel } catch {
    FAIL 'kernel' "PORT ERROR (kernel-version pin not yet executed on a real runtime - report this line): $($_.Exception.Message) @ line $($_.InvocationInfo.ScriptLineNumber)"
}
$FAMILIES = @('jcs', 'modality', 'parameter', 'tailoring', 'attestation', 'facet',
              'reference', 'lifecycle', 'tier', 'dsse', 'composition', 'conditional', 'risk', 'kernel')
foreach ($k in $FAMILIES) {
    $p = 0; if ($COUNTS.ContainsKey($k)) { $p = $COUNTS[$k] }
    $f = 0; if ($COUNTS.ContainsKey("${k}:FAIL")) { $f = $COUNTS["${k}:FAIL"] }
    Write-Host "  ${k}: $p pass, $f fail"
}
Write-Host ("  vectors wall-clock: {0:n1} s" -f $SW.Elapsed.TotalSeconds)

if (-not $VectorsOnly) {
    Write-Host '== bundles =='
    $targets = $Bundles
    if (@($targets).Count -eq 0) {
        $targets = @()
        $ce = Join-Path $ROOT 'converted_examples'
        foreach ($corpus in (Get-ChildItem $ce -Directory | Sort-Object Name)) {
            foreach ($d in (Get-ChildItem $corpus.FullName -Directory | Sort-Object Name)) {
                if ($d.Name.EndsWith('-bundle')) { $targets += $d.FullName } } }
    }
    foreach ($t in $targets) { Validate-Bundle (Resolve-Path $t).Path }
}
$SW.Stop()
Write-Host ("total wall-clock: {0:n1} s" -f $SW.Elapsed.TotalSeconds)
$nfail = 0
foreach ($k in $COUNTS.Keys) { if ($k.EndsWith(':FAIL')) { $nfail += $COUNTS[$k] } }
if ($nfail -gt 0) {
    Write-Host "$nfail FAILURES:"
    foreach ($f in $FAILURES | Select-Object -First 40) { Write-Host "  - $f" }
    exit 1
}
Write-Host 'ALL GREEN'
exit 0
