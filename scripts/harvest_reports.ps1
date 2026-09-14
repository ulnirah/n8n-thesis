# harvest_reports.ps1
#
# Reads every risk-register HTML report under the given root and writes one
# CSV row per run: model, fault, rate, configuration, BQI, element coverage,
# coverage verdict, high/medium counts, elements scored, avg SRCC, verdict.
#
#     powershell -ExecutionPolicy Bypass -File .\harvest_reports.ps1
#
# Output: report_summary.csv in the current folder. Open it in Excel.

param([string]$Root = ".", [string]$Out = "report_summary.csv")

$files = Get-ChildItem -Path $Root -Filter "risk-register-*.html" -Recurse -File
if ($files.Count -eq 0) { Write-Host "No risk-register-*.html found."; exit 1 }

$rows = @()

foreach ($f in $files) {

    $t = Get-Content -LiteralPath $f.FullName -Raw

    # KPI tiles: value / label pairs, in document order
    $vals = [regex]::Matches($t, 'class="kpi-value">([^<]*)</div>') | ForEach-Object { $_.Groups[1].Value.Trim() }
    $labs = [regex]::Matches($t, 'class="kpi-label">([^<]*)</div>') | ForEach-Object { $_.Groups[1].Value.Trim() }
    $subs = [regex]::Matches($t, 'class="kpi-sub"[^>]*>([^<]*)</div>') | ForEach-Object {
                $_.Groups[1].Value -replace '&nbsp;|&middot;', ' ' -replace '\s+', ' ' }

    $kpi = @{}
    for ($k = 0; $k -lt [Math]::Min($vals.Count, $labs.Count); $k++) { $kpi[$labs[$k]] = $vals[$k] }

    # avg SRCC sits in a kpi-sub, e.g. "avg SRCC: 1"
    $srcc = ""
    $m = [regex]::Match($t, 'avg SRCC:\s*([^<]+)')
    if ($m.Success) { $srcc = $m.Groups[1].Value.Trim() }

    # coverage verdict word from the sub-line under Element Coverage
    $covV = ""
    $m = [regex]::Match(($subs -join ' | '), '\b(PASS|REVIEW|FAIL)\b')
    if ($m.Success) { $covV = $m.Groups[1].Value }

    # screening verdict
    $verdict = ""
    $m = [regex]::Match($t, '(DATA UNRELIABLE|USE WITH CAUTION|RELIABLE)')
    if ($m.Success) { $verdict = $m.Groups[1].Value }

    # parse model / fault / rate / configuration out of the filename
    $name = $f.BaseName
    $model = ""
    foreach ($mm in @("IFC43-Building-Architecture","IFC4-Building-Architecture",
                      "IFC43-Building-Structural","IFC4-Building-Structural",
                      "IFC43-Infra-Bridge","IFC4-Infra-Bridge",
                      "IFC43-Infra-Road","IFC4-Infra-Road")) {
        if ($name -like "*$mm*") { if ($mm.Length -gt $model.Length) { $model = $mm } }
    }
    $fault = "baseline"; $rate = ""
    $m = [regex]::Match($name, '__(F\d)-r(\d+)')
    if ($m.Success) { $fault = $m.Groups[1].Value; $rate = $m.Groups[2].Value + "%" }
    $config = if ($name -match "DUALFILE") { "dual-file" }
              elseif ($fault -eq "baseline") { "-" } else { "single-file" }

    $rows += [pscustomobject]@{
        File             = $f.Name
        Folder           = $f.Directory.Name
        Model            = $model
        Fault            = $fault
        Rate             = $rate
        Config           = $config
        BQI              = $kpi["Model BQI Score"]
        ElementCoverage  = $kpi["Element Coverage"]
        CoverageVerdict  = $covV
        HighRisk         = $kpi["High-Risk Elements"]
        MediumRisk       = $kpi["Medium-Risk Elements"]
        ElementsScored   = $kpi["Elements Scored"]
        AvgSRCC          = $srcc
        Verdict          = $verdict
    }
}

$rows | Sort-Object Model, Fault, Config, Rate |
        Export-Csv -Path $Out -NoTypeInformation -Encoding UTF8

Write-Host "Wrote $($rows.Count) row(s) to $Out"
Write-Host ""
Write-Host "Quick check, avg SRCC by fault and configuration:"
$rows | Where-Object { $_.Fault -ne "baseline" } |
    Group-Object Fault, Config |
    ForEach-Object { Write-Host ("  {0,-22} {1,3} run(s)" -f $_.Name, $_.Count) }
