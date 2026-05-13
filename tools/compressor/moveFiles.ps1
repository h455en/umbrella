# =============================================================================
# Move-FilesByExtension.ps1
# Clearly moves (cuts) files - Recursive by default
# =============================================================================

function Normalize-Extensions {
    param([Parameter(Mandatory=$true)] $Extensions)
    
    $normalized = @()
    if ($Extensions -is [string]) { $Extensions = @($Extensions) }
    
    foreach ($ext in $Extensions) {
        $ext = $ext.Trim()
        if (-not $ext.StartsWith('.')) { $ext = ".$ext" }
        $normalized += $ext.ToLower()
    }
    return $normalized
}

function Move-FilesByExtension {
    [CmdletBinding()]
    param(
        [string]$SourceDir = ".",
        [string]$TargetDir = "TARGET",
        [Parameter(Mandatory=$true)]
        $Extensions = @(".heic", ".mp3", ".mp4", ".pdf"),
        [switch]$Recursive = $true,
        [switch]$GroupByExtension,
        [switch]$DryRun
    )

    $SourcePath = Resolve-Path $SourceDir -ErrorAction Stop
    $TargetPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($TargetDir)

    # Create target folder
    if (-not (Test-Path $TargetPath)) {
        New-Item -Path $TargetPath -ItemType Directory -Force | Out-Null
        Write-Host "Created target folder: $TargetDir" -ForegroundColor Cyan
    }

    $extList = Normalize-Extensions $Extensions
    Write-Host "Searching for extensions: $($extList -join ', ')" -ForegroundColor Yellow

    # Get files
    $files = Get-ChildItem -Path $SourcePath -File -Recurse:$Recursive
    
    $movedCount = 0
    $foundCount = 0

    foreach ($file in $files) {
        if ($file.Extension.ToLower() -notin $extList) {
            continue
        }

        $foundCount++
        
        # Destination setup
        if ($GroupByExtension) {
            $subFolder = Join-Path $TargetPath ($file.Extension.TrimStart('.').ToLower())
            if (-not (Test-Path $subFolder)) {
                New-Item -Path $subFolder -ItemType Directory -Force | Out-Null
            }
            $DestFolder = $subFolder
        } else {
            $DestFolder = $TargetPath
        }

        $DestFile = Join-Path $DestFolder $file.Name

        # Avoid overwriting - add number if file exists
        $counter = 1
        $originalName = $file.Name
        while (Test-Path $DestFile) {
            $base = [IO.Path]::GetFileNameWithoutExtension($originalName)
            $DestFile = Join-Path $DestFolder "$base`_$counter$($file.Extension)"
            $counter++
        }

        if ($DryRun) {
            Write-Host "[DRY RUN] Would move: $($file.FullName)" -ForegroundColor DarkYellow
        } else {
            try {
                Move-Item -Path $file.FullName -Destination $DestFile -Force -ErrorAction Stop
                Write-Host "Moved: $($file.Name)" -ForegroundColor Green
                $movedCount++
            }
            catch {
                Write-Host "Failed to move $($file.Name): $_" -ForegroundColor Red
            }
        }
    }

    # Summary
    Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
    Write-Host "Files found matching extensions : $foundCount" -ForegroundColor Yellow
    Write-Host "Files moved                    : $movedCount" -ForegroundColor Green
    Write-Host "Target folder                  : $TargetPath" -ForegroundColor Cyan

    if ($foundCount -eq 0) {
        Write-Host "`nNo files with the specified extensions were found." -ForegroundColor Red
        Write-Host "Check the extensions list and make sure files exist in the folder (or subfolders)." -ForegroundColor Red
    }
}


# ========================= EXAMPLE USAGE =========================

$IN = "C:\Users\h455n\Downloads\_PIPELINE\IN\Phone\2025"
$TARGET = "C:\Users\h455n\Downloads\_PIPELINE\IN\Phone\_MP3"
$EXTENSIONS = @(".mp3") # "".heic", ".mp3", ".mp4", ".pdf")

# Example 1: Basic usage (Recommended)
Move-FilesByExtension `
    -SourceDir $IN   `
    -TargetDir $TARGET   `
    -Extensions $EXTENSIONS   `
    -Recursive:$true   `
    -GroupByExtension:$false  `

# Example 2: Advanced usage (uncomment to use)
<#
Move-FilesByExtension `
    -SourceDir "C:\Users\YourName\Downloads" `
    -TargetDir "C:\Users\YourName\SortedMedia" `
    -Extensions @(".heic",".jpg",".png",".mp4",".mov") `
    -Recursive `
    -GroupByExtension `
    -DryRun
#>