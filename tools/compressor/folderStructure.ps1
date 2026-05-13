# ================================================
# Video Tree Scanner + HTML Report - v9.1 (Fixed)
# ================================================

param(
    [string]$RootPath = ".",
    [string]$OutputHtml = "MyVideos.html",
    [int]$MaxFiles = 3
)

# Video extensions
$VideoExtensions = @(".mp4",".mkv",".avi",".mov",".wmv",".flv",".webm",".m4v",".mpg",".mpeg",".3gp",".ts",".m2ts",".vob",".rmvb")

Write-Host "Scanning for videos in: $RootPath" -ForegroundColor Cyan

$Videos = Get-ChildItem -Path $RootPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $VideoExtensions -contains $_.Extension.ToLower() }

$totalVideos = $Videos.Count
Write-Host "Found $totalVideos video files" -ForegroundColor Green

# ==================== Build Tree ====================
function Build-VideoTree {
    param($VideoFiles, $Root)
    $tree = @{ _files = [System.Collections.ArrayList]::new(); _sub = @{} }
    foreach ($file in $VideoFiles) {
        $relPath = $file.DirectoryName.Substring($Root.Length).TrimStart('\', '/')
        $parts = if ($relPath) { $relPath -split '\\' } else { @() }
        $current = $tree
        foreach ($part in $parts) {
            if (-not $current._sub.ContainsKey($part)) {
                $current._sub[$part] = @{ _files = [System.Collections.ArrayList]::new(); _sub = @{} }
            }
            $current = $current._sub[$part]
        }
        [void]$current._files.Add($file)
    }
    $tree
}

$FolderTree = Build-VideoTree $Videos $RootPath

# ==================== HTML Generation ====================
$htmlHeader = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Library Tree</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Roboto', system-ui, sans-serif; }
        .file { transition: all 0.2s; }
        .file:hover { background-color: #1f2937 !important; }
        .file:nth-child(odd)  { background-color: #0f172a; }
        .file:nth-child(even) { background-color: #1e2937; }
        .file + .file { border-top: 1px solid #334155; }
    </style>
</head>
<body class="bg-slate-950 text-slate-200">

    <!-- Thin Header -->
    <header class="bg-slate-900 border-b border-slate-700 py-3 text-center text-sm font-medium text-slate-400">
        Video Library Tree • $RootPath
    </header>

    <div class="max-w-5xl mx-auto p-6">
        
        <!-- Stats -->
        <div class="bg-slate-900 rounded-3xl shadow-2xl border border-slate-700 p-6 mb-10 flex items-center justify-between">
            <div>
                <p class="text-slate-400 text-sm mb-1">Total Videos</p>
                <p class="text-5xl font-semibold text-emerald-400">$totalVideos</p>
            </div>
            <div class="text-right">
                <p class="text-slate-500 text-xs">Root Folder</p>
                <p class="font-mono text-sm text-slate-400">$RootPath</p>
            </div>
        </div>

        <div class="tree space-y-4 bg-slate-900 rounded-3xl shadow-2xl border border-slate-700 p-6">
"@

function Get-CountPill {
    param([int]$Count)
    if ($Count -le 3) {
        return "<span class='inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'>$Count</span>"
    }
    elseif ($Count -le 5) {
        return "<span class='inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-500/20 text-orange-400 border border-orange-500/30'>$Count</span>"
    }
    else {
        return "<span class='inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30'>$Count</span>"
    }
}

function Add-TreeToHtml {
    param($Node)

    $output = ""

    foreach ($file in $Node._files | Sort-Object Name) {
        $name = $file.Name
        $fullPath = $file.FullName.Replace("/", "\")
        $folderPath = $file.DirectoryName.Replace("/", "\").Replace("'", "\'")   # Escape single quotes

        $output += @"
            <div class="file flex items-center gap-4 px-6 py-4 rounded-2xl mx-1">
                <!-- Action Buttons -->
                <div class="flex gap-2 w-52 flex-shrink-0">
                    <button onclick="copyName('$($name.Replace("'", "\'"))')" 
                            class="px-4 py-2 text-xs font-medium bg-slate-700 hover:bg-slate-600 rounded-2xl transition-colors flex-1">
                        Name
                    </button>
                    <button onclick="copyPath('$($fullPath.Replace("'", "\'"))')" 
                            class="px-4 py-2 text-xs font-medium bg-slate-700 hover:bg-slate-600 rounded-2xl transition-colors flex-1">
                        Path
                    </button>
                    <button onclick="openFolder('$folderPath')" 
                            title="Open containing folder"
                            class="px-4 py-2 text-xs font-medium bg-blue-600 hover:bg-blue-500 rounded-2xl transition-colors flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2 2 2 0 01-2 2 2 2 0 01-2-2 2 2 0 012-2 2 2 0 01-2-2 2 2 0 012-2zm0 0V9a2 2 0 012-2 2 2 0 01-2-2 2 2 0 01-2-2 2 2 0 012-2z" />
                        </svg>
                    </button>
                </div>
                
                <!-- File Info -->
                <div class="flex-1 min-w-0">
                    <div class="font-medium text-slate-100">$name</div>
                    <div class="text-xs text-slate-400 mt-1 font-mono truncate">$fullPath</div>
                </div>
            </div>
"@
    }

    # Subfolders (unchanged)
    foreach ($key in ($Node._sub.Keys | Sort-Object)) {
        $subNode = $Node._sub[$key]
        
        function Count-Videos($n) {
            $c = $n._files.Count
            foreach ($s in $n._sub.Values) { $c += Count-Videos $s }
            $c
        }
        $branchTotal = Count-Videos $subNode

        $highlight = if ($branchTotal -le $MaxFiles) { "bg-amber-900/30 border-amber-400/40" } else { "bg-slate-800 border-slate-700" }
        $pill = Get-CountPill $branchTotal

        $output += @"
        <details class="group">
            <summary class="$highlight px-6 py-4 rounded-3xl border cursor-pointer hover:border-slate-500 flex items-center justify-between mb-2">
                <span class="font-semibold text-lg">$key</span>
                $pill
            </summary>
            <div class="pl-9 pt-2 pb-5 space-y-3 border-l border-slate-700 ml-6">
"@
        $output += Add-TreeToHtml $subNode
        $output += "</div></details>"
    }

    $output
}

$htmlBody = Add-TreeToHtml $FolderTree

$html = $htmlHeader + $htmlBody + @"
        </div>
    </div>

    <footer class="bg-slate-900 border-t border-slate-700 py-5 text-center text-xs text-slate-500">
        Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm") • PowerShell Video Scanner
    </footer>

    <script>
        function copyName(name) {
            navigator.clipboard.writeText(name).then(() => showToast("Name copied"));
        }
        function copyPath(path) {
            navigator.clipboard.writeText(path).then(() => showToast("Path copied"));
        }
        function openFolder(folderPath) {
            try {
                // Best method for opening folder in Windows Explorer
                const explorerCommand = 'explorer.exe "' + folderPath + '"';
                window.location.href = 'data:application/x-msdownload,' + encodeURIComponent(explorerCommand);
                
                // Fallback using file protocol
                setTimeout(() => {
                    window.open('file:///' + folderPath.replace(/\\/g, '/'), '_blank');
                }, 50);
                
                showToast("Opening folder in Explorer...");
            } catch(e) {
                alert("Could not open folder: " + folderPath);
            }
        }

        function showToast(msg) {
            const toast = document.createElement("div");
            toast.textContent = msg;
            toast.style.cssText = "position:fixed; bottom:30px; left:50%; transform:translateX(-50%); background:#1e2937; color:#bae6fd; padding:12px 26px; border-radius:9999px; z-index:1000; box-shadow:0 10px 15px -3px rgb(0 0 0 / 0.3);";
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 1600);
        }
    </script>
</body>
</html>
"@

# Save and open
$html | Out-File -FilePath $OutputHtml -Encoding UTF8
Write-Host "`n✅ Fixed report generated: $OutputHtml" -ForegroundColor Green
Invoke-Item $OutputHtml

# .\folderStructure.ps1 -RootPath "D:\H455N\_PMP_\" -OutputHtml "MyVideos.html" -MaxFiles 2


