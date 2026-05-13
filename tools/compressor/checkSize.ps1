function Export-FileSizeHtml {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,
       
        [Parameter(Mandatory = $false)]
        [int]$MinSizeMB = 0,
        [Parameter(Mandatory = $false)]
        [string]$OutputFile = "FileReport.html"
    )

    if (Test-Path $Path) {
        Write-Host "Scanning $Path (Min Size: $MinSizeMB MB)..." -ForegroundColor Cyan
        
        $minSizeBytes = $MinSizeMB * 1MB

        $files = Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -ge $minSizeBytes } |
        Sort-Object Length -Descending

        $totalSizeBytes = ($files | Measure-Object -Property Length -Sum).Sum
        $totalReadable = Get-HumanReadableSize $totalSizeBytes
        $fileCount = $files.Count

        # Build HTML Table Rows
        $rows = foreach ($file in $files) {
            $readableSize = Get-HumanReadableSize $file.Length
            $badgeHtml = Get-SizeBadge $file.Length

            $folderPath = $file.DirectoryName
            $unixPath = $folderPath.Replace("\", "/")

            "<tr>
                <td class='text-right'>$($file.Name)</td>
                <td>$badgeHtml</td>
                <td>
                    <a href='file:///$unixPath' target='_blank'>$folderPath</a>
                    <button class='button small secondary copy-btn ml-2' data-path='$unixPath'>
                        Copy
                    </button>
                </td>
            </tr>"
        }

        $htmlHeader = @"
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/foundation-sites@6.8.1/dist/css/foundation.min.css'>
    <title>File Size Report</title>
    <style>
        body { padding: 20px; background-color: #f5f5f5; }
        .header {
            background: #212529;
            color: white;
            padding: 15px 20px;
            border-radius: 4px 4px 0 0;
        }
        .label {
            font-size: 0.9rem;
            font-weight: 600;
            padding: 6px 12px;
            margin: 0;
        }
        table td, table th { vertical-align: middle; }
        .text-right { text-align: right; }
        .controls { background: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
        .copy-btn { font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class='grid-container'>
        <div class='header'>
            <h5 class='margin-bottom-0'>File Inventory: $Path</h5>
            <p class='margin-bottom-0'>
                $fileCount files &nbsp; • &nbsp; Total Size: <strong>$totalReadable</strong>
            </p>
        </div>

        <div class='controls'>
            <div class='grid-x grid-margin-x'>
                <div class='cell medium-5'>
                    <input type='text' id='searchInput' class='input' placeholder='Search by file name...'>
                </div>
                <div class='cell medium-4'>
                    <label>Minimum Size: <span id='sizeValue' class='label secondary'>0</span> MB</label>
                    <input type='range' id='sizeSlider' min='0' max='5000' value='$MinSizeMB' step='10' style='width:100%'>
                </div>
                <div class='cell medium-3'>
                    <button class='button' onclick='resetFilters()'>Reset Filters</button>
                </div>
            </div>
        </div>

        <table class='table' id='fileTable'>
            <thead>
                <tr>
                    <th class='text-right'>File Name</th>
                    <th>Size</th>
                    <th>Folder (Click to Open)</th>
                </tr>
            </thead>
            <tbody>
"@
        $htmlFooter = @"
            </tbody>
        </table>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const sizeSlider = document.getElementById('sizeSlider');
        const sizeValue = document.getElementById('sizeValue');
        const table = document.getElementById('fileTable');

        function filterTable() {
            const searchText = searchInput.value.toLowerCase();
            const minMb = parseInt(sizeSlider.value) || 0;
            sizeValue.textContent = minMb;

            Array.from(table.getElementsByTagName('tr')).forEach(row => {
                if (row.cells.length < 2) return;

                const fileName = row.cells[0].textContent.toLowerCase();
                const sizeText = row.cells[1].textContent;
                const sizeMb = parseFloat(sizeText) || 0;

                const matchesSearch = fileName.includes(searchText);
                const matchesSize = sizeMb >= minMb;

                row.style.display = (matchesSearch && matchesSize) ? '' : 'none';
            });
        }

        searchInput.addEventListener('input', filterTable);
        sizeSlider.addEventListener('input', filterTable);

        function resetFilters() {
            searchInput.value = '';
            sizeSlider.value = 0;
            filterTable();
        }

        // Copy button with feedback
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const path = btn.getAttribute('data-path');
                navigator.clipboard.writeText(path).then(() => {
                    const original = btn.textContent;
                    btn.textContent = 'Copied!';
                    btn.classList.add('success');
                    setTimeout(() => {
                        btn.textContent = original;
                        btn.classList.remove('success');
                    }, 1600);
                });
            });
        });
    </script>
</body>
</html>
"@

        $finalHtml = $htmlHeader + ($rows -join "`n") + $htmlFooter
        $finalHtml | Out-File -FilePath $OutputFile -Encoding utf8
       
        Write-Host "Report generated successfully: $OutputFile" -ForegroundColor Green
        Invoke-Item $OutputFile
    }
    else {
        Write-Warning "Path not found: $Path"
    }
}

# ============_Helper Functions_=========

function Get-HumanReadableSize {
    param([long]$Bytes)
    if ($Bytes -ge 1TB) { return "{0:N0} TB" -f ($Bytes / 1TB) }
    if ($Bytes -ge 1GB) { return "{0:N0} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N0} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N0} KB" -f ($Bytes / 1KB) }
    return "$Bytes Bytes"
}

function Get-SizeBadge {
    param([long]$Bytes)
    
    $mb = $Bytes / 1MB

    $colorClass = switch ($true) {
        ($mb -lt 200) { "success" }
        ($mb -lt 400) { "info" }
        ($mb -lt 700) { "primary" }
        ($mb -lt 1200) { "warning" }
        ($mb -lt 2000) { "orange" }
        default { "alert" }
    }

    $sizeText = Get-HumanReadableSize $Bytes
    return "<span class='label $colorClass rounded'>$sizeText</span>"
}

# ___________________Call______________________________
$report = "C:\Users\h455n\Downloads\_PS\MyLargeFiles.html"


$folder = "F:\_WAY"
$folder = "F:\PROGRAM_FILES\tmp\zamp"
$folder = "C:\Users\h455n\Downloads\_PIPELINE"

$size = 5

Export-FileSizeHtml -Path $folder -MinSizeMB $size -OutputFile $report
