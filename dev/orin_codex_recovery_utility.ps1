param(
    [ValidateSet("Backup", "Repair", "BackupAndRepair")]
    [string]$Mode = "Backup",
    [string]$OutputDirectory = [Environment]::GetFolderPath("Desktop"),
    [switch]$SkipPackageState,
    [switch]$ForceCloseCodex,
    [switch]$ResetClipboard
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[codex-recovery] $Message"
}

function Assert-CodexClosed {
    $running = Get-Process | Where-Object { $_.ProcessName -like "*Codex*" -or $_.ProcessName -like "codex" }
    if ($running) {
        $details = ($running | Sort-Object ProcessName, Id | ForEach-Object { "$($_.ProcessName)#$($_.Id)" }) -join ", "
        throw "Codex must be fully closed before this utility runs. Still running: $details"
    }
}

function Stop-CodexIfRequested {
    param([bool]$Force)

    if (-not $Force) {
        Assert-CodexClosed
        return
    }

    $running = Get-Process | Where-Object { $_.ProcessName -like "*Codex*" -or $_.ProcessName -like "codex" }
    if (-not $running) {
        return
    }

    $details = ($running | Sort-Object ProcessName, Id | ForEach-Object { "$($_.ProcessName)#$($_.Id)" }) -join ", "
    Write-Step "Closing Codex processes: $details"
    $running | Stop-Process -Force
    Start-Sleep -Seconds 2
    Assert-CodexClosed
}

function Ensure-Directory {
    param([string]$Path)
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

function New-RepairReport {
    param(
        [string]$Path,
        [string[]]$Actions
    )

    $actionBlock = if ($Actions.Count -gt 0) {
        ($Actions | ForEach-Object { "- $_" }) -join [Environment]::NewLine
    } else {
        "- No repair actions were needed."
    }

    @"
Codex Repair Report
Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')

Actions performed:
$actionBlock

Repair scope:
- Removed transient sqlite WAL/SHM files so Codex can rebuild them cleanly.
- Cleared temp/cache folders that are safe to regenerate.
- Cleared Electron renderer, code, GPU, and WebGPU caches that can contribute to UI stalls.
- Optionally reset Windows clipboard state when requested.
- Did not delete your primary .codex sessions, memories, auth, config, plugins, or skills.
"@ | Set-Content -LiteralPath $Path -Encoding UTF8
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
            Source = "C:\Users\anden\.codex"
            Destination = Join-Path $payloadRoot ".codex"
        },
        @{
            Source = "C:\Users\anden\AppData\Local\OpenAI\Codex"
            Destination = Join-Path $payloadRoot "Local_OpenAI\Codex"
        }
    )

    if ($IncludePackageState) {
        $sources += @{
            Source = "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0"
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

function Invoke-SafeRepair {
    param(
        [string]$DesktopPath,
        [bool]$ResetClipboardState
    )

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $repairRoot = Join-Path $DesktopPath "Codex_Repair_Report_$stamp"
    Ensure-Directory -Path $repairRoot
    $actions = New-Object System.Collections.Generic.List[string]

    $transientFiles = @(
        "C:\Users\anden\.codex\logs_2.sqlite-shm",
        "C:\Users\anden\.codex\logs_2.sqlite-wal",
        "C:\Users\anden\.codex\state_5.sqlite-shm",
        "C:\Users\anden\.codex\state_5.sqlite-wal"
    )

    foreach ($file in $transientFiles) {
        if (Remove-FileIfPresent -Path $file) {
            $actions.Add("removed transient file $file") | Out-Null
        }
    }

    $transientDirs = @(
        "C:\Users\anden\.codex\.tmp",
        "C:\Users\anden\.codex\tmp",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\TempState",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\AC\Temp",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\Cache",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\Code Cache",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\GPUCache",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\DawnGraphiteCache",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\DawnWebGPUCache",
        "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Roaming\Codex\Shared Dictionary\cache"
    )

    foreach ($dir in $transientDirs) {
        if (Remove-ChildrenIfPresent -Path $dir) {
            $actions.Add("cleared transient directory $dir") | Out-Null
        }
    }

    $localCacheRoot = "C:\Users\anden\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache"
    if (Test-Path -LiteralPath $localCacheRoot) {
        $cacheTargets = @(
            (Join-Path $localCacheRoot "Temp"),
            (Join-Path $localCacheRoot "Local\Temp")
        )
        foreach ($cacheDir in $cacheTargets) {
            if (Remove-ChildrenIfPresent -Path $cacheDir) {
                $actions.Add("cleared cache directory $cacheDir") | Out-Null
            }
        }
    }

    if ($ResetClipboardState) {
        Invoke-ClipboardReset -Actions $actions
    }

    New-RepairReport -Path (Join-Path $repairRoot "REPAIR_REPORT.txt") -Actions $actions.ToArray()

    return @{
        RepairRoot = $repairRoot
        Actions = $actions.ToArray()
    }
}

Stop-CodexIfRequested -Force:$ForceCloseCodex
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
        $repairResult = Invoke-SafeRepair -DesktopPath $OutputDirectory -ResetClipboardState:$ResetClipboard
    }
    "BackupAndRepair" {
        Write-Step "Creating recovery bundle before repair."
        $backupResult = New-BackupBundle -DesktopPath $OutputDirectory -IncludePackageState:$includePackageState
        Write-Step "Running safe Codex repair."
        $repairResult = Invoke-SafeRepair -DesktopPath $OutputDirectory -ResetClipboardState:$ResetClipboard
    }
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
}

$result | ConvertTo-Json -Depth 4
