# verify_exports.ps1  (v3)
#
# Structural verification of the sensitivity JSON exports produced by the
# n8n pipeline. Requires nothing beyond Windows PowerShell.
#
#     powershell -ExecutionPolicy Bypass -File .\verify_exports.ps1
#
# Optional: point it at a different root
#     powershell -ExecutionPolicy Bypass -File .\verify_exports.ps1 "C:\path\to\root"

param([string]$Root = ".")

$BaselineN = @{
    "IFC4-Building-Architecture"  = 14
    "IFC43-Building-Architecture" = 14
    "IFC4-Building-Structural"    = 16
    "IFC43-Building-Structural"   = 16
    "IFC4-Infra-Bridge"           = 57
    "IFC43-Infra-Bridge"          = 68
    "IFC4-Infra-Road"             = 55
    "IFC43-Infra-Road"            = 81
}

$Keys = @("score_completeness", "score_validity",
          "score_qto_coverage", "score_qto_agreement")

$files = Get-ChildItem -Path $Root -Filter "sensitivity-*.json" -Recurse -File
if ($files.Count -eq 0) {
    Write-Host "No sensitivity-*.json found under $((Resolve-Path $Root).Path)"
    exit 1
}

$failures  = @()
$folders   = @{}
$f6Reduced = 0
$f6Total   = 0
$shownKeys = $false

foreach ($f in $files) {

    $folder = $f.Directory.Name
    if ($folders.ContainsKey($folder)) { $folders[$folder]++ } else { $folders[$folder] = 1 }

    # longest matching model name, so IFC43-... is not matched as IFC4-...
    $model = $null
    foreach ($m in $BaselineN.Keys) {
        if ($f.Name -like "*$m*") {
            if (($null -eq $model) -or ($m.Length -gt $model.Length)) { $model = $m }
        }
    }
    if ($null -eq $model) {
        $failures += "$($f.Name)  ->  model not recognised from filename"
        continue
    }

    $expected = $BaselineN[$model]
    $isF6 = $f.Name.ToUpper().Contains("F6")
    if ($isF6) { $f6Total++ }

    try {
        $raw    = Get-Content -LiteralPath $f.FullName -Raw
        $parsed = ConvertFrom-Json -InputObject $raw
        # PowerShell 5.1 returns a JSON array as a single object; unwrap it
        if ($parsed -is [array]) { $data = $parsed } else { $data = @($parsed) }
        if (($data.Count -eq 1) -and ($data[0] -is [array])) { $data = $data[0] }
    } catch {
        $failures += "$($f.Name)  ->  unreadable JSON"
        continue
    }

    $n = $data.Count
    if ($n -eq 0) { $failures += "$($f.Name)  ->  empty export"; continue }

    $first = $data[0]

    # show the property names once, so a schema change is immediately visible
    if (-not $shownKeys) {
        $names = @($first.PSObject.Properties | ForEach-Object { $_.Name })
        Write-Host "Fields found in $($f.Name):"
        Write-Host ("  " + ($names -join ", "))
        Write-Host ""
        $shownKeys = $true
    }

    # GlobalId present and unique
    $gids = @($data | ForEach-Object { $_.GlobalId })
    if ($gids -contains $null) { $failures += "$($f.Name)  ->  record without GlobalId"; continue }
    $dup = $n - (@($gids | Select-Object -Unique)).Count
    if ($dup -gt 0) { $failures += "$($f.Name)  ->  $dup duplicated GlobalId"; continue }

    # all four dimension scores present on the first record
    $names   = @($first.PSObject.Properties | ForEach-Object { $_.Name })
    $missing = @($Keys | Where-Object { $names -notcontains $_ })
    if ($missing.Count -gt 0) {
        $failures += "$($f.Name)  ->  missing keys: $($missing -join ', ')"
        continue
    }

    # element count
    if ($isF6) {
        if ($n -gt $expected) {
            $failures += "$($f.Name)  ->  F6 run has MORE elements ($n) than baseline ($expected)"
        } elseif ($n -lt $expected) {
            $f6Reduced++
        }
    } elseif ($n -ne $expected) {
        $failures += "$($f.Name)  ->  element count $n, expected $expected"
    }
}

Write-Host "Scanned $($files.Count) export(s) under $((Resolve-Path $Root).Path)"
Write-Host ""
Write-Host "Files per folder:"
foreach ($k in ($folders.Keys | Sort-Object)) {
    Write-Host ("  {0,4}  {1}" -f $folders[$k], $k)
}
Write-Host ""
Write-Host "$f6Reduced of $f6Total F6 run(s) show a reduced element count, as expected by design."

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "$($failures.Count) file(s) FAILED. First 15:" -ForegroundColor Red
    $failures | Select-Object -First 15 | ForEach-Object { Write-Host "  $_" }
    exit 1
}

Write-Host ""
Write-Host "All $($files.Count) files passed: valid JSON, no duplicated GlobalId," -ForegroundColor Green
Write-Host "all four dimension scores present, element counts as expected." -ForegroundColor Green
exit 0
