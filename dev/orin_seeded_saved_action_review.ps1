param(
    [switch]$RestoreOnly
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SourcePath = Join-Path $env:LOCALAPPDATA "Nexus Desktop AI\saved_actions.json"
$StateDir = Join-Path $RootDir "dev\logs\seeded_saved_action_review"
$BackupPath = Join-Path $StateDir "saved_actions.backup.json"
$LauncherPath = Join-Path $RootDir "desktop\orin_desktop_launcher.pyw"

function Ensure-StateDir {
    New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
}

function Backup-Source {
    Ensure-StateDir
    if (Test-Path -LiteralPath $SourcePath) {
        Copy-Item -LiteralPath $SourcePath -Destination $BackupPath -Force
    } elseif (Test-Path -LiteralPath $BackupPath) {
        Remove-Item -LiteralPath $BackupPath -Force
    }
}

function Restore-Source {
    if (Test-Path -LiteralPath $BackupPath) {
        Copy-Item -LiteralPath $BackupPath -Destination $SourcePath -Force
        return $true
    }
    return $false
}

function Write-SeededSource {
    $payload = [ordered]@{
        schema_version = 1
        actions        = @(
            [ordered]@{
                id              = "open_notepad_task"
                title           = "Open Weekly Reports"
                target_kind     = "folder"
                target          = "C:\Windows"
                aliases         = @("weekly reports")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "weekly_reports_explorer"
                title           = "Weekly Reports Explorer"
                target_kind     = "app"
                target          = "explorer.exe"
                aliases         = @("weekly reports")
                invocation_mode = "aliases_only"
                trigger_mode    = "launch"
            },
            [ordered]@{
                id              = "open_notes_task"
                title           = "Open Notes Task"
                target_kind     = "app"
                target          = "notepad.exe"
                aliases         = @("notes task")
                invocation_mode = "aliases_only"
                trigger_mode    = "launch"
            },
            [ordered]@{
                id              = "workspace_docs_folder"
                title           = "Open Workspace Docs"
                target_kind     = "folder"
                target          = "C:\Nexus Desktop AI\Docs"
                aliases         = @("workspace docs")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_readme_task"
                title           = "Open Root README"
                target_kind     = "file"
                target          = "C:\Nexus Desktop AI\README.md"
                aliases         = @("root readme")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_launcher_source"
                title           = "Open Desktop Launcher"
                target_kind     = "file"
                target          = "C:\Nexus Desktop AI\desktop\orin_desktop_launcher.pyw"
                aliases         = @("desktop launcher")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_issue_board"
                title           = "Open Screenshot Folder"
                target_kind     = "folder"
                target          = "C:\Users\anden\OneDrive\Pictures\Screenshots"
                aliases         = @("screenshot folder")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            },
            [ordered]@{
                id              = "open_saved_source"
                title           = "Open Saved Action Source Module"
                target_kind     = "file"
                target          = "C:\Nexus Desktop AI\desktop\saved_action_source.py"
                aliases         = @("saved action source")
                invocation_mode = "aliases_only"
                trigger_mode    = "open"
            }
        )
        groups         = @(
            [ordered]@{
                id                = "workspace_tools"
                title             = "Workspace Tools"
                aliases           = @("workspace tools")
                member_action_ids = @("open_saved_source", "open_notepad_task")
            },
            [ordered]@{
                id                = "notes_suite"
                title             = "Notes Suite"
                aliases           = @("notes suite")
                member_action_ids = @("open_notes_task")
            },
            [ordered]@{
                id                = "docs_hub"
                title             = "Docs Hub"
                aliases           = @("docs hub")
                member_action_ids = @("workspace_docs_folder", "open_readme_task")
            },
            [ordered]@{
                id                = "launcher_tools"
                title             = "Launcher Tools"
                aliases           = @("launcher tools")
                member_action_ids = @("open_launcher_source", "open_saved_source")
            },
            [ordered]@{
                id                = "planning_board"
                title             = "Planning Board"
                aliases           = @("planning board")
                member_action_ids = @("open_issue_board", "weekly_reports_explorer")
            },
            [ordered]@{
                id                = "review_pack"
                title             = "Review Pack"
                aliases           = @("review pack")
                member_action_ids = @("open_readme_task", "open_notes_task", "open_saved_source")
            },
            [ordered]@{
                id                = "workspace_launchers"
                title             = "Workspace Launchers"
                aliases           = @("workspace launchers")
                member_action_ids = @("open_notepad_task", "workspace_docs_folder", "open_issue_board")
            }
        )
    }

    $json = ($payload | ConvertTo-Json -Depth 8) + "`n"
    $encoding = New-Object System.Text.UTF8Encoding($false)
    Ensure-StateDir
    [System.IO.File]::WriteAllText($SourcePath, $json, $encoding)
}

function Launch-Desktop {
    if (-not (Test-Path -LiteralPath $LauncherPath)) {
        throw "Launcher not found: $LauncherPath"
    }

    $python = (Get-Command python).Source
    if (-not $python) {
        throw "Could not resolve the python executable."
    }

    $argString = '"' + $LauncherPath + '"'
    Start-Process -FilePath $python -ArgumentList $argString -WorkingDirectory $RootDir -WindowStyle Hidden | Out-Null
}

if ($RestoreOnly) {
    if (Restore-Source) {
        Write-Host "Restored saved action source from $BackupPath"
    } else {
        Write-Host "No seeded review backup was found at $BackupPath"
    }
    exit 0
}

Backup-Source
Write-SeededSource
Launch-Desktop

Write-Host "Seeded saved action review source written to $SourcePath"
Write-Host "Backup saved to $BackupPath"
Write-Host "Launcher started with the seeded 7+ task/group review dataset."
