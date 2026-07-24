# Assemble a flat Thought Palette draft.json into an import-ready Library[] JSON.
# Usage: pwsh -File assemble.ps1 <draft.json> [output.json]   (default: import.json beside draft)
# PowerShell fallback for assemble.py; must produce identical output. See SCHEMA.md.
param(
  [Parameter(Mandatory = $true)][string]$DraftPath,
  [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$PROTECTED = @('未分類', '通用')
$HEX_RE = '^#[0-9A-Fa-f]{6}$'
$SLUG_RE = '^[a-z0-9-]+$'
if (-not $OutputPath) { $OutputPath = Join-Path (Split-Path -Parent $DraftPath) 'import.json' }

function Test-Num($v) { $v -is [int] -or $v -is [long] -or $v -is [double] -or $v -is [decimal] }
function Prop($obj, $name, $default) {
  if ($null -ne $obj -and $obj.PSObject.Properties[$name]) { return $obj.$name }
  return $default
}

$draft = Get-Content -Raw -Path $DraftPath -Encoding UTF8 | ConvertFrom-Json
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

$library = Prop $draft 'library' 'Analysis'; if (-not $library) { $library = 'Analysis' }
$elements = @(Prop $draft 'elements' @())
$palettes = @(Prop $draft 'palettes' @())

$eleById = [ordered]@{}
for ($i = 0; $i -lt $elements.Count; $i++) {
  $e = $elements[$i]; $eid = Prop $e 'id' $null
  if (-not $eid) { $errors.Add("elements[$i] missing id"); continue }
  if ($eleById.Contains($eid)) { $errors.Add("duplicate element id '$eid'") }
  if ($eid -notmatch $SLUG_RE) { $warnings.Add("element id '$eid' is not a latin slug [a-z0-9-]") }
  if (-not (Prop $e 'text' $null)) { $warnings.Add("element '$eid' has empty text") }
  if (-not (Prop $e 'storage_cat' $null)) { $warnings.Add("element '$eid' has no storage_cat; filed under 未分類") }
  $eleById[$eid] = $e
}

$referenced = [System.Collections.Generic.HashSet[string]]::new()

$order = [System.Collections.Generic.List[string]]::new(); $PROTECTED | ForEach-Object { $order.Add($_) }
$buckets = @{}; foreach ($n in $PROTECTED) { $buckets[$n] = [System.Collections.Generic.List[object]]::new() }
foreach ($e in $elements) {
  $eid = Prop $e 'id' $null; if (-not $eid) { continue }
  $cat = Prop $e 'storage_cat' '未分類'; if (-not $cat) { $cat = '未分類' }
  if (-not $buckets.ContainsKey($cat)) { $buckets[$cat] = [System.Collections.Generic.List[object]]::new(); $order.Add($cat) }
  $buckets[$cat].Add([ordered]@{ ele_id = $eid; text = (Prop $e 'text' '') })
}
$storageElement = [System.Collections.Generic.List[object]]::new()
for ($i = 0; $i -lt $order.Count; $i++) {
  $name = $order[$i]
  $storageElement.Add([ordered]@{ cat_id = "scat-$($i + 1)"; cat_name = $name; cat_ele = @($buckets[$name]) })
}

$paletas = [System.Collections.Generic.List[object]]::new()
for ($pi = 0; $pi -lt $palettes.Count; $pi++) {
  $p = $palettes[$pi]
  $pname = Prop $p 'name' "Palette $($pi + 1)"; if (-not $pname) { $pname = "Palette $($pi + 1)" }
  $uCat = [ordered]@{ cat_id = "pcat-$($pi + 1)-u"; cat_name = '未分類'; cat_base = 0; cat_factor = 1; cat_ele = [System.Collections.Generic.List[object]]::new() }
  $gCat = [ordered]@{ cat_id = "pcat-$($pi + 1)-g"; cat_name = '通用'; cat_base = 0; cat_factor = 1; cat_color = '#FFFFFF'; cat_ele = [System.Collections.Generic.List[object]]::new() }
  $protectedTargets = @{ '未分類' = $uCat; '通用' = $gCat }
  $outCats = [System.Collections.Generic.List[object]]::new(); $outCats.Add($uCat); $outCats.Add($gCat)
  $seenInPalette = [System.Collections.Generic.HashSet[string]]::new()

  $cats = @(Prop $p 'cats' @())
  for ($ci = 0; $ci -lt $cats.Count; $ci++) {
    $c = $cats[$ci]
    $cname = Prop $c 'name' "cat $($ci + 1)"; if (-not $cname) { $cname = "cat $($ci + 1)" }
    $base = Prop $c 'base' 0; $factor = Prop $c 'factor' 1
    if (-not (Test-Num $base)) { $errors.Add("palette '$pname' cat '$cname' base is not numeric"); $base = 0 }
    if (-not (Test-Num $factor)) { $errors.Add("palette '$pname' cat '$cname' factor is not numeric"); $factor = 1 }
    if ((Test-Num $base) -and $base -lt 0) { $warnings.Add("palette '$pname' cat '$cname' has negative base ($base)") }

    $refs = [System.Collections.Generic.List[object]]::new()
    foreach ($pl in @(Prop $c 'elements' @())) {
      $ele = Prop $pl 'ele' $null
      if (-not $eleById.Contains($ele)) { $errors.Add("palette '$pname' cat '$cname' references unknown element '$ele'"); continue }
      if ($seenInPalette.Contains($ele)) { $errors.Add("palette '$pname' references element '$ele' more than once"); continue }
      [void]$seenInPalette.Add($ele); [void]$referenced.Add($ele)
      $val = Prop $pl 'val' 0
      if (-not (Test-Num $val)) { $errors.Add("palette '$pname' cat '$cname' element '$ele' val is not numeric"); $val = 0 }
      elseif ($val -lt -5 -or $val -gt 5) { $warnings.Add("palette '$pname' cat '$cname' element '$ele' val $val outside -5..+5") }
      $refs.Add([ordered]@{ ele_id = $ele; val = $val; index = $refs.Count })
    }

    $color = Prop $c 'color' $null
    if ($null -ne $color -and $color -notmatch $HEX_RE) { $errors.Add("palette '$pname' cat '$cname' color '$color' is not #RRGGBB"); $color = $null }

    if ($protectedTargets.ContainsKey($cname)) {
      $target = $protectedTargets[$cname]
      $target.cat_base = $base; $target.cat_factor = $factor
      if ($cname -eq '未分類' -and $color) { $target.cat_color = $color }
      foreach ($r in $refs) { $r.index = $target.cat_ele.Count; $target.cat_ele.Add($r) }
      continue
    }

    $cat = [ordered]@{ cat_id = "pcat-$($pi + 1)-$($ci + 1)"; cat_name = $cname; cat_base = $base; cat_factor = $factor; cat_ele = @($refs) }
    if ($color) { $cat.cat_color = $color }
    $outCats.Add($cat)
  }

  if ($gCat.cat_ele.Count -eq 0) { $warnings.Add("palette '$pname' has an empty 通用 cat; consider cross-cutting elements (documentation health, conventions, DX)") }

  $named = @($outCats | Where-Object { $PROTECTED -notcontains $_.cat_name })
  if ($named.Count -gt 21) { $errors.Add("palette '$pname' has $($named.Count) named cats (max 21)") }
  elseif ($named.Count -gt 11) { $warnings.Add("palette '$pname' has $($named.Count) named cats (>11 may fatigue the user)") }

  $metadata = [ordered]@{}
  $md = Prop $p 'metadata' $null
  if ($md) { foreach ($prop in $md.PSObject.Properties) { $metadata[$prop.Name] = $prop.Value } }
  $kind = Prop $p 'kind' $null; if ($kind) { $metadata['kind'] = $kind }
  $groups = [ordered]@{}
  foreach ($c in $cats) { $g = Prop $c 'group' $null; if ($g) { $groups[(Prop $c 'name' '')] = $g } }
  if ($groups.Count -gt 0 -and -not $metadata.Contains('cat_groups')) { $metadata['cat_groups'] = $groups }

  # normalize cat_ele lists to arrays for JSON
  foreach ($c in $outCats) { $c.cat_ele = @($c.cat_ele) }
  $paletas.Add([ordered]@{ pal_id = "pal-$($pi + 1)"; pal_name = $pname; metadata = $metadata; cats = @($outCats) })
}

foreach ($eid in $eleById.Keys) { if (-not $referenced.Contains($eid)) { $warnings.Add("element '$eid' is not referenced by any palette") } }

$lib = [ordered]@{ storage_id = 'lib-1'; storage_name = $library; storage_element = @($storageElement); paletas = @($paletas) }

# --- report ---
Write-Host '=== Thought Palette assembly ==='
Write-Host "library: $library"
$eleCount = ($storageElement | ForEach-Object { $_.cat_ele.Count } | Measure-Object -Sum).Sum
Write-Host "storage cats: $($storageElement.Count), elements: $eleCount"
foreach ($p in $paletas) {
  $named = @($p.cats | Where-Object { $PROTECTED -notcontains $_.cat_name })
  $refCount = ($p.cats | ForEach-Object { $_.cat_ele.Count } | Measure-Object -Sum).Sum
  $k = if ($p.metadata.Contains('kind')) { $p.metadata['kind'] } else { '-' }
  Write-Host "palette '$($p.pal_name)' ($k): $($named.Count) named cats, $refCount refs"
}
if ($warnings.Count) { Write-Host "`n$($warnings.Count) WARNING(s):"; $warnings | ForEach-Object { Write-Host "  ! $_" } }
if ($errors.Count) { Write-Host "`n$($errors.Count) ERROR(s):"; $errors | ForEach-Object { Write-Host "  x $_" } }
if (-not $errors.Count -and -not $warnings.Count) { Write-Host 'no issues.' }

if ($errors.Count) { Write-Error "`nNOT written: resolve $($errors.Count) error(s) first."; exit 1 }
# -AsArray forces a top-level JSON array; feed the single $lib so it wraps to [ {lib} ]
# (feeding the already-array $output would double-wrap into [[lib]])
$json = ConvertTo-Json -InputObject $lib -Depth 100 -AsArray
[System.IO.File]::WriteAllText($OutputPath, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "`nWrote $OutputPath"
