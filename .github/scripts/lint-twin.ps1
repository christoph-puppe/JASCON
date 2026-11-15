<#
lint-twin.ps1 - holds validate_core.ps1 to one rule: no PowerShell operator
ever compares two strings.

Why. JASCON compares identifiers code point by code point (D2) and never
normalizes (D3.4). PowerShell's comparison operators do neither. -eq, -ne,
-contains and their relatives fold case; all of them, the -c forms included,
compare under a culture, which ignores U+00AD SOFT HYPHEN and calls
canonically equivalent sequences equal. A Tailoring whose id differed from
its content's origin by one soft hyphen was read as the authority's own
(backlog #45, #58). The twin therefore compares strings with
[string]::Equals(a, b, $ORD) and the Str-In helper, and this script keeps
it that way.

How. The file is parsed with PowerShell's own parser, so comments, strings
and nested expressions are read as PowerShell reads them. For every binary
expression:

  - an operator that only makes sense on strings or collections of them
    (-like, -match, -replace, -split, -contains, -in, their negations and
    every -c and -i form) is a violation;
  - -eq and -ne are allowed when one operand is provably not a string:
    $null, $true, $false, a number literal, a cast to a numeric or boolean
    type, a .Count or .Length, a static member of a numeric type, the
    result of arithmetic other than +, or of one of the integer-returning
    calls named below. Anything else is a violation;
  - -lt, -le, -gt, -ge are refused when one operand is provably a string:
    a string literal or a cast to [string].

What it cannot see. Whether a variable holds a string. `$a -eq $b` is
refused even when both are numbers; write the cast (`[int]$a -eq [int]$b`).
`$x -eq 5` is accepted although PowerShell compares as strings when $x is
one; a digit string from data that differs from the number by an ignorable
character would pass there. No such comparison of a data string against a
number literal was found when the rule was introduced (2026-11-13).
The ordering operators get the weaker test because the twin orders
numbers with them in its inner loops and nothing else: strings are sorted
with [Array]::Sort and the ordinal comparer, never compared with -lt. Two
variables that hold strings, compared with -lt, would not be seen here.

Usage:  powershell -File .github\scripts\lint-twin.ps1 [path-to-ps1]
Exit code 1 and one line per violation when the rule is broken.
#>
[CmdletBinding()]
param([string]$Path = '')

$ErrorActionPreference = 'Stop'
if (-not $Path) {
    # The default is worked out here and from $MyInvocation, as validate_core.ps1
    # does. In a param() default, Windows PowerShell 5.1 has not set
    # $PSScriptRoot yet; PowerShell 7 has, so the first version of this
    # script ran on 7 and stopped on 5.1 (2026-11-13).
    $here = Split-Path -Parent $MyInvocation.MyCommand.Path
    $Path = Join-Path (Split-Path -Parent (Split-Path -Parent $here)) 'jascon/scripts/validate_core.ps1'
}
$tokens = $null; $parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path $Path).Path, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) { Write-Host "lint-twin: $Path does not parse: $($parseErrors[0].Message)"; exit 2 }

$EQUALITY = @('Ieq', 'Ine')
$ORDERING = @('Ilt', 'Ile', 'Igt', 'Ige')
$NUMERIC_TYPES = @('int', 'int32', 'long', 'int64', 'uint32', 'uint64', 'byte', 'double', 'decimal', 'bool', 'boolean', 'char',
                   'bigint', 'system.numerics.biginteger', 'system.int32', 'system.int64', 'system.decimal', 'system.double')
$NUMERIC_VARS = @('null', 'true', 'false')
$INT_MEMBERS = @('Count', 'Length', 'One', 'Zero', 'MinusOne', 'MaxValue', 'MinValue', 'Sign', 'ElapsedMilliseconds')
$INT_CALLS = @('CompareTo', 'IndexOf', 'LastIndexOf', 'Compare', 'CompareOrdinal', 'GetLength', 'ToInt32', 'ConvertToUtf32')
$ARITHMETIC = @('Minus', 'Multiply', 'Divide', 'Rem', 'Band', 'Bor', 'Bxor', 'Shl', 'Shr')

# Is this operand, read from the source alone, certainly not a string?
function Test-NotString($node) {
    while ($node -is [System.Management.Automation.Language.ParenExpressionAst]) {
        $p = $node.Pipeline
        if (($p -is [System.Management.Automation.Language.PipelineAst]) -and ($p.PipelineElements.Count -eq 1) -and
            ($p.PipelineElements[0] -is [System.Management.Automation.Language.CommandExpressionAst])) { $node = $p.PipelineElements[0].Expression }
        else { return $false }
    }
    if ($node -is [System.Management.Automation.Language.ConstantExpressionAst]) {
        if ($node -is [System.Management.Automation.Language.StringConstantExpressionAst]) { return $false }
        return ($node.Value -is [System.ValueType])
    }
    if ($node -is [System.Management.Automation.Language.VariableExpressionAst]) { return ($NUMERIC_VARS -contains $node.VariablePath.UserPath.ToLowerInvariant()) }
    if ($node -is [System.Management.Automation.Language.ConvertExpressionAst]) { return ($NUMERIC_TYPES -contains $node.Type.TypeName.FullName.ToLowerInvariant()) }
    if ($node -is [System.Management.Automation.Language.InvokeMemberExpressionAst]) {
        return (($node.Member -is [System.Management.Automation.Language.StringConstantExpressionAst]) -and ($INT_CALLS -contains $node.Member.Value))
    }
    if ($node -is [System.Management.Automation.Language.MemberExpressionAst]) {
        return (($node.Member -is [System.Management.Automation.Language.StringConstantExpressionAst]) -and ($INT_MEMBERS -contains $node.Member.Value))
    }
    if ($node -is [System.Management.Automation.Language.UnaryExpressionAst]) { return ($node.TokenKind.ToString() -eq 'Minus') -and (Test-NotString $node.Child) }
    if ($node -is [System.Management.Automation.Language.BinaryExpressionAst]) { return ($ARITHMETIC -contains $node.Operator.ToString()) }
    return $false
}

# Is this operand, read from the source alone, certainly a string?
function Test-String($node) {
    if ($node -is [System.Management.Automation.Language.StringConstantExpressionAst]) { return $true }
    if ($node -is [System.Management.Automation.Language.ExpandableStringExpressionAst]) { return $true }
    if ($node -is [System.Management.Automation.Language.ConvertExpressionAst]) { return ($node.Type.TypeName.FullName.ToLowerInvariant() -eq 'string') }
    return $false
}

$found = New-Object System.Collections.ArrayList
foreach ($b in $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.BinaryExpressionAst] }, $true)) {
    $op = $b.Operator.ToString()
    if ($op -notmatch '^[IC](eq|ne|lt|le|gt|ge|like|notlike|match|notmatch|replace|contains|notcontains|in|notin|split)$') { continue }
    if (($EQUALITY -contains $op) -and ((Test-NotString $b.Left) -or (Test-NotString $b.Right))) { continue }
    if (($ORDERING -contains $op) -and -not ((Test-String $b.Left) -or (Test-String $b.Right))) { continue }
    $text = $b.Extent.Text -replace '\s+', ' '
    if ($text.Length -gt 110) { $text = $text.Substring(0, 110) + ' ...' }
    [void]$found.Add(('{0,5}:{1,-4} {2,-13} {3}' -f $b.Extent.StartLineNumber, $b.Extent.StartColumnNumber, $op, $text))
}
if ($found.Count -gt 0) {
    $found | ForEach-Object { Write-Host $_ }
    Write-Host "lint-twin: $($found.Count) comparison(s) could be between strings. Use [string]::Equals(a, b, `$ORD) or Str-In, or cast a number."
    exit 1
}
Write-Host "lint-twin: no PowerShell operator compares two strings in $(Split-Path -Leaf $Path)"
exit 0
