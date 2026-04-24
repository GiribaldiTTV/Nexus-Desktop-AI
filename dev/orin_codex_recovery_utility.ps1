param(
    [ValidateSet("Backup", "Repair", "BackupAndRepair")]
    [string]$Mode = "Backup",
    [string]$OutputDirectory = [Environment]::GetFolderPath("Desktop"),
    [switch]$SkipPackageState,
    [switch]$ForceCloseCodex,
    [switch]$ResetClipboard,
    [switch]$QuarantineOversizedSessions,
    [ValidateRange(1, 4096)]
    [int]$OversizedSessionThresholdMB = 100,
    [switch]$ResetAppShellState,
    [switch]$RepairWindowsShell,
    [switch]$CaptureShellDiagnostics
)

$ErrorActionPreference = "Stop"

$script:UserProfile = [Environment]::GetFolderPath("UserProfile")
$script:DesktopPath = [Environment]::GetFolderPath("Desktop")
$script:LocalAppData = [Environment]::GetFolderPath("LocalApplicationData")
$script:CodexRoot = Join-Path $script:UserProfile ".codex"
$script:PackageRoot = Join-Path $script:LocalAppData "Packages\OpenAI.Codex_2p2nqsd0c76g0"
$script:RoamingCodexRoot = Join-Path $script:PackageRoot "LocalCache\Roaming\Codex"
$script:CodexProcessNames = @("Codex", "codex")
$script:ShellProcessNames = @("explorer", "StartMenuExperienceHost", "ShellExperienceHost", "SearchHost", "TextInputHost")

function Write-Step {
    param([string]$Message)
    Write-Host "[codex-recovery] $Message"
}

function Ensure-Directory {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "Ensure-Directory requires a non-empty path."
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Copy-PathIfPresent {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return $false
    }

    $parent = Split-Path -Parent $Destination
    Ensure-Directory -Path $parent
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    return $true
}

function Remove-ChildrenIfPresent {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }

    Get-ChildItem -LiteralPath $Path -Force | Remove-Item -Recurse -Force
    return $true
}

function Remove-FileIfPresent {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }

    Remove-Item -LiteralPath $Path -Force
    return $true
}

function Get-CodexProcesses {
    $allProcesses = @()
    foreach ($name in $script:CodexProcessNames) {
        $allProcesses += Get-Process -Name $name -ErrorAction SilentlyContinue
    }

    $seen = @{}
    $unique = foreach ($process in $allProcesses) {
        if (-not $seen.ContainsKey($process.Id)) {
            $seen[$process.Id] = $true
            $process
        }
    }

    return @($unique)
}

function Test-InertCodexResidue {
    param([System.Diagnostics.Process]$Process)

    $path = $null
    try {
        $path = $Process.Path
    } catch {
        $path = $null
    }

    return (
        $Process.ProcessName -eq "Codex" -and
        $Process.MainWindowHandle -eq 0 -and
        [string]::IsNullOrWhiteSpace($path) -and
        $Process.WorkingSet64 -le 128KB
    )
}

function Get-BlockingCodexProcesses {
    return @(
        Get-CodexProcesses | Where-Object { -not (Test-InertCodexResidue -Process $_) }
    )
}

function Format-ProcessSummary {
    param([System.Diagnostics.Process]$Process)

    return "{0}#{1}" -f $Process.ProcessName, $Process.Id
}

function Assert-CodexClosed {
    $blocking = Get-BlockingCodexProcesses
    if ($blocking.Count -gt 0) {
        $details = ($blocking | Sort-Object ProcessName, Id | ForEach-Object { Format-ProcessSummary -Process $_ }) -join ", "
        throw "Codex must be fully closed before this utility runs. Still running: $details. If Windows reports Access is denied, right-click the repair batch and choose Run as administrator, or restart Windows and run repair before reopening Codex."
    }

    $residue = @(Get-CodexProcesses | Where-Object { Test-InertCodexResidue -Process $_ })
    if ($residue.Count -gt 0) {
        $details = ($residue | Sort-Object Id | ForEach-Object { Format-ProcessSummary -Process $_ }) -join ", "
        Write-Step "Ignoring inert Codex shell residue: $details"
    }
}

function Invoke-GracefulCodexClose {
    param(
        [System.Diagnostics.Process[]]$Processes,
        [System.Collections.Generic.List[string]]$Actions
    )

    foreach ($process in $Processes) {
        if ($process.MainWindowHandle -eq 0) {
            continue
        }

        try {
            if ($process.CloseMainWindow()) {
                $Actions.Add("requested graceful close for $(Format-ProcessSummary -Process $process)") | Out-Null
            }
        } catch {
            $Actions.Add("graceful close skipped for $(Format-ProcessSummary -Process $process): $($_.Exception.Message)") | Out-Null
        }
    }
}

function Stop-CodexIfRequested {
    param(
        [bool]$Force,
        [System.Collections.Generic.List[string]]$Actions
    )

    if (-not $Force) {
        Assert-CodexClosed
        return
    }

    $blocking = Get-BlockingCodexProcesses
    if ($blocking.Count -eq 0) {
        Assert-CodexClosed
        return
    }

    $details = ($blocking | Sort-Object ProcessName, Id | ForEach-Object { Format-ProcessSummary -Process $_ }) -join ", "
    Write-Step "Closing Codex processes: $details"

    Invoke-GracefulCodexClose -Processes $blocking -Actions $Actions
    Start-Sleep -Seconds 2

    foreach ($process in (Get-BlockingCodexProcesses)) {
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            $Actions.Add("force-stopped $(Format-ProcessSummary -Process $process)") | Out-Null
        } catch {
            $Actions.Add("Stop-Process failed for $(Format-ProcessSummary -Process $process): $($_.Exception.Message)") | Out-Null
        }
    }

    Start-Sleep -Seconds 2

    foreach ($process in (Get-BlockingCodexProcesses)) {
        $null = & taskkill.exe /PID $process.Id /T /F 2>&1
        if ($LASTEXITCODE -eq 0) {
            $Actions.Add("taskkill stopped $(Format-ProcessSummary -Process $process)") | Out-Null
        } else {
            $Actions.Add("taskkill failed for $(Format-ProcessSummary -Process $process)") | Out-Null
        }
    }

    Start-Sleep -Seconds 2
    Assert-CodexClosed
}

