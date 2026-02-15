# 1. Date and Culture setup
$culture = [System.Globalization.CultureInfo]::GetCultureInfo("fr-FR")
$rawDate = Get-Date

# 2. Get the short month (févr.), remove the dot, and take only the first 3 letters (fev)
$month = $rawDate.ToString("MMM", $culture).Replace(".", "").ToLower()

# 3. Remove Accents (turns 'fév' into 'fev')
$normalized = $month.Normalize([System.Text.NormalizationForm]::FormD)
$monthSafe = ($normalized.ToCharArray() | Where-Object { 
    [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($_) -ne [System.Globalization.UnicodeCategory]::NonSpacingMark 
}) -join ""

# 4. Final Filename Construction (e.g., menu_cde_15_fev_2026.pdf)
$dateString = "$($rawDate.ToString('dd'))_$($monthSafe.Substring(0,3))_$($rawDate.Year)"
$fileName = "menu_cde_$($dateString).pdf"

# --- Rest of your script logic ---
$apiDate = $rawDate.ToString("yyyy-MM-dd")
$url = "https://infoconso-cde14.salamandre.tm.fr/API/public/v1/Pdf/218/2/2/$($apiDate)/PDF?AffCon=false&AffEta=false&AffGrpEta=false&AffMen=false"
$docsPath = "docs"
$pdfPath = Join-Path $docsPath $fileName

try {
    Write-Host "Downloading to: $pdfPath" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $url -OutFile $pdfPath -ErrorAction Stop
    
    # Update HTML Template
    $templatePath = "docs/template.html"
    $htmlPath = "docs/cde.html"
    if (Test-Path $templatePath) {
        $html = Get-Content $templatePath -Raw
        $html = $html.Replace("{{FILENAME}}", $fileName)
        $html = $html.Replace("{{FULL_DATE}}", $rawDate.ToString("dd MMMM yyyy", $culture))
        $html = $html.Replace("{{TIME}}", $rawDate.ToString("HH:mm"))
        $html | Out-File -FilePath $htmlPath -Encoding utf8
    }
    
    # Export for GitHub Workflow
    if ($env:GITHUB_ENV) { "ARTIFACT_NAME=$($fileName.Replace('.pdf', ''))" | Out-File -FilePath $env:GITHUB_ENV -Append }
}
catch { exit 1 }