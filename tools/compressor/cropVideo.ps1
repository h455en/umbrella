# ==============================
# FUNCTIONS
# ==============================

function Invoke-FFmpeg {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    if ($FFMPEG -like "*.exe") {
        $ffmpegExe = $FFMPEG
    }
    else {
        $ffmpegExe = Join-Path $FFMPEG "ffmpeg.exe"
    }

    if (!(Test-Path $ffmpegExe)) {
        throw "ffmpeg.exe not found: $ffmpegExe"
    }

    & $ffmpegExe @Args

    if ($LASTEXITCODE -ne 0) {
        throw "FFmpeg failed (exit code $LASTEXITCODE)"
    }
}

function Crop-Videos {
    param(
        [string]$InputFolder,
        [string]$OutputFolder,
        [int]$L,
        [int]$R,
        [int]$T,
        [int]$B,
        [bool]$RemoveAudio,
        [bool]$Lossless
    )

    if (!(Test-Path $InputFolder)) {
        throw "Input folder not found: $InputFolder"
    }

    New-Item -ItemType Directory -Force -Path $OutputFolder | Out-Null

    # SUPPORT MULTIPLE VIDEO FORMATS
    $files = Get-ChildItem $InputFolder -File | Where-Object {
        $_.Extension -match "\.(mp4|mkv|avi|mov)$"
    }

    Write-Host "Files detected:" $files.Count

    if ($files.Count -eq 0) {
        throw "No video files found in $InputFolder"
    }

    foreach ($file in $files) {

        $in = $file.FullName
        $out = Join-Path $OutputFolder $file.Name

        Write-Host "Processing:" $file.Name

        $vf = "crop=in_w-{0}-{1}:in_h-{2}-{3}:{0}:{2}" -f $L, $R, $T, $B

        # force overwrite with -y
        $args = @("-y", "-i", $in, "-vf", $vf)

        if ($Lossless) {
            $args += @("-c:v", "libx264", "-crf", "0", "-preset", "slow")
        }
        else {
            $args += @("-c:v", "libx264", "-crf", "18", "-preset", "slow")
        }

        if ($RemoveAudio) {
            $args += "-an"
        }
        else {
            $args += @("-c:a", "copy")
        }

        $args += $out

        try {
            Invoke-FFmpeg -Args $args
        }
        catch {
            Write-Host "ERROR processing $($file.Name): $_" -ForegroundColor Red
        }
    }
}

# ===============
# CONFIGURATION
# ===============

$FFMPEG = "C:\Users\hdoghmen\Downloads\d00\ffmpeg_master\bin\ffmpeg.exe"

$inputFolder = "D:\H455N\_PMP_\PMIQ\PMIQ_Part_6\PG\Executing\EXEC"
$outputFolder = "C:\Users\hdoghmen\Downloads\_crop"

$L = 65
$R = 55
$T = 245
$B = 275

$RemoveAudio = $true
$Lossless = $true

# ============
# EXECUTION
# ============

Crop-Videos `
    -InputFolder $inputFolder `
    -OutputFolder $outputFolder `
    -L $L -R $R -T $T -B $B `
    -RemoveAudio $RemoveAudio `
    -Lossless $Lossless