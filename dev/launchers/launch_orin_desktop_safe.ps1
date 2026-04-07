param(
    [switch]$OverlayTrace
)

$ErrorActionPreference = "Stop"

$pythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
$launchersDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent (Split-Path -Parent $launchersDir)
$launcherPath = Join-Path $rootDir "desktop\orin_desktop_launcher.pyw"

if (-not (Test-Path -LiteralPath $pythonwPath)) {
    throw "pythonw.exe not found at: $pythonwPath"
}

if (-not (Test-Path -LiteralPath $launcherPath)) {
    throw "Desktop launcher not found at: $launcherPath"
}

$previousOverlayTrace = $env:NEXUS_OVERLAY_TRACE

try {
    if ($OverlayTrace) {
        $env:NEXUS_OVERLAY_TRACE = "1"
    }

    $process = Start-Process `
        -FilePath $pythonwPath `
        -ArgumentList @($launcherPath) `
        -WorkingDirectory $rootDir `
        -WindowStyle Hidden `
        -PassThru

    Write-Output ("SAFE_DESKTOP_LAUNCHER|pid=" + $process.Id + "|launcher=" + $launcherPath)
}
finally {
    if ($null -eq $previousOverlayTrace) {
        Remove-Item Env:NEXUS_OVERLAY_TRACE -ErrorAction SilentlyContinue
    }
    else {
        $env:NEXUS_OVERLAY_TRACE = $previousOverlayTrace
    }
}