function Get-DisplayPath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $Path
    }

    if ($Path.StartsWith($script:DesktopPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Replace($script:DesktopPath, "$env:USERPROFILE\Desktop")
    }

    if ($Path.StartsWith($script:UserProfile, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Replace($script:UserProfile, "$env:USERPROFILE")
    }

    return $Path
}

function New-RecoveryReadme {
    param(
        [string]$Path,
        [string]$ModeValue,
        [string[]]$IncludedPaths
    )

    $includedBlock = if ($IncludedPaths.Count -gt 0) {
        ($IncludedPaths | ForEach-Object { "- $_" }) -join [Environment]::NewLine
    } else {
        "- No source paths were available on this machine."
    }

    @"
Codex Recovery Utility Bundle
Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')
Mode: $ModeValue

What this bundle contains:
$includedBlock

Restore guidance:
1. Make sure Codex is fully closed.
2. Keep this zip somewhere safe before uninstalling or repairing Codex.
3. After reinstalling Codex, launch it once, then close it again.
4. Extract the backed-up folders to their original locations.
5. Launch Codex and verify your local state returned.

Important:
- This utility is designed to be run only while Codex is closed.
- If you used Repair or BackupAndRepair mode, review REPAIR_REPORT.txt in the same bundle folder.
- If the restored state behaves badly, rename the restored folders aside and relaunch Codex to let it rebuild fresh state.
"@ | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Get-ProcessSnapshotLines {
    param([string[]]$Names)

    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($name in $Names) {
        $processes = Get-Process -Name $name -ErrorAction SilentlyContinue | Sort-Object Id
        if (-not $processes) {
            $lines.Add("${name}: not running") | Out-Null
            continue
        }

        foreach ($process in $processes) {
            $path = $null
            try {
                $path = $process.Path
            } catch {
                $path = $null
            }

            $wsMb = [math]::Round($process.WorkingSet64 / 1MB, 2)
            $startText = "unknown"
            try {
                $startText = $process.StartTime.ToString("yyyy-MM-dd HH:mm:ss")
            } catch {
                $startText = "unavailable"
            }

            $line = "{0} pid={1} ws_mb={2} main_window={3} started={4}" -f $process.ProcessName, $process.Id, $wsMb, $process.MainWindowHandle, $startText
            if (-not [string]::IsNullOrWhiteSpace($path)) {
                $line = "$line path=$path"
            }
            $lines.Add($line) | Out-Null
        }
    }

    return $lines.ToArray()
}

function Get-RelevantApplicationEvents {
    param([datetime]$StartTime)

    $providers = @("Application Hang", "Windows Error Reporting", "Application Error")
    $events = New-Object System.Collections.Generic.List[object]

    foreach ($provider in $providers) {
        try {
            $providerEvents = Get-WinEvent -FilterHashtable @{
                LogName = "Application"
                StartTime = $StartTime
                ProviderName = $provider
            } -ErrorAction Stop

            foreach ($event in $providerEvents) {
                if ($event.Message -match "Codex\.exe|explorer\.exe|StartMenuExperienceHost|ShellExperienceHost|SearchHost|TextInputHost|svchost\.exe") {
                    $events.Add($event) | Out-Null
                }
            }
        } catch {
            continue
        }
    }

    return @($events | Sort-Object TimeCreated -Descending | Select-Object -First 30)
}

function Format-EventSummary {
    param($Event)

    $lines = @($Event.Message -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $snippet = ($lines | Select-Object -First 5) -join " | "
    return "[{0}] {1} #{2} {3}" -f $Event.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss"), $Event.ProviderName, $Event.Id, $snippet
}

function Export-ShellDiagnosticsSnapshot {
    param(
        [string]$Path,
        [string]$Stage
    )

    $divider = "=" * 78
    $content = New-Object System.Collections.Generic.List[string]
    $content.Add($divider) | Out-Null
    $content.Add("Stage: $Stage") | Out-Null
    $content.Add("Captured: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')") | Out-Null
    $content.Add("") | Out-Null
    $content.Add("Relevant processes:") | Out-Null

    foreach ($line in (Get-ProcessSnapshotLines -Names ($script:ShellProcessNames + $script:CodexProcessNames))) {
        $content.Add("- $line") | Out-Null
    }

    $content.Add("") | Out-Null
    $content.Add("Recent relevant Application log events:") | Out-Null
    $events = Get-RelevantApplicationEvents -StartTime (Get-Date).AddDays(-2)
    if ($events.Count -eq 0) {
        $content.Add("- none found in the last 48 hours") | Out-Null
    } else {
        foreach ($event in $events) {
            $content.Add("- $(Format-EventSummary -Event $event)") | Out-Null
        }
    }

    $content.Add("") | Out-Null
    Add-Content -LiteralPath $Path -Value $content -Encoding UTF8
}

function Invoke-ClipboardReset {
    param([System.Collections.Generic.List[string]]$Actions)

    try {
        powershell -NoProfile -STA -Command "Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.Clipboard]::Clear()"
        if ($LASTEXITCODE -eq 0) {
            $Actions.Add("cleared current Windows clipboard contents") | Out-Null
        } else {
            $Actions.Add("attempted clipboard clear, but the STA clipboard helper returned exit code $LASTEXITCODE") | Out-Null
        }
    } catch {
        $Actions.Add("clipboard clear failed: $($_.Exception.Message)") | Out-Null
    }

    $clipboardServices = Get-Service | Where-Object { $_.Name -like "cbdhsvc_*" }
    foreach ($service in $clipboardServices) {
        try {
            Restart-Service -Name $service.Name -Force -ErrorAction Stop
            $Actions.Add("restarted clipboard service $($service.Name)") | Out-Null
        } catch {
            $Actions.Add("clipboard service restart skipped for $($service.Name): $($_.Exception.Message)") | Out-Null
        }
    }

    $textInputHosts = Get-Process -Name TextInputHost -ErrorAction SilentlyContinue
    foreach ($process in $textInputHosts) {
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            $Actions.Add("restarted TextInputHost process $($process.Id)") | Out-Null
        } catch {
            $Actions.Add("TextInputHost restart skipped for $($process.Id): $($_.Exception.Message)") | Out-Null
        }
    }
}

function New-BackupBundle {
    param(
        [string]$DesktopPath,
        [bool]$IncludePackageState
    )

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $bundleRoot = Join-Path $DesktopPath "Codex_Recovery_Bundle_$stamp"
    $zipPath = "$bundleRoot.zip"
    $payloadRoot = Join-Path $bundleRoot "payload"
    Ensure-Directory -Path $payloadRoot

    $sources = @(
        @{
            Source = $script:CodexRoot
            Destination = Join-Path $payloadRoot ".codex"
        },
        @{
            Source = Join-Path $script:LocalAppData "OpenAI\Codex"
            Destination = Join-Path $payloadRoot "Local_OpenAI\Codex"
        }
    )

    if ($IncludePackageState) {
        $sources += @{
            Source = $script:PackageRoot
            Destination = Join-Path $payloadRoot "Packages\OpenAI.Codex_2p2nqsd0c76g0"
        }
    }

    $includedPaths = New-Object System.Collections.Generic.List[string]
    foreach ($entry in $sources) {
        if (Copy-PathIfPresent -Source $entry.Source -Destination $entry.Destination) {
            $includedPaths.Add($entry.Source) | Out-Null
        }
    }

    New-RecoveryReadme -Path (Join-Path $bundleRoot "RESTORE_INSTRUCTIONS.txt") -ModeValue "Backup" -IncludedPaths $includedPaths.ToArray()

    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath -CompressionLevel Optimal -Force

    return @{
        BundleRoot = $bundleRoot
        ZipPath = $zipPath
        IncludedPaths = $includedPaths.ToArray()
    }
}

function Invoke-OversizedSessionQuarantine {
    param(
        [string]$DesktopPath,
        [int]$ThresholdMB,
        [System.Collections.Generic.List[string]]$Actions
    )

    $thresholdBytes = $ThresholdMB * 1MB
    $candidates = New-Object System.Collections.Generic.List[System.IO.FileInfo]
    foreach ($root in @((Join-Path $script:CodexRoot "sessions"), (Join-Path $script:CodexRoot "archived_sessions"))) {
        if (-not (Test-Path -LiteralPath $root)) {
            continue
        }

        foreach ($file in (Get-ChildItem -LiteralPath $root -Recurse -File -Filter "*.jsonl" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt $thresholdBytes })) {
            $candidates.Add($file) | Out-Null
        }
    }

    if ($candidates.Count -eq 0) {
        $Actions.Add("found no Codex session files over ${ThresholdMB} MB to quarantine") | Out-Null
        return $null
    }

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $quarantineRoot = Join-Path $DesktopPath "Codex_Oversized_Session_Quarantine_$stamp"
    Ensure-Directory -Path $quarantineRoot

    foreach ($file in $candidates) {
        $relative = $file.FullName.Substring($script:CodexRoot.Length).TrimStart("\")
        $destination = Join-Path $quarantineRoot $relative
        Ensure-Directory -Path (Split-Path -Parent $destination)
        Move-Item -LiteralPath $file.FullName -Destination $destination -Force
        $sizeMb = [math]::Round($file.Length / 1MB, 2)
        $Actions.Add("cold-quarantined oversized session $($file.FullName) (${sizeMb} MB) to $destination") | Out-Null
    }

    return $quarantineRoot
}

function Invoke-AppShellReset {
    param([System.Collections.Generic.List[string]]$Actions)

    if (-not (Test-Path -LiteralPath $script:RoamingCodexRoot)) {
        $Actions.Add("Codex app-shell cache root was not present: $script:RoamingCodexRoot") | Out-Null
        return
    }

    $resetDirectories = @(
        (Join-Path $script:RoamingCodexRoot "Cache"),
        (Join-Path $script:RoamingCodexRoot "Code Cache"),
        (Join-Path $script:RoamingCodexRoot "GPUCache"),
        (Join-Path $script:RoamingCodexRoot "DawnGraphiteCache"),
        (Join-Path $script:RoamingCodexRoot "DawnWebGPUCache"),
        (Join-Path $script:RoamingCodexRoot "Shared Dictionary\cache"),
        (Join-Path $script:RoamingCodexRoot "blob_storage"),
        (Join-Path $script:RoamingCodexRoot "Local Storage"),
        (Join-Path $script:RoamingCodexRoot "Session Storage"),
        (Join-Path $script:RoamingCodexRoot "sentry"),
        (Join-Path $script:RoamingCodexRoot "Crashpad")
    )

    foreach ($directory in $resetDirectories) {
        if (Remove-ChildrenIfPresent -Path $directory) {
            $Actions.Add("cleared Codex app-shell directory $directory") | Out-Null
        }
    }

    $resetFiles = @(
        (Join-Path $script:RoamingCodexRoot "DIPS"),
        (Join-Path $script:RoamingCodexRoot "DIPS-wal"),
        (Join-Path $script:RoamingCodexRoot "SharedStorage"),
        (Join-Path $script:RoamingCodexRoot "SharedStorage-wal"),
        (Join-Path $script:RoamingCodexRoot "Local State"),
        (Join-Path $script:RoamingCodexRoot "Preferences"),
        (Join-Path $script:RoamingCodexRoot "lockfile")
    )

    foreach ($file in $resetFiles) {
        if (Remove-FileIfPresent -Path $file) {
            $Actions.Add("removed Codex app-shell file $file") | Out-Null
        }
    }
}

function Invoke-WindowsShellRecovery {
    param([System.Collections.Generic.List[string]]$Actions)

    foreach ($processName in @("StartMenuExperienceHost", "ShellExperienceHost", "SearchHost", "TextInputHost")) {
        foreach ($process in (Get-Process -Name $processName -ErrorAction SilentlyContinue)) {
            try {
                Stop-Process -Id $process.Id -Force -ErrorAction Stop
                $Actions.Add("restarted Windows shell helper $processName process $($process.Id)") | Out-Null
            } catch {
                $Actions.Add("Windows shell helper restart skipped for $processName process $($process.Id): $($_.Exception.Message)") | Out-Null
            }
        }
    }

    $explorerWasRunning = $false
    foreach ($process in (Get-Process -Name explorer -ErrorAction SilentlyContinue)) {
        $explorerWasRunning = $true
        try {
            if ($process.MainWindowHandle -ne 0) {
                $null = $process.CloseMainWindow()
            }
        } catch {
        }
    }

    if ($explorerWasRunning) {
        Start-Sleep -Seconds 2
        foreach ($process in (Get-Process -Name explorer -ErrorAction SilentlyContinue)) {
            try {
                Stop-Process -Id $process.Id -Force -ErrorAction Stop
                $Actions.Add("stopped explorer.exe process $($process.Id) for shell rebuild") | Out-Null
            } catch {
                $Actions.Add("explorer.exe stop skipped for $($process.Id): $($_.Exception.Message)") | Out-Null
            }
        }
    } else {
        $Actions.Add("explorer.exe was not running before shell recovery; starting a fresh shell instance") | Out-Null
    }

    Start-Sleep -Seconds 2
    Start-Process explorer.exe
    $Actions.Add("started explorer.exe to rebuild the Windows taskbar and Start menu shell") | Out-Null
}

function New-RepairReport {
    param(
        [string]$Path,
        [string[]]$Actions,
        [string]$DiagnosticsPath,
        [string]$QuarantinePath
    )

    $actionBlock = if ($Actions.Count -gt 0) {
        ($Actions | ForEach-Object { "- $_" }) -join [Environment]::NewLine
    } else {
        "- No repair actions were needed."
    }

    $extras = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($DiagnosticsPath)) {
        $extras.Add("- Shell diagnostics: $(Get-DisplayPath -Path $DiagnosticsPath)") | Out-Null
    }
    if (-not [string]::IsNullOrWhiteSpace($QuarantinePath)) {
        $extras.Add("- Oversized-session quarantine: $(Get-DisplayPath -Path $QuarantinePath)") | Out-Null
    }

    $extraBlock = if ($extras.Count -gt 0) {
        ($extras | ForEach-Object { $_ }) -join [Environment]::NewLine
    } else {
        "- No additional artifacts were created."
    }

    @"
Codex Repair Report
Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')

Actions performed:
$actionBlock

Artifacts:
$extraBlock

Repair scope:
- Removed transient sqlite WAL/SHM files so Codex can rebuild them cleanly.
- Cleared temp/cache folders that are safe to regenerate.
- Cleared Electron renderer, code, GPU, and WebGPU caches that can contribute to UI stalls.
- Can cold-quarantine oversized session files outside .codex after a backup.
- Can reset Codex app-shell state that may keep bad sidebar, pin, or window state alive.
- Can restart the Windows taskbar and Start-menu shell if shell recovery is requested.
- Can capture shell/Codex hang evidence into a lightweight diagnostics log for the next freeze.
- Optionally resets Windows clipboard state when requested.
- Did not delete your primary .codex memories, auth, config, plugins, or skills.
"@ | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Invoke-SafeRepair {
    param(
        [string]$DesktopPath,
        [bool]$ResetClipboardState,
        [bool]$QuarantineSessions,
        [int]$ThresholdMB,
        [bool]$ResetCodexAppShellState,
        [bool]$RecoverWindowsShell,
        [bool]$CaptureDiagnostics
    )

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $repairRoot = Join-Path $DesktopPath "Codex_Repair_Report_$stamp"
    Ensure-Directory -Path $repairRoot

    $actions = New-Object System.Collections.Generic.List[string]
    $diagnosticsPath = $null
    $quarantineRoot = $null

    if ($CaptureDiagnostics) {
        $diagnosticsPath = Join-Path $repairRoot "SHELL_DIAGNOSTICS.txt"
        Export-ShellDiagnosticsSnapshot -Path $diagnosticsPath -Stage "Before repair"
        $actions.Add("captured pre-repair shell diagnostics to $diagnosticsPath") | Out-Null
    }

    $transientFiles = @(
        (Join-Path $script:CodexRoot "logs_2.sqlite-shm"),
        (Join-Path $script:CodexRoot "logs_2.sqlite-wal"),
        (Join-Path $script:CodexRoot "state_5.sqlite-shm"),
        (Join-Path $script:CodexRoot "state_5.sqlite-wal")
    )

    foreach ($file in $transientFiles) {
        if (Remove-FileIfPresent -Path $file) {
            $actions.Add("removed transient file $file") | Out-Null
        }
    }

    $transientDirs = @(
        (Join-Path $script:CodexRoot ".tmp"),
        (Join-Path $script:CodexRoot "tmp"),
        (Join-Path $script:PackageRoot "TempState"),
        (Join-Path $script:PackageRoot "AC\Temp"),
        (Join-Path $script:RoamingCodexRoot "Cache"),
        (Join-Path $script:RoamingCodexRoot "Code Cache"),
        (Join-Path $script:RoamingCodexRoot "GPUCache"),
        (Join-Path $script:RoamingCodexRoot "DawnGraphiteCache"),
        (Join-Path $script:RoamingCodexRoot "DawnWebGPUCache"),
        (Join-Path $script:RoamingCodexRoot "Shared Dictionary\cache")
    )

    foreach ($dir in $transientDirs) {
        if (Remove-ChildrenIfPresent -Path $dir) {
            $actions.Add("cleared transient directory $dir") | Out-Null
        }
    }

    $localCacheRoot = Join-Path $script:PackageRoot "LocalCache"
    foreach ($cacheDir in @((Join-Path $localCacheRoot "Temp"), (Join-Path $localCacheRoot "Local\Temp"))) {
        if (Remove-ChildrenIfPresent -Path $cacheDir) {
            $actions.Add("cleared cache directory $cacheDir") | Out-Null
        }
    }

    if ($ResetCodexAppShellState) {
        Invoke-AppShellReset -Actions $actions
    }

    if ($QuarantineSessions) {
        $quarantineRoot = Invoke-OversizedSessionQuarantine -DesktopPath $DesktopPath -ThresholdMB $ThresholdMB -Actions $actions
    }

    if ($ResetClipboardState) {
        Invoke-ClipboardReset -Actions $actions
    }

    if ($RecoverWindowsShell) {
        Invoke-WindowsShellRecovery -Actions $actions
    }

    if ($CaptureDiagnostics) {
        Export-ShellDiagnosticsSnapshot -Path $diagnosticsPath -Stage "After repair"
        $actions.Add("captured post-repair shell diagnostics to $diagnosticsPath") | Out-Null
    }

    New-RepairReport -Path (Join-Path $repairRoot "REPAIR_REPORT.txt") -Actions $actions.ToArray() -DiagnosticsPath $diagnosticsPath -QuarantinePath $quarantineRoot

    return @{
        RepairRoot = $repairRoot
        Actions = $actions.ToArray()
        DiagnosticsPath = $diagnosticsPath
        QuarantinePath = $quarantineRoot
    }
}

$startupActions = New-Object System.Collections.Generic.List[string]
Stop-CodexIfRequested -Force:$ForceCloseCodex -Actions $startupActions
Ensure-Directory -Path $OutputDirectory

$includePackageState = -not $SkipPackageState
$backupResult = $null
$repairResult = $null

switch ($Mode) {
    "Backup" {
        Write-Step "Creating full Codex recovery bundle."
        $backupResult = New-BackupBundle -DesktopPath $OutputDirectory -IncludePackageState:$includePackageState
    }
    "Repair" {
        Write-Step "Running safe Codex repair."
        $repairResult = Invoke-SafeRepair `
            -DesktopPath $OutputDirectory `
            -ResetClipboardState:$ResetClipboard `
            -QuarantineSessions:$QuarantineOversizedSessions `
            -ThresholdMB $OversizedSessionThresholdMB `
            -ResetCodexAppShellState:$ResetAppShellState `
            -RecoverWindowsShell:$RepairWindowsShell `
            -CaptureDiagnostics:$CaptureShellDiagnostics
    }
    "BackupAndRepair" {
        Write-Step "Creating recovery bundle before repair."
        $backupResult = New-BackupBundle -DesktopPath $OutputDirectory -IncludePackageState:$includePackageState
        Write-Step "Running safe Codex repair."
        $repairResult = Invoke-SafeRepair `
            -DesktopPath $OutputDirectory `
            -ResetClipboardState:$ResetClipboard `
            -QuarantineSessions:$QuarantineOversizedSessions `
            -ThresholdMB $OversizedSessionThresholdMB `
            -ResetCodexAppShellState:$ResetAppShellState `
            -RecoverWindowsShell:$RepairWindowsShell `
            -CaptureDiagnostics:$CaptureShellDiagnostics
    }
}

if ($startupActions.Count -gt 0 -and $repairResult) {
    $repairResult.Actions = @($startupActions.ToArray() + $repairResult.Actions)
    New-RepairReport `
        -Path (Join-Path $repairResult.RepairRoot "REPAIR_REPORT.txt") `
        -Actions $repairResult.Actions `
        -DiagnosticsPath $repairResult.DiagnosticsPath `
        -QuarantinePath $repairResult.QuarantinePath
}

$result = [ordered]@{
    mode = $Mode
    output_directory = $OutputDirectory
}

if ($backupResult) {
    $result["backup_zip"] = $backupResult.ZipPath
}

if ($repairResult) {
    $result["repair_report_dir"] = $repairResult.RepairRoot
    $result["repair_actions"] = $repairResult.Actions
    if ($repairResult.DiagnosticsPath) {
        $result["shell_diagnostics"] = $repairResult.DiagnosticsPath
    }
    if ($repairResult.QuarantinePath) {
        $result["oversized_session_quarantine"] = $repairResult.QuarantinePath
    }
}

$result | ConvertTo-Json -Depth 4
