

function Convert-Audio {
    # Force the session to use UTF8 for everything
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    Add-Type -AssemblyName System.Windows.Forms
    $FolderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $FolderBrowser.Description = "Select the folder containing Arabic audio files"
    
    if ($FolderBrowser.ShowDialog() -ne "OK") {
        Write-Host "No folder selected. Exiting." -ForegroundColor Red
        return
    }

    $IN = $FolderBrowser.SelectedPath
    $FFMPEG = "C:\Users\h455n\Downloads\_PIPELINE\FFMPEG\bin\ffmpeg.exe"
    $Extensions = @("*.mp4","*.mp3","*.m4a", "*.wav","*.aac","*.mpeg","*.mkv")

    if (!(Test-Path -LiteralPath $FFMPEG)) {
        Write-Host "FFmpeg not found at: $FFMPEG" -ForegroundColor Red
        return
    }

    # Use -LiteralPath to prevent Arabic characters from being treated as wildcards
    # Exclude any existing "RESIZED" folders
    $files = Get-ChildItem -LiteralPath $IN -Recurse -Include $Extensions | 
             Where-Object { $_.FullName -notmatch "RESIZED" }
    
    $total = $files.Count
    if ($total -eq 0) {
        Write-Host "No files found in: $IN" -ForegroundColor Yellow
        return
    }

    $index = 0
    foreach ($file in $files) {
        $index++

        # Create local RESIZED folder
        $outDir = Join-Path -Path $file.DirectoryName -ChildPath "RESIZED"
        if (!(Test-Path -LiteralPath $outDir)) {
            New-Item -ItemType Directory -Path $outDir -Force | Out-Null
        }

        $outputFile = Join-Path -Path $outDir -ChildPath "$($file.BaseName)_.mp3"

        Write-Progress -Activity "Processing Audio" -Status "File $index of $total" -PercentComplete (($index/$total)*100)
        Write-Host "[$index/$total] Processing: $($file.Name)" -ForegroundColor Cyan

        # --- The Secret Sauce for Spaces and Arabic ---
        # We pass arguments as an array so PowerShell doesn't misinterpret spaces
        $ffmpegArgs = @(
            "-y",
            "-i", $file.FullName,         # Input path
            "-ac", "1",                   # Mono
            "-ar", "8000",                # 8kHz
            "-c:a", "libmp3lame",         # MP3 Codec
            "-b:a", "8k",                 # 8kbps
            "-hide_banner",
            "-loglevel", "error",
            $outputFile                   # Output path
        )

        # Execute using the & operator with the array
        & $FFMPEG @ffmpegArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   -> Success" -ForegroundColor Green
        } else {
            Write-Host "   -> FAILED: $($file.Name)" -ForegroundColor Red
        }
    }

    Write-Host "`nConversion Complete!" -ForegroundColor Yellow
}

# --- Execution ---
$in = "F:\_WAY\SAID\a9ida_salaf"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\BIN_HADI"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\FIFI"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\RABEE"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\conf_5"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\MOSNAD"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\TILIMSANI"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\MANHAJ"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\TAFSIR"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\LOM3A"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\BIN_HADI_2"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\KALIMAT_AL_SHEIKH"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\HILYA"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\CONF_7"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\CHARH_HADITH_BIN_HADI"
$in = "C:\Users\h455n\Downloads\_PIPELINE\IN\AUD\HAMAWIYYA"

$in = "F:\_WAY\دروس\سليمان الرحيلي\فقة المعاملات المالية المعاصرة 3"

$prefix = ""
$suffix = "_"
Convert-Audio `
    -IN $in `
    -Prefix $prefix `
    -Suffix $suffix
