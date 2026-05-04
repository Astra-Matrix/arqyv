# ─────────────────────────────────────────────────────────────────────────────
#  ARQYV — One-line installer for Windows (PowerShell 5.1+)
#  Usage: irm https://arqyv.app/install.ps1 | iex
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo       = "https://github.com/Alaustrup/arqyv.git"
$InstallDir = if ($env:ARQYV_DIR) { $env:ARQYV_DIR } else { "$env:LOCALAPPDATA\ARQYV" }
$LauncherDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

function Write-Step  { param($msg) Write-Host "  -> " -ForegroundColor Cyan -NoNewline; Write-Host $msg }
function Write-OK    { param($msg) Write-Host "  OK " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Write-Fatal { param($msg) Write-Host "  !! " -ForegroundColor Red -NoNewline; Write-Host $msg; exit 1 }

Clear-Host
Write-Host ""
Write-Host "    ___  ____  ___  _   _ _     __" -ForegroundColor Cyan
Write-Host "   / _ \|  _ \/ _ \| | | \ \   / /" -ForegroundColor Cyan
Write-Host "  / /_\ \ |_)| | | | |_| |\ \ / / " -ForegroundColor Cyan
Write-Host " /  _  |  _ \| |_| |  _  | \ V /  " -ForegroundColor Cyan
Write-Host "/_/   \_\_| \_\\__\_\_| |_|  \_/   " -ForegroundColor Cyan
Write-Host ""
Write-Host "  AI-powered personal media library" -ForegroundColor White
Write-Host ""

# ── Preflight ──────────────────────────────────────────────────────────────
Write-Step "Checking prerequisites..."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Fatal "git is required. Install from https://git-scm.com/download/win"
}

$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pyCmd) { Write-Fatal "Python 3.11+ required. Install from https://python.org" }

$pyVer = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
$parts = $pyVer.Split('.')
if ([int]$parts[0] -lt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -lt 11)) {
    Write-Fatal "Python 3.11+ required (found $pyVer). Download from https://python.org"
}
Write-OK "Python $pyVer found"

# ── Clone / update ─────────────────────────────────────────────────────────
if (Test-Path "$InstallDir\.git") {
    Write-Step "Updating existing install at $InstallDir..."
    & git -C $InstallDir pull --quiet --ff-only
} else {
    Write-Step "Cloning ARQYV into $InstallDir..."
    & git clone --depth 1 $Repo $InstallDir --quiet
}
Write-OK "Source ready at $InstallDir"

# ── Install Python dependencies ────────────────────────────────────────────
Write-Step "Installing Python dependencies..."
& python -m pip install --quiet --upgrade pip
& python -m pip install --quiet -e $InstallDir
Write-OK "Dependencies installed"

# ── Optional AI packages ───────────────────────────────────────────────────
$installAI = if ($env:ARQYV_AI) { $env:ARQYV_AI } else { "1" }
if ($installAI -eq "1") {
    Write-Step "Installing optional AI packages..."
    try {
        & python -m pip install --quiet sentence-transformers openai-whisper chromadb rank-bm25 imagehash
        Write-OK "AI packages installed"
    } catch {
        Write-Step "Some AI packages skipped. ARQYV still runs without them."
    }
}

# ── Launcher batch file ────────────────────────────────────────────────────
$BatchContent = "@echo off`r`npythonw `"$InstallDir\run.py`" %*`r`n"
$BatchPath = "$LauncherDir\arqyv.bat"
Set-Content -Path $BatchPath -Value $BatchContent -Encoding ASCII
Write-OK "Launcher created at $BatchPath"

# ── Start Menu shortcut ────────────────────────────────────────────────────
$StartMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$WshShell  = New-Object -ComObject WScript.Shell
$Shortcut  = $WshShell.CreateShortcut("$StartMenu\ARQYV.lnk")
$Shortcut.TargetPath  = "pythonw"
$Shortcut.Arguments   = "`"$InstallDir\run.py`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "ARQYV — AI media library"
$Shortcut.Save()
Write-OK "Start Menu shortcut created"

Write-Host ""
Write-Host "  ARQYV installed successfully!" -ForegroundColor Green
Write-Host "  Run:  arqyv   or open from the Start Menu" -ForegroundColor White
Write-Host "  Docs: https://arqyv.app/docs" -ForegroundColor Cyan
Write-Host ""
