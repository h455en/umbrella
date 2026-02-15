# 1. Date Logic
$culture = [System.Globalization.CultureInfo]::GetCultureInfo("fr-FR")
$rawDate = Get-Date
# Force 'fev' instead of 'fév.'
$dateString = $rawDate.ToString("dd_MMM_yyyy", $culture).Replace(".", "").ToLower()
$fileName = "menu_cde_$($dateString).pdf"

# 2. API Config
$apiDate = $rawDate.ToString("yyyy-MM-dd")
$url = "https://infoconso-cde14.salamandre.tm.fr/API/public/v1/Pdf/218/2/2/$($apiDate)/PDF?AffCon=false&AffEta=false&AffGrpEta=false&AffMen=false"

# 3. Pathing - Save EVERYTHING inside 'docs'
$docsPath = "docs"
if (!(Test-Path $docsPath)) { New-Item -ItemType Directory -Path $docsPath }

$pdfPath      = Join-Path $docsPath $fileName
$templatePath = Join-Path $docsPath "template.html"
$htmlPath     = Join-Path $docsPath "cde.html"

try {
    Write-Host "Downloading $fileName..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $url -OutFile $pdfPath -ErrorAction Stop

    # 4. Update HTML
    if (Test-Path $templatePath) {
        $html = Get-Content $templatePath -Raw
        $html = $html.Replace("{{FULL_DATE}}", $rawDate.ToString("dd MMMM yyyy", $culture))
        $html = $html.Replace("{{FILENAME}}", $fileName) # This makes the link "./menu_cde_..."
        $html = $html.Replace("{{TIME}}", $rawDate.ToString("HH:mm"))
        
        $html | Out-File -FilePath $htmlPath -Encoding utf8
        Write-Host "Web page updated." -ForegroundColor Green
    }
}
catch {
    Write-Error "Failed: $($_.Exception.Message)"
    exit 1
}