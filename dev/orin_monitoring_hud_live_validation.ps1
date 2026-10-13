param(
    [string]$PythonPath = $env:NEXUS_VALIDATION_PYTHON,
    [string]$ArtifactRoot = "",
    [int]$MarkerTimeoutSeconds = 25,
    [int]$NoProgressTimeoutSeconds = 10,
    [switch]$RunInteractionSelfQA,
    [switch]$VisibleClient,
    [switch]$ActiveUserFacingClient,
    [switch]$RecordingOptionCSelfQA,
    [switch]$Rar3DProof,
    [switch]$Rar3EProof,
    [switch]$SupplementalRuntimeProof,
    [switch]$UserConfirmedACSupplementProof,
    [string]$ExactDesktopShortcutPath = "",
    [int]$InteractionStepDelayMilliseconds = 250,
    [int]$FinalClientHoldSeconds = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$script:RuntimeProcess = $null
$script:RuntimeLauncherProcess = $null
$script:LastProgressAt = Get-Date
$script:LastProgress = "start"
$script:ManifestStatus = "ABORTED"
$script:FailureMessage = ""
$script:ObservedMarkers = New-Object System.Collections.Generic.List[string]
$script:CleanupNotes = New-Object System.Collections.Generic.List[string]
$script:ScreenshotPath = ""
$script:ScreenshotEvidencePath = ""
$script:InteractionManifestStatus = "NOT_REQUESTED"
$script:RestartInteractionManifestStatus = "NOT_REQUESTED"
$script:BeforeScreenshotPath = ""
$script:BeforeScreenshotEvidencePath = ""
$script:ShortVideoProof = [ordered]@{
    status = "NOT_REQUESTED"
    path = ""
    userInspectablePath = ""
    frameCount = 0
    sourceRoot = ""
    proofClass = "short-video-or-frame-sequence"
}
$script:PerElementScreenshotProof = [ordered]@{
    status = "NOT_REQUESTED"
    root = ""
    count = 0
    proofClass = "focused-per-element-screenshot"
    screenshots = @()
}
$script:SupplementalIssueProof = [ordered]@{
    status = "NOT_REQUESTED"
    root = ""
    manifest = ""
    issueFolders = @()
}
$script:ShortcutResolution = [ordered]@{
    path = ""
    targetPath = ""
    workingDirectory = ""
    arguments = ""
    activeRoot = $rootDir
    status = "NOT_TESTED"
    detail = ""
}
$script:LaunchProof = [ordered]@{
    status = "NOT_TESTED"
    proofClass = "exact-user-desktop-shortcut-launch"
    exactDesktopShortcutRequired = $true
    directRuntimeLaunchAllowedForLv1 = $false
    shortcutPath = ""
    shortcutResolution = $script:ShortcutResolution
    runtimeLog = ""
    restartRuntimeLog = ""
    launcherProcessId = 0
    rendererProcessId = 0
}

function Step([object]$Paths, [string]$Message) {
    $script:LastProgressAt = Get-Date
    $script:LastProgress = $Message
    $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $Message
    Add-Content -LiteralPath $Paths.StepLog -Value $line -Encoding utf8
    Write-Output $line
}

function Check-Progress([string]$Activity) {
    if ($NoProgressTimeoutSeconds -gt 0 -and (Get-Date) -gt $script:LastProgressAt.AddSeconds($NoProgressTimeoutSeconds)) {
        throw "No-progress watchdog exceeded during $Activity. Last progress: $script:LastProgress"
    }
}

function Assert-NoSyntheticLiveValidationInteraction {
    param([object]$Paths)

    $rendererPath = Join-Path $rootDir "desktop\desktop_renderer.py"
    if (-not (Test-Path -LiteralPath $rendererPath)) {
        throw "Synthetic-interaction preflight could not inspect renderer path: $rendererPath"
    }
    $rendererText = Get-Content -LiteralPath $rendererPath -Raw
    $startMarker = "def _start_monitoring_hud_live_client_real_os_self_qa"
    $startIndex = $rendererText.IndexOf($startMarker, [StringComparison]::Ordinal)
    if ($startIndex -lt 0) {
        throw "Synthetic-interaction preflight could not find active LV1 self-QA route marker: $startMarker"
    }
    $nextMethodIndex = $rendererText.IndexOf("`n    def ", $startIndex + $startMarker.Length, [StringComparison]::Ordinal)
    if ($nextMethodIndex -lt 0) {
        $routeText = $rendererText.Substring($startIndex)
    }
    else {
        $routeText = $rendererText.Substring($startIndex, $nextMethodIndex - $startIndex)
    }
    $forbiddenPatterns = @(
        @{ Pattern = ".click("; Label = "direct JavaScript click" },
        @{ Pattern = "dispatchEvent(new MouseEvent"; Label = "synthetic DOM mouse event" },
        @{ Pattern = "QTest.mouse"; Label = "QTest widget-only mouse event" },
        @{ Pattern = "handler calls"; Label = "direct handler-call proof" }
    )
    $findings = New-Object System.Collections.Generic.List[string]
    foreach ($entry in $forbiddenPatterns) {
        if ($routeText.Contains([string]$entry.Pattern)) {
            $findings.Add("$($entry.Label): $($entry.Pattern)")
        }
    }
    if ($findings.Count -gt 0) {
        $findingPath = Join-Path $Paths.Root "synthetic_live_validation_interaction_blockers.txt"
        $findings | Set-Content -LiteralPath $findingPath -Encoding utf8
        Step $Paths "blocked LV1 before launch: active route contains synthetic interaction code: $findingPath"
        throw "Live Validation interaction route contains banned synthetic/widget/direct-handler interaction code. STOP and diagnose the real-input failure first; do not edit the validator to use synthetic fallback. Blockers: $($findings -join '; ')"
    }
    Step $Paths "no-synthetic-interaction preflight PASS: active LV1 interaction route contains no JS click, DOM MouseEvent, QTest mouse, or direct-handler interaction proof"
    Step $Paths "real-input fallback policy PASS: if a live click fails, diagnose hit target, z-order, native hit testing, focus, scroll, and runtime state before any validator change; synthetic fallback requires explicit USER waiver"
}

function Resolve-ValidationPython {
    $candidates = @()
    if ($PythonPath) { $candidates += $PythonPath }
    $candidates += "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    $pathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($pathPython -and $pathPython.Source) { $candidates += $pathPython.Source }
    foreach ($candidate in $candidates) {
        if (-not $candidate -or -not (Test-Path -LiteralPath $candidate)) { continue }
        try {
            & $candidate -c "import PySide6" | Out-Null
            if ($LASTEXITCODE -eq 0) { return (Resolve-Path -LiteralPath $candidate).Path }
        } catch {}
    }
    throw "No Qt-capable Python interpreter found."
}

function New-Paths {
    if (-not $ArtifactRoot) {
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
        $ArtifactRoot = Join-Path $rootDir "dev\logs\fam_006_monitoring_hud_live_validation\$stamp"
    }
    New-Item -ItemType Directory -Force -Path $ArtifactRoot | Out-Null
    $artifactLeaf = Split-Path -Leaf $ArtifactRoot
    $userScreenshotsRoot = Join-Path $env:USERPROFILE "OneDrive\Pictures\Screenshots"
    if (-not (Test-Path -LiteralPath $userScreenshotsRoot)) {
        $picturesRoot = [Environment]::GetFolderPath("MyPictures")
        $userScreenshotsRoot = Join-Path $picturesRoot "Screenshots"
    }
    $screenshotEvidenceRoot = Join-Path $userScreenshotsRoot "Nexus Desktop AI\fam_006_monitoring_hud_live_validation\$artifactLeaf"
    $elementScreenshotEvidenceRoot = Join-Path $screenshotEvidenceRoot "focused_element_screenshots"
    New-Item -ItemType Directory -Force -Path $screenshotEvidenceRoot | Out-Null
    New-Item -ItemType Directory -Force -Path $elementScreenshotEvidenceRoot | Out-Null
    [pscustomobject]@{
        Root = $ArtifactRoot
        ScreenshotEvidenceRoot = $screenshotEvidenceRoot
        ElementScreenshotEvidenceRoot = $elementScreenshotEvidenceRoot
        RuntimeLog = Join-Path $ArtifactRoot "runtime_log.txt"
        RestartRuntimeLog = Join-Path $ArtifactRoot "runtime_restart_check_log.txt"
        StdoutLog = Join-Path $ArtifactRoot "stdout.txt"
        StderrLog = Join-Path $ArtifactRoot "stderr.txt"
        RestartStdoutLog = Join-Path $ArtifactRoot "stdout_restart_check.txt"
        RestartStderrLog = Join-Path $ArtifactRoot "stderr_restart_check.txt"
        StepLog = Join-Path $ArtifactRoot "step_log.txt"
        Manifest = Join-Path $ArtifactRoot "manifest.json"
        BeforeScreenshot = Join-Path $ArtifactRoot "monitoring_hud_desktop_before_launch.png"
        BeforeScreenshotEvidence = Join-Path $screenshotEvidenceRoot "monitoring_hud_full_virtual_desktop_before_launch.png"
        Screenshot = Join-Path $ArtifactRoot "monitoring_hud_desktop_after_launch.png"
        ScreenshotEvidence = Join-Path $screenshotEvidenceRoot "monitoring_hud_full_virtual_desktop_after_launch.png"
        InteractionManifest = Join-Path $ArtifactRoot "monitoring_hud_live_client_interaction_manifest.json"
        InteractionEvidenceRoot = Join-Path $ArtifactRoot "live_client_interaction"
        RestartInteractionManifest = Join-Path $ArtifactRoot "monitoring_hud_restart_check_interaction_manifest.json"
        RestartInteractionEvidenceRoot = Join-Path $ArtifactRoot "restart_check_interaction"
        ShortVideoFrameRoot = Join-Path $ArtifactRoot "short_video_frames"
        ShortVideo = Join-Path $ArtifactRoot "monitoring_hud_lv1_short_video.mp4"
        ShortVideoEvidence = Join-Path $screenshotEvidenceRoot "monitoring_hud_lv1_short_video.mp4"
        AbortSignal = Join-Path $ArtifactRoot "startup_abort.signal"
    }
}

function ConvertTo-SafeScreenshotName([string]$Value) {
    $safe = ($Value -replace "[^A-Za-z0-9_-]", "_").Trim("_")
    if ([string]::IsNullOrWhiteSpace($safe)) {
        return "unnamed_element"
    }
    return $safe.ToLowerInvariant()
}

function Get-HudIssueIdsForElementLabel {
    param([string]$ElementName)
    $lowerName = $ElementName.ToLowerInvariant()
    $matches = New-Object System.Collections.Generic.List[string]
    $issueRules = [ordered]@{
        "UTS-HUD-001" = @("button", "glow", "close", "settings", "profile", "manage", "create", "edit", "save", "discard", "delete", "cancel")
        "UTS-HUD-002" = @("background", "grid", "card", "window", "panel")
        "UTS-HUD-003" = @("button", "selector", "dropdown")
        "UTS-HUD-004" = @("warning", "discard", "delete", "cancel", "hover")
        "UTS-HUD-005" = @("button", "create", "selector", "dropdown")
        "UTS-HUD-006" = @("source_row", "source-picker", "source_picker", "checked")
        "UTS-HUD-007" = @("filter", "dropdown", "max_five")
        "UTS-HUD-008" = @("source_row", "source-picker", "source_picker", "hover")
        "UTS-HUD-009" = @("polling", "rate")
        "UTS-HUD-010" = @("source_settings", "display_mode", "warning_checkbox")
        "UTS-HUD-011" = @("dashboard", "data_sources", "manage_monitors")
        "UTS-HUD-012" = @("unsaved", "guard", "discard", "save")
        "UTS-HUD-013" = @("dashboard", "overlay", "manage", "source", "scrollbar", "divider", "button", "recording")
        "UTS-HUD-014" = @("overlay_profile", "clean", "selector", "choice_panel", "create", "dirty", "guard", "save", "discard", "delete", "profile_to_edit")
        "UTS-HUD-015" = @("scrollbar")
        "UTS-HUD-016" = @("divider", "page_break")
        "UTS-HUD-017" = @("button", "glow", "color", "uniform", "recording")
        "UTS-HUD-018" = @("row_title", "row-title", "page_break", "divider", "tab")
        "UTS-HUD-019" = @("state_stability", "surface_stability", "group_switch", "responsive_window", "window_contract", "open_state", "window_create_clean", "window_display_mode_buttons")
        "UTS-HUD-020" = @("source_settings", "shift", "focus", "gold", "warning")
        "UTS-HUD-021" = @("scalability", "window_size", "minimum", "responsive", "scale", "compact", "normal", "overlay_profile", "recording")
    }
    foreach ($issueId in $issueRules.Keys) {
        foreach ($keyword in $issueRules[$issueId]) {
            if ($lowerName.Contains($keyword)) {
                $matches.Add($issueId)
                break
            }
        }
    }
    if ($matches.Count -eq 0) {
        $matches.Add("UTS-HUD-013")
    }
    return @($matches)
}

function Copy-FocusedElementScreenshotsToUserEvidence {
    param(
        [object]$Paths,
        [int]$MinimumScreenshots = 48,
        [string]$FocusedLane = "full"
    )

    $contextNames = @(
        "initial_live_client_visible",
        "dashboard_standalone_virtual_desktop_travel",
        "final_anchored_live_client",
        "full_virtual_desktop",
        "desktop_before_launch",
        "desktop_after_launch"
    )

    if (-not (Test-Path -LiteralPath $Paths.InteractionEvidenceRoot)) {
        return [ordered]@{
            status = "FAIL"
            root = $Paths.ElementScreenshotEvidenceRoot
            count = 0
            reason = "interaction evidence root missing; LV1 focused per-element screenshots missing"
            proofClass = "focused-per-element-screenshot"
            screenshots = @()
        }
    }

    New-Item -ItemType Directory -Force -Path $Paths.ElementScreenshotEvidenceRoot | Out-Null
    $screenshots = @()
    $pngs = @(Get-ChildItem -LiteralPath $Paths.InteractionEvidenceRoot -Filter "*.png" -File | Sort-Object Name)
    foreach ($png in $pngs) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($png.Name)
        $lowerName = $baseName.ToLowerInvariant()
        $isContext = $false
        foreach ($context in $contextNames) {
            if ($lowerName.Contains($context)) {
                $isContext = $true
                break
            }
        }
        if ($isContext) { continue }

        $elementName = ConvertTo-SafeScreenshotName $baseName
        $destinationName = "element_{0}.png" -f $elementName
        $destination = Join-Path $Paths.ElementScreenshotEvidenceRoot $destinationName
        Copy-Item -LiteralPath $png.FullName -Destination $destination -Force
        $issueIds = @(Get-HudIssueIdsForElementLabel -ElementName $elementName)
        $screenshots += [pscustomobject]@{
            elementLabel = $elementName
            stateOrAction = $baseName
            proofClass = "focused-per-element-screenshot"
            issueIds = $issueIds
            sourcePath = $png.FullName
            userInspectablePath = $destination
        }
    }

    $allIssueIds = @(
        "UTS-HUD-001", "UTS-HUD-002", "UTS-HUD-003", "UTS-HUD-004", "UTS-HUD-005", "UTS-HUD-006",
        "UTS-HUD-007", "UTS-HUD-008", "UTS-HUD-009", "UTS-HUD-010", "UTS-HUD-011", "UTS-HUD-012",
        "UTS-HUD-013", "UTS-HUD-014", "UTS-HUD-015", "UTS-HUD-016", "UTS-HUD-017",
        "UTS-HUD-018", "UTS-HUD-019", "UTS-HUD-020", "UTS-HUD-021"
    )
    if ($FocusedLane -eq "recording-option-c") {
        $allIssueIds = @()
        $MinimumScreenshots = [Math]::Max(12, [Math]::Min($MinimumScreenshots, 12))
    } elseif ($FocusedLane -eq "recording-option-c-rar3d") {
        $allIssueIds = @()
        $MinimumScreenshots = [Math]::Max(18, [Math]::Min($MinimumScreenshots, 18))
    } elseif ($FocusedLane -eq "recording-option-c-rar3e") {
        $allIssueIds = @()
        $MinimumScreenshots = [Math]::Max(28, [Math]::Min($MinimumScreenshots, 28))
    }
    $issueCoverage = @()
    foreach ($issueId in $allIssueIds) {
        $covered = @($screenshots | Where-Object { @($_.issueIds) -contains $issueId })
        $issueCoverage += [pscustomobject]@{
            issueId = $issueId
            status = if ($covered.Count -gt 0) { "PASS" } else { "FAIL" }
            screenshotCount = [int]$covered.Count
            screenshots = @($covered | Select-Object -ExpandProperty userInspectablePath)
        }
    }
    $missingIssueCoverage = @($issueCoverage | Where-Object { $_.status -ne "PASS" })
    $requiredElementLabels = @(
        "unsaved_guard_save_discard_buttons_visible",
        "unsaved_guard_discard_red_danger_button",
        "unsaved_guard_panel_background_no_grid_bleed",
        "dirty_guard_close_button_functionality",
        "manage_monitors_dirty_guard_save_discard_cancel_modal",
        "manage_monitors_dirty_guard_modal_uniform_with_overlay_profile",
        "manage_monitors_dirty_guard_background_blur_blocking",
        "manage_monitors_dirty_guard_close_button_functionality",
        "manage_monitors_create_after_delete_reuses_monitor_group_number",
        "manage_monitors_recreated_monitor_group_3_dirty_draft",
        "02_recording_card_target_status_visual_contract",
        "02_recording_card_target_preview_standard_state_rows",
        "02_dashboard_quick_access_start_stop_ready_state",
        "02_recording_card_log_viewer_studio_pre_session_ready_state",
        "02_recording_studio_native_window_ready_state",
        "02_recording_card_log_viewer_studio_requested_state",
        "02_log_viewer_studio_native_window_shell_state",
        "02_recording_card_log_viewer_studio_opened_state"
    )
    if ($FocusedLane -eq "recording-option-c") {
        $requiredElementLabels = @(
            "02_recording_card_target_status_visual_contract",
            "02_recording_card_target_preview_standard_state_rows",
            "02_dashboard_quick_access_start_stop_ready_state",
            "02_recording_card_log_viewer_studio_pre_session_ready_state",
            "03_manage_monitors_open_state",
            "02_recording_studio_native_window_ready_state",
            "02_dashboard_quick_access_recording_active_state",
            "02_dashboard_quick_access_stop_saved_request_state",
            "02_recording_card_saved_complete_readback_state",
            "02_recording_studio_native_log_saved_tracking_state",
            "02_recording_card_log_viewer_studio_requested_state",
            "02_log_viewer_studio_native_window_shell_state",
            "02_recording_card_log_viewer_studio_opened_state",
            "02_log_viewer_c1_closed_before_start_stop",
            "02_log_viewer_c1_recording_active_state",
            "02_log_viewer_c1_stop_saved_request_state",
            "02_log_viewer_c1_closed_after_start_stop",
            "02_log_viewer_c2_minimized_before_start_stop",
            "02_log_viewer_c2_recording_active_state",
            "02_log_viewer_c2_stop_saved_request_state",
            "02_log_viewer_c2_minimized_after_start_stop",
            "02_log_viewer_c3_open_unfocused_before_start_stop",
            "02_log_viewer_c3_shell_open_unfocused_before_start_stop",
            "02_log_viewer_c3_recording_active_state",
            "02_log_viewer_c3_stop_saved_request_state",
            "02_log_viewer_c3_open_unfocused_after_start_stop",
            "02_log_viewer_c3_shell_open_unfocused_after_start_stop",
            "02_native_proof_windows_closed_before_overlay_profile_selector",
            "02_hud_overlay_active_profile_selector_real_os_selected",
            "02_recording_card_mirrors_hud_overlay_active_profile_real_os_selection",
            "02_recording_option_c_focused_lane_complete"
        )
    } elseif ($FocusedLane -eq "recording-option-c-rar3d") {
        $requiredElementLabels = @(
            "rar3d_rar2b-fam006-003_hud_close_hover",
            "rar3d_rar2b-fam006-003_hud_close_focus",
            "rar3d_rar2b-fam006-013_quick_access_default",
            "rar3d_rar2b-fam006-013_quick_access_hover",
            "rar3d_rar2b-fam006-013_quick_access_pressed",
            "rar3d_rar2b-fam006-018_recording_studio_default",
            "rar3d_rar2b-fam006-018_recording_studio_hover",
            "rar3d_rar2b-fam006-018_recording_studio_pressed",
            "rar3d_rar2b-fam006-019_open_native_logs_default",
            "rar3d_rar2b-fam006-019_open_native_logs_hover",
            "rar3d_rar2b-fam006-019_open_native_logs_pressed",
            "rar3d_rar2b-fam006-019_open_exported_logs_default",
            "rar3d_rar2b-fam006-019_open_exported_logs_hover",
            "rar3d_rar2b-fam006-019_open_exported_logs_pressed",
            "rar3d_rar2b-fam006-016_recording_studio_geometry_original",
            "rar3d_rar2b-fam006-016_recording_studio_geometry_moved",
            "rar3d_rar2b-fam006-021_log_viewer_studio_geometry_original",
            "rar3d_rar2b-fam006-021_log_viewer_studio_geometry_moved"
        )
    } elseif ($FocusedLane -eq "recording-option-c-rar3e") {
        $requiredElementLabels = @(
            "rar3e_rar2b-fam006-004_dashboard_geometry_original",
            "rar3e_rar2b-fam006-004_dashboard_geometry_moved",
            "rar3e_rar2b-fam006-004_dashboard_geometry_closed",
            "rar3e_rar2b-fam006-004_dashboard_geometry_reopened",
            "rar3e_rar2b-fam006-003_hud_close_keyboard_focus",
            "rar3e_rar2b-fam006-003_hud_close_keyboard_after",
            "rar3e_rar2b-fam006-007_quick_access_default",
            "rar3e_rar2b-fam006-007_quick_access_hover",
            "rar3e_rar2b-fam006-007_quick_access_start_keyboard_focus",
            "rar3e_rar2b-fam006-007_quick_access_start_keyboard_after",
            "rar3e_rar2b-fam006-007_quick_access_recording_active",
            "rar3e_rar2b-fam006-007_quick_access_stop_keyboard_focus",
            "rar3e_rar2b-fam006-007_quick_access_stop_keyboard_after",
            "rar3e_rar2b-fam006-010_recording_card_buttons_default",
            "rar3e_rar2b-fam006-010_recording_card_studio_hover",
            "rar3e_rar2b-fam006-010_recording_card_studio_button_keyboard_focus",
            "rar3e_rar2b-fam006-010_recording_card_studio_button_keyboard_after",
            "rar3e_rar2b-fam006-010_recording_card_log_viewer_hover",
            "rar3e_rar2b-fam006-010_recording_card_log_viewer_button_keyboard_focus",
            "rar3e_rar2b-fam006-010_recording_card_log_viewer_button_keyboard_after",
            "rar3e_rar2b-fam006-014_recording_studio_start_before_activation",
            "rar3e_rar2b-fam006-014_recording_studio_start_after_activation",
            "rar3e_rar2b-fam006-014_recording_studio_stop_before_activation",
            "rar3e_rar2b-fam006-014_recording_studio_stop_after_activation",
            "rar3e_rar2b-fam006-014_recording_studio_start_keyboard_focus",
            "rar3e_rar2b-fam006-014_recording_studio_start_keyboard_after",
            "rar3e_rar2b-fam006-014_recording_studio_stop_keyboard_focus",
            "rar3e_rar2b-fam006-014_recording_studio_stop_keyboard_after",
            "rar3e_rar2b-fam006-019_open_native_logs_before_activation",
            "rar3e_rar2b-fam006-019_open_native_logs_after_activation",
            "rar3e_rar2b-fam006-019_open_exported_logs_before_activation",
            "rar3e_rar2b-fam006-019_open_exported_logs_after_activation",
            "rar3e_rar2b-fam006-016_recording_studio_real_drag_original",
            "rar3e_rar2b-fam006-016_recording_studio_real_drag_moved",
            "rar3e_rar2b-fam006-016_recording_studio_real_drag_reopened",
            "rar3e_rar2b-fam006-021_log_viewer_studio_real_drag_original",
            "rar3e_rar2b-fam006-021_log_viewer_studio_real_drag_moved",
            "rar3e_rar2b-fam006-021_log_viewer_studio_real_drag_reopened",
            "rar3e_context_dashboard_after_remaining_proof"
        )
    }
    $availableElementLabels = @($screenshots | Select-Object -ExpandProperty elementLabel)
    $missingRequiredElementLabels = @($requiredElementLabels | Where-Object { $availableElementLabels -notcontains $_ })

    if ($screenshots.Count -lt $MinimumScreenshots) {
        return [ordered]@{
            status = "FAIL"
            root = $Paths.ElementScreenshotEvidenceRoot
            count = $screenshots.Count
            reason = "only $($screenshots.Count) focused per-element screenshot(s) copied; minimum is $MinimumScreenshots"
            proofClass = "focused-per-element-screenshot"
            perElementVisualInventory = $screenshots
            issueFormCoverageMatrix = $issueCoverage
            screenshots = $screenshots
        }
    }

    if ($missingRequiredElementLabels.Count -gt 0) {
        return [ordered]@{
            status = "FAIL"
            root = $Paths.ElementScreenshotEvidenceRoot
            count = $screenshots.Count
            reason = "focused screenshots missing mandatory dirty-guard parity element(s): $($missingRequiredElementLabels -join ', ')"
            proofClass = "focused-per-element-screenshot"
            perElementVisualInventory = $screenshots
            issueFormCoverageMatrix = $issueCoverage
            screenshots = $screenshots
        }
    }

    if ($FocusedLane -notin @("recording-option-c", "recording-option-c-rar3d", "recording-option-c-rar3e") -and $missingIssueCoverage.Count -gt 0) {
        return [ordered]@{
            status = "FAIL"
            root = $Paths.ElementScreenshotEvidenceRoot
            count = $screenshots.Count
            reason = "focused screenshots missing issue-form coverage for: $(@($missingIssueCoverage | Select-Object -ExpandProperty issueId) -join ', ')"
            proofClass = "focused-per-element-screenshot"
            perElementVisualInventory = $screenshots
            issueFormCoverageMatrix = $issueCoverage
            screenshots = $screenshots
        }
    }

    [ordered]@{
        status = "PASS"
        root = $Paths.ElementScreenshotEvidenceRoot
        count = $screenshots.Count
        reason = "focused UI screenshots were copied to the USER-inspectable OneDrive screenshots folder with element labels in each filename and mapped to the returned UTS issue form"
        proofClass = "focused-per-element-screenshot"
        perElementVisualInventory = $screenshots
        issueFormCoverageMatrix = $issueCoverage
        screenshots = $screenshots
    }
}

function Copy-SupplementalIssueScreenshotsToUserEvidence {
    param(
        [object]$Paths,
        [string[]]$IssueFilter = @(),
        [string]$ProofClass = "supplemental-runtime-proof-gap-investigation"
    )

    $issueRules = @(
        [pscustomobject]@{
            issueId = "A"
            folder = "A_Recording_Studio_Button_Click"
            expected = "Clicking the visible Dashboard Recording Card Recording Studio button opens the standalone Recording Studio window."
            observed = "Current return-flow proof must include the normal visible Dashboard Recording Card button path, event proof, bridge proof, and focused native Recording Studio screenshot."
            confidence = "Runtime return-flow proof when the interaction manifest includes real OS click and focused native-window screenshot evidence."
            patterns = @("02_recording_studio_native_window_ready_state", "02_recording_card_target_status_visual_contract")
        },
        [pscustomobject]@{
            issueId = "B"
            folder = "B_Start_Stop_Quick_Access_Placement"
            expected = "Accepted current repair scope keeps active Start/Stop in Dashboard Quick Access while the Recording card remains target/status summary."
            observed = "Screenshot evidence captures the repaired Dashboard Quick Access Start/Stop placement and the Recording card summary surface."
            confidence = "Verified source-truth comparison and repaired UI placement."
            patterns = @("02_dashboard_quick_access_start_stop_ready_state", "02_dashboard_quick_access_recording_active_state")
        },
        [pscustomobject]@{
            issueId = "C"
            folder = "C_Log_Viewer_Focus_Open_Regression"
            expected = "Opening/closing/minimizing Log Viewer should not make every later start/stop steal focus unless source truth requires it."
            observed = "Current return-flow proof must include C1 closed, C2 minimized, and C3 open-unfocused Start/Stop sequences with real OS Quick Access clicks and native focus/window state evidence."
            confidence = "Runtime return-flow proof when all C1/C2/C3 interaction-manifest steps pass with pre/post screenshots."
            patterns = @(
                "02_log_viewer_studio_native_window_shell_state",
                "02_recording_card_log_viewer_studio_opened_state",
                "02_log_viewer_c1_closed_before_start_stop",
                "02_log_viewer_c1_closed_after_start_stop",
                "02_log_viewer_c2_minimized_before_start_stop",
                "02_log_viewer_c2_minimized_after_start_stop",
                "02_log_viewer_c3_open_unfocused_before_start_stop",
                "02_log_viewer_c3_open_unfocused_after_start_stop"
            )
        },
        [pscustomobject]@{
            issueId = "D"
            folder = "D_Log_Viewer_Recording_Studio_Ownership"
            expected = "Recording Studio and Log Viewer ownership boundaries should match accepted source truth; USER now says native log tracking belongs in Recording Studio and Log Viewer should stay shell/export oriented."
            observed = "Screenshots capture Recording Studio ready and saved-native-log tracking states plus Log Viewer shell-only boundaries for ownership comparison."
            confidence = "Runtime proof when the saved-native-log tracking and shell-only screenshots are present."
            patterns = @("02_recording_studio_native_window_ready_state", "02_recording_studio_native_log_saved_tracking_state", "02_log_viewer_studio_native_window_shell_state")
        },
        [pscustomobject]@{
            issueId = "E"
            folder = "E_Manual_Overlay_Profile_Normal_Path"
            expected = "Overlay Profile create/edit/switch/restart should work through normal USER paths and keep Recording target mirrored."
            observed = "Current return-flow proof must include seeded selector mirroring, normal create/edit/save/switch path, and fresh-runtime restart persistence proof before E can turn green."
            confidence = "Runtime return-flow proof when all normal-path and restart interaction-manifest steps pass with focused screenshots."
            patterns = @(
                "02_hud_overlay_active_profile_selector_real_os_selected",
                "02_recording_card_mirrors_hud_overlay_active_profile_real_os_selection",
                "02_overlay_profile_normal_path_created_draft_recording_mirror",
                "02_overlay_profile_normal_path_saved_recording_mirror",
                "02_overlay_profile_normal_path_switch_saved_recording_mirror",
                "02_overlay_profile_restart_persistence_recording_target_mirror"
            )
        },
        [pscustomobject]@{
            issueId = "F"
            folder = "F_Dashboard_Card_Holder_Visual_State"
            expected = "Dashboard card holder should keep equal left/right card insets with scrollbar gutter exempt from visual offset."
            observed = "Focused Recording card screenshots exist, but equal-inset visual adjudication is not measured by this helper."
            confidence = "Inferred/needs product visual adjudication."
            patterns = @("02_recording_card_target_status_visual_contract", "02_recording_card_saved_complete_readback_state")
        }
    )

    $issueResults = @()
    foreach ($issue in $issueRules) {
        if ($IssueFilter.Count -gt 0 -and -not ($IssueFilter -contains $issue.issueId)) {
            continue
        }
        $folderPath = Join-Path $Paths.ScreenshotEvidenceRoot $issue.folder
        New-Item -ItemType Directory -Force -Path $folderPath | Out-Null
        $copied = @()
        foreach ($pattern in $issue.patterns) {
            $matches = @(Get-ChildItem -LiteralPath $Paths.ElementScreenshotEvidenceRoot -Filter "*.png" -File -ErrorAction SilentlyContinue | Where-Object {
                $_.BaseName.ToLowerInvariant().Contains($pattern.ToLowerInvariant())
            })
            foreach ($match in $matches) {
                $destination = Join-Path $folderPath $match.Name
                Copy-Item -LiteralPath $match.FullName -Destination $destination -Force
                $copied += $destination
            }
        }
        $issueResults += [pscustomobject]@{
            issueId = $issue.issueId
            folder = $folderPath
            expected = $issue.expected
            observed = $issue.observed
            confidence = $issue.confidence
            screenshotCount = [int]$copied.Count
            screenshots = @($copied)
        }
    }

    $manifestPath = Join-Path $Paths.ScreenshotEvidenceRoot "supplemental_issue_evidence_manifest.json"
    $manifest = [ordered]@{
        status = "SUPPLEMENTAL_INVESTIGATION_EVIDENCE"
        proofClass = $ProofClass
        root = $Paths.ScreenshotEvidenceRoot
        interactionManifest = $Paths.InteractionManifest
        generatedAt = (Get-Date).ToUniversalTime().ToString("o")
        noRetroactiveEvidenceLaundering = $true
        helperPathAndUserPathSeparated = $true
        normalUserAutomationStatus = "Blocked when Computer Use native pipe path is unavailable; USER-confirmed findings are not disproven by helper proof."
        issueFolders = $issueResults
    }
    $manifest | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $manifestPath -Encoding utf8
    [ordered]@{
        status = "PASS"
        root = $Paths.ScreenshotEvidenceRoot
        manifest = $manifestPath
        issueFolders = $issueResults
    }
}

function Marker-Count([object]$Paths, [string]$Pattern) {
    if (-not (Test-Path -LiteralPath $Paths.RuntimeLog)) { return 0 }
    @(Select-String -LiteralPath $Paths.RuntimeLog -Pattern $Pattern -SimpleMatch).Count
}

function Wait-Marker([object]$Paths, [string]$Pattern) {
    $deadline = (Get-Date).AddSeconds($MarkerTimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $count = Marker-Count $Paths $Pattern
        if ($count -gt 0) {
            $script:ObservedMarkers.Add($Pattern)
            Step $Paths "observed marker: $Pattern count=$count"
            return
        }
        if ($script:RuntimeProcess -and $script:RuntimeProcess.HasExited) {
            throw "Runtime exited before marker appeared: $Pattern"
        }
        Check-Progress "waiting for marker $Pattern"
        Start-Sleep -Milliseconds 250
    }
    throw "Timed out waiting for marker: $Pattern"
}

function Wait-JsonManifestStatus([object]$Paths, [string]$ManifestPath, [object]$Process, [string]$Label) {
    $deadline = (Get-Date).AddSeconds($MarkerTimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $ManifestPath) {
            try {
                $raw = Get-Content -LiteralPath $ManifestPath -Raw
                $manifest = $raw | ConvertFrom-Json
                $status = ""
                if ($manifest -and ($manifest.PSObject.Properties.Name -contains "status")) {
                    $status = [string]$manifest.status
                }
                if (-not [string]::IsNullOrWhiteSpace($status)) {
                    Step $Paths "$Label manifest status: $status"
                    return [pscustomobject]@{
                        status = $status
                        raw = $raw
                        manifest = $manifest
                    }
                }
            }
            catch {
                Step $Paths "$Label manifest parse pending: $($_.Exception.Message)"
            }
        }
        if ($Process -and $Process.HasExited -and -not (Test-Path -LiteralPath $ManifestPath)) {
            throw "$Label process exited before manifest appeared: $ManifestPath"
        }
        Check-Progress "waiting for $Label manifest"
        Start-Sleep -Milliseconds 250
    }
    throw "Timed out waiting for $Label manifest: $ManifestPath"
}

function Stop-TrackedDesktopRuntime {
    param(
        [object]$Paths,
        [string]$Reason
    )

    if ($script:RuntimeLauncherProcess) {
        try {
            if (-not $script:RuntimeLauncherProcess.HasExited) {
                Stop-Process -Id $script:RuntimeLauncherProcess.Id -Force -ErrorAction Stop
                $script:CleanupNotes.Add("Stopped desktop launcher pid=$($script:RuntimeLauncherProcess.Id) during $Reason")
                Step $Paths "stopped desktop launcher during $Reason pid=$($script:RuntimeLauncherProcess.Id)"
            }
            else {
                $script:CleanupNotes.Add("Desktop launcher exited before $Reason pid=$($script:RuntimeLauncherProcess.Id)")
            }
        }
        catch {
            $script:CleanupNotes.Add("Cleanup failed for desktop launcher pid=$($script:RuntimeLauncherProcess.Id): $($_.Exception.Message)")
        }
        $script:RuntimeLauncherProcess = $null
    }

    if ($script:RuntimeProcess) {
        try {
            if (-not $script:RuntimeProcess.HasExited) {
                Stop-Process -Id $script:RuntimeProcess.Id -Force -ErrorAction Stop
                $script:CleanupNotes.Add("Stopped desktop renderer pid=$($script:RuntimeProcess.Id) during $Reason")
                Step $Paths "stopped desktop renderer during $Reason pid=$($script:RuntimeProcess.Id)"
            }
            else {
                $script:CleanupNotes.Add("Desktop renderer exited before $Reason pid=$($script:RuntimeProcess.Id)")
            }
        }
        catch {
            $script:CleanupNotes.Add("Cleanup failed for desktop renderer pid=$($script:RuntimeProcess.Id): $($_.Exception.Message)")
        }
        $script:RuntimeProcess = $null
    }
}

function Run-RestartInteractionSelfQA([object]$Paths, [string]$ShortcutPath, [int]$StepDelayMs, [int]$FinalHoldMs) {
    $previousRuntimeLog = [string]$Paths.RuntimeLog
    $previousRendererPid = 0
    if ($script:RuntimeProcess) {
        try {
            $previousRendererPid = [int]$script:RuntimeProcess.Id
        }
        catch {
            $previousRendererPid = 0
        }
    }
    if (($script:RuntimeProcess -and -not $script:RuntimeProcess.HasExited) -or
        ($script:RuntimeLauncherProcess -and -not $script:RuntimeLauncherProcess.HasExited)) {
        Start-Sleep -Milliseconds 1200
        Stop-TrackedDesktopRuntime $Paths "restart persistence check"
        Start-Sleep -Milliseconds 1500
    }

    New-Item -ItemType Directory -Force -Path $Paths.RestartInteractionEvidenceRoot | Out-Null
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_MANIFEST = $Paths.RestartInteractionManifest
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_ROOT = $Paths.RestartInteractionEvidenceRoot
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_STEP_DELAY_MS = [string]$StepDelayMs
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_FINAL_HOLD_MS = [string]$FinalHoldMs
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_LANE = "recording-option-c-restart-check"
    $env:NEXUS_HARNESS_LOG_ROOT = $Paths.Root
    $env:NEXUS_HARNESS_DISABLE_DIAGNOSTICS = "1"
    $env:NEXUS_HARNESS_DISABLE_VOICE = "1"
    $env:NEXUS_HARNESS_AUTO_ACCEPT_RELAUNCH = "1"
    $env:NEXUS_HARNESS_SUPPRESS_ALREADY_RUNNING_DIALOGS = "1"
    $env:NEXUS_HARNESS_RELAUNCH_WAIT_SECONDS = "20"

    $script:RestartInteractionManifestStatus = "PENDING"
    $restartLaunch = Start-ExactDesktopShortcutRuntime -Paths $Paths -ShortcutPath $ShortcutPath -Label "restart persistence" -ExcludedRuntimeLogs @($previousRuntimeLog) -ExcludedRendererProcessIds @($previousRendererPid) | Select-Object -Last 1
    $script:RuntimeProcess = $restartLaunch.process
    $script:RuntimeLauncherProcess = $restartLaunch.launcherProcess
    $Paths.RestartRuntimeLog = $restartLaunch.runtimeLog
    Step $Paths "launched restart persistence through exact USER Desktop shortcut pid=$($script:RuntimeProcess.Id)"
    $result = Wait-JsonManifestStatus $Paths $Paths.RestartInteractionManifest $script:RuntimeProcess "restart interaction self-QA" | Select-Object -Last 1
    $script:RestartInteractionManifestStatus = [string]$result.status
    if ($script:RestartInteractionManifestStatus -ne "PASS") {
        throw "Restart interaction self-QA did not pass. Status: $script:RestartInteractionManifestStatus"
    }
    if ($result.raw -notmatch [regex]::Escape("Restart check reloads saved USER Overlay Profile and Recording target mirror")) {
        throw "Restart interaction self-QA missing required Overlay Profile persistence proof label."
    }
    if ($result.raw -match '"directJsClickUsed"\s*:\s*true' -or
        $result.raw -notmatch '"realOsInputProof"\s*:\s*true') {
        throw "Restart interaction self-QA lacks required proof boundary or contains forbidden direct JS click proof."
    }
    $restartScreenshots = @(Get-ChildItem -LiteralPath $Paths.RestartInteractionEvidenceRoot -Filter "*.png" -File -ErrorAction SilentlyContinue)
    foreach ($png in $restartScreenshots) {
        Copy-Item -LiteralPath $png.FullName -Destination (Join-Path $Paths.InteractionEvidenceRoot $png.Name) -Force
    }
    Step $Paths "restart interaction self-QA manifest PASS: $($Paths.RestartInteractionManifest)"
}

function Capture-Screen([object]$Paths, [string]$Label = "after_launch") {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $screens = [System.Windows.Forms.Screen]::AllScreens
    $bounds = [System.Drawing.Rectangle]::Empty
    foreach ($screen in $screens) {
        if ($bounds.IsEmpty) {
            $bounds = $screen.Bounds
        }
        else {
            $bounds = [System.Drawing.Rectangle]::Union($bounds, $screen.Bounds)
        }
    }
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        if ($Label -eq "before_launch") {
            $bitmap.Save($Paths.BeforeScreenshot, [System.Drawing.Imaging.ImageFormat]::Png)
            Copy-Item -LiteralPath $Paths.BeforeScreenshot -Destination $Paths.BeforeScreenshotEvidence -Force
            $script:BeforeScreenshotPath = $Paths.BeforeScreenshot
            $script:BeforeScreenshotEvidencePath = $Paths.BeforeScreenshotEvidence
            Step $Paths "captured before-launch full virtual desktop screenshot: $($Paths.BeforeScreenshot)"
            Step $Paths "copied before-launch user-inspectable screenshot evidence: $($Paths.BeforeScreenshotEvidence)"
        }
        else {
            $bitmap.Save($Paths.Screenshot, [System.Drawing.Imaging.ImageFormat]::Png)
            Copy-Item -LiteralPath $Paths.Screenshot -Destination $Paths.ScreenshotEvidence -Force
            $script:ScreenshotPath = $Paths.Screenshot
            $script:ScreenshotEvidencePath = $Paths.ScreenshotEvidence
            Step $Paths "captured after-launch full virtual desktop screenshot: $($Paths.Screenshot)"
            Step $Paths "copied after-launch user-inspectable screenshot evidence: $($Paths.ScreenshotEvidence)"
        }
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

function Get-PngInfo([string]$Path) {
    Add-Type -AssemblyName System.Drawing
    $image = [System.Drawing.Image]::FromFile($Path)
    try {
        [pscustomobject]@{
            Path = (Resolve-Path -LiteralPath $Path).Path
            Width = [int]$image.Width
            Height = [int]$image.Height
            Area = [int]($image.Width * $image.Height)
        }
    }
    finally {
        $image.Dispose()
    }
}

function New-ShortVideoProof {
    param(
        [object]$Paths,
        [string[]]$SourceRoots,
        [int]$MinimumFrames = 5
    )

    $ffmpeg = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
    if (-not $ffmpeg -or -not $ffmpeg.Source) {
        return [ordered]@{
            status = "FAIL"
            reason = "ffmpeg.exe unavailable; LV1 requires durable short video or ordered frame-sequence proof"
            path = ""
            userInspectablePath = ""
            frameCount = 0
            sourceRoot = ""
            proofClass = "short-video-or-frame-sequence"
        }
    }

    $pngs = @()
    foreach ($root in $SourceRoots) {
        if ($root -and (Test-Path -LiteralPath $root)) {
            $pngs += @(Get-ChildItem -LiteralPath $root -Filter "*.png" -File | Sort-Object FullName)
        }
    }
    if ($pngs.Count -lt 2) {
        return [ordered]@{
            status = "FAIL"
            reason = "fewer than two PNG frames available for short video proof"
            path = ""
            userInspectablePath = ""
            frameCount = [int]$pngs.Count
            sourceRoot = ($SourceRoots -join ";")
            proofClass = "short-video-or-frame-sequence"
        }
    }

    $infos = @()
    foreach ($png in $pngs) {
        try { $infos += @(Get-PngInfo -Path $png.FullName) } catch {}
    }
    $groups = @($infos | Group-Object { "$($_.Width)x$($_.Height)" } | Sort-Object @{ Expression = { $_.Count }; Descending = $true }, @{ Expression = { ($_.Group | Select-Object -First 1).Area }; Descending = $true })
    $selectedGroup = $groups | Where-Object { $_.Count -ge $MinimumFrames } | Select-Object -First 1
    if (-not $selectedGroup) {
        $selectedGroup = $groups | Where-Object { $_.Count -ge 2 } | Select-Object -First 1
    }
    if (-not $selectedGroup) {
        return [ordered]@{
            status = "FAIL"
            reason = "no same-size PNG frame group was large enough for ffmpeg video proof"
            path = ""
            userInspectablePath = ""
            frameCount = 0
            sourceRoot = ($SourceRoots -join ";")
            proofClass = "short-video-or-frame-sequence"
        }
    }

    Remove-Item -LiteralPath $Paths.ShortVideoFrameRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $Paths.ShortVideoFrameRoot | Out-Null
    $index = 1
    foreach ($frame in @($selectedGroup.Group | Sort-Object Path)) {
        Copy-Item -LiteralPath $frame.Path -Destination (Join-Path $Paths.ShortVideoFrameRoot ("frame_{0:0000}.png" -f $index)) -Force
        $index += 1
    }

    & $ffmpeg.Source -y -loglevel error -framerate 2 -i (Join-Path $Paths.ShortVideoFrameRoot "frame_%04d.png") -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -movflags +faststart $Paths.ShortVideo
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Paths.ShortVideo)) {
        return [ordered]@{
            status = "FAIL"
            reason = "ffmpeg failed to encode LV1 short video proof"
            path = $Paths.ShortVideo
            userInspectablePath = ""
            frameCount = [int]$selectedGroup.Count
            sourceRoot = ($SourceRoots -join ";")
            proofClass = "short-video-or-frame-sequence"
        }
    }

    Copy-Item -LiteralPath $Paths.ShortVideo -Destination $Paths.ShortVideoEvidence -Force
    [ordered]@{
        status = "PASS"
        reason = "durable LV1 short video proof generated from ordered same-size screenshot frames"
        path = $Paths.ShortVideo
        userInspectablePath = $Paths.ShortVideoEvidence
        frameCount = [int]$selectedGroup.Count
        sourceRoot = ($SourceRoots -join ";")
        proofClass = "short-video-or-frame-sequence"
        ffmpeg = $ffmpeg.Source
        frameRoot = $Paths.ShortVideoFrameRoot
    }
}

function Save-Manifest([object]$Paths, [string]$PythonExe) {
    $observedMarkers = @($script:ObservedMarkers)
    $interactionRaw = ""
    if (Test-Path -LiteralPath $Paths.InteractionManifest) {
        $interactionRaw = Get-Content -LiteralPath $Paths.InteractionManifest -Raw
    }
    $restartInteractionRaw = ""
    if (Test-Path -LiteralPath $Paths.RestartInteractionManifest) {
        $restartInteractionRaw = Get-Content -LiteralPath $Paths.RestartInteractionManifest -Raw
    }
    $standaloneDashboardWindowReady = (
        ($observedMarkers -contains "MONITORING_HUD_STANDALONE_DASHBOARD_WINDOW_READY") -or
        ($interactionRaw -match '"standalone_surface_independence"\s*:\s*true') -or
        ($interactionRaw -match '"dashboard_monitor_management"\s*:\s*true')
    )
    $surfaceNativeIndependenceReady = (
        ($observedMarkers -contains "MONITORING_HUD_SURFACE_NATIVE_INDEPENDENCE_READY") -or
        ($interactionRaw -match '"overlay_not_dashboard_coupled"\s*:\s*true') -or
        ($interactionRaw -match '"dashboardCoupled"\s*:\s*false') -or
        ($interactionRaw -match '"surfaceIndependence"\s*:\s*"dashboard_overlay_core_top_level_windows"')
    )
    $overlayCardsMovableReady = (
        ($observedMarkers -contains "MONITORING_HUD_OVERLAY_CARD_LAYOUT_EDITED") -or
        (
            ($interactionRaw -match 'active live-client drag overlay monitor card sent') -and
            ($interactionRaw -match 'active live-client resize overlay monitor card sent') -and
            (
                ($interactionRaw -match '"overlay_cards_owned_by_overlay"\s*:\s*true') -or
                ($interactionRaw -match '"cardsMovableInOverlay"\s*:\s*true')
            )
        )
    )
    $surfaceVirtualDesktopTravelReady = (
        ($observedMarkers -contains "MONITORING_HUD_SURFACE_VIRTUAL_DESKTOP_TRAVEL_READY") -or
        (
            ($interactionRaw -match 'dashboard and overlay move independently across virtual desktop without clipping') -and
            ($interactionRaw -match '"ok"\s*:\s*true') -and
            ($interactionRaw -match '"withinTargetMonitor"\s*:\s*true') -and
            ($interactionRaw -match '"withinVirtualDesktop"\s*:\s*true')
        )
    )
    $dashboardStandaloneWindowTravelReady = (
        ($observedMarkers -contains "MONITORING_HUD_DASHBOARD_STANDALONE_WINDOW_TRAVEL_READY") -or
        (
            ($interactionRaw -match 'dashboard standalone window moves across virtual desktop without clipping') -and
            ($interactionRaw -match '"ok"\s*:\s*true') -and
            ($interactionRaw -match '"movement"\s*:\s*"dashboard_native_window_only"')
        )
    )
    $dashboardClippingBoundaryReady = (
        ($observedMarkers -contains "MONITORING_HUD_DASHBOARD_CLIPPING_BOUNDARY_READY") -or
        (
            ($interactionRaw -match '"clippingOk"\s*:\s*true') -and
            ($interactionRaw -match '"withinTargetMonitor"\s*:\s*true') -and
            ($interactionRaw -match '"withinVirtualDesktop"\s*:\s*true')
        )
    )
    $dashboardCoreOverlayDecouplingReady = (
        ($observedMarkers -contains "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY") -or
        (
            ($interactionRaw -match '"decouplingOk"\s*:\s*true') -and
            ($interactionRaw -match '"overlayGeometryUnchanged"\s*:\s*true') -and
            ($interactionRaw -match '"coreGeometryUnchanged"\s*:\s*true')
        )
    )
    $dashboardSettingsContentReady = [bool]($observedMarkers -contains "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY")
    $dashboardMonitorGroupClarityReady = [bool]($observedMarkers -contains "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY")
    $dashboardOverlayNonGatingCopyReady = [bool]($observedMarkers -contains "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY")
    $dashboardProviderTruthReady = [bool]($observedMarkers -contains "MONITORING_HUD_DASHBOARD_PROVIDER_TRUTH_READY")
    $dashboardStateModelReady = [bool]($observedMarkers -contains "MONITORING_HUD_DASHBOARD_STATE_MODEL_READY")
    $dashboardWarningControlsReady = [bool]($observedMarkers -contains "MONITORING_HUD_DASHBOARD_WARNING_CONTROLS_READY")
    $coreIndependentPresetMonitorReady = (
        ($observedMarkers -contains "CORE_VISUALIZATION_INDEPENDENT_PRESET_MONITOR_READY") -or
        (
            ($interactionRaw -match '"travelPolicy"\s*:\s*"independent_user_selected_monitor_scoped"') -and
            ($interactionRaw -match '"attachedToHudDashboardOrNcp"\s*:\s*false')
        )
    )
    $coreHudSurfaceSeparationReady = (
        ($observedMarkers -contains "CORE_VISUALIZATION_HUD_SURFACE_SEPARATION_READY") -or
        (
            ($interactionRaw -match '"surfaceSeparationOk"\s*:\s*true') -and
            ($interactionRaw -match '"dashboardOverlap"\s*:\s*false') -and
            ($interactionRaw -match '"overlayOverlap"\s*:\s*false') -and
            ($interactionRaw -match '"movable"\s*:\s*false')
        )
    )
    $coreWorkerwCoordinateRebaseReady = [bool](
        $observedMarkers | Where-Object { $_ -match "CORE_VISUALIZATION_WORKERW_COORDINATE_REBASE_READY" }
    )
    $manifest = [pscustomobject]@{
        status = $script:ManifestStatus
        evidenceScope = "Monitoring HUD technical desktop observation; visual quality requires direct inspection"
        visualEvidenceLimit = "Markers, logs, and helper status are diagnostics; they do not establish user-facing visual acceptance"
        exactUserDesktopShortcutLaunchProof = $script:LaunchProof
        screenshotAndShortVideoObserved = [bool]($script:ScreenshotPath -and (Test-Path -LiteralPath $script:ScreenshotPath) -and ($script:ShortVideoProof.status -eq "PASS"))
        userFacingDesktopLauncherObserved = [bool]($script:LaunchProof.status -eq "PASS")
        overlayDisplayAcceptance = "deferred-non-gating"
        coreRepairClassification = "dependency-repair-only"
        dashboardSpecificProof = [pscustomobject]@{
            beforeLaunchFullVirtualDesktopScreenshot = [bool]$script:BeforeScreenshotPath
            afterLaunchFullVirtualDesktopScreenshot = [bool]$script:ScreenshotPath
            shortVideoOrFrameSequenceProof = $script:ShortVideoProof
            perElementUserInspectableScreenshots = $script:PerElementScreenshotProof
            userInspectableScreenshotFolder = [bool]$Paths.ScreenshotEvidenceRoot
            userInspectableElementScreenshotFolder = $Paths.ElementScreenshotEvidenceRoot
            exactUserDesktopShortcutLaunchProof = $script:LaunchProof
            activeUserFacingClient = [bool]$ActiveUserFacingClient
            activeClientProofClassification = "supporting-only-unless-launched-through-exact-user-desktop-shortcut"
            interactionSelfQA = $script:InteractionManifestStatus
            dashboardStandaloneWindowTravelReady = [bool]$dashboardStandaloneWindowTravelReady
            dashboardClippingBoundaryReady = [bool]$dashboardClippingBoundaryReady
            dashboardCoreOverlayDecouplingReady = [bool]$dashboardCoreOverlayDecouplingReady
            dashboardSettingsContentReady = [bool]$dashboardSettingsContentReady
            dashboardMonitorGroupClarityReady = [bool]$dashboardMonitorGroupClarityReady
            dashboardProviderTruthReady = [bool]$dashboardProviderTruthReady
            dashboardStateModelReady = [bool]$dashboardStateModelReady
            dashboardWarningControlsReady = [bool]$dashboardWarningControlsReady
            noFakeTelemetryPosture = $observedMarkers -contains "MONITORING_HUD_STATUS_BEHAVIOR_READY"
        }
        python = $PythonExe
        runtimeLog = $Paths.RuntimeLog
        beforeLaunchScreenshot = $script:BeforeScreenshotPath
        userInspectableBeforeLaunchScreenshot = $script:BeforeScreenshotEvidencePath
        screenshot = $script:ScreenshotPath
        screenshotEvidenceRoot = $Paths.ScreenshotEvidenceRoot
        elementScreenshotEvidenceRoot = $Paths.ElementScreenshotEvidenceRoot
        perElementUserInspectableScreenshots = $script:PerElementScreenshotProof
        userInspectableScreenshot = $script:ScreenshotEvidencePath
        afterLaunchScreenshot = $script:ScreenshotPath
        userInspectableAfterLaunchScreenshot = $script:ScreenshotEvidencePath
        activeUserFacingClient = [bool]$ActiveUserFacingClient
        interactionSelfQARequested = $effectiveRunInteractionSelfQA
        interactionStepDelayMs = $effectiveStepDelayMilliseconds
        finalClientHoldMs = $effectiveFinalHoldMilliseconds
        markerTimeoutSeconds = $MarkerTimeoutSeconds
        noProgressTimeoutSeconds = $NoProgressTimeoutSeconds
        interactionManifest = $Paths.InteractionManifest
        interactionManifestStatus = $script:InteractionManifestStatus
        interactionEvidenceRoot = $Paths.InteractionEvidenceRoot
        restartInteractionManifest = $Paths.RestartInteractionManifest
        restartInteractionManifestStatus = $script:RestartInteractionManifestStatus
        restartInteractionEvidenceRoot = $Paths.RestartInteractionEvidenceRoot
        restartInteractionProof = [pscustomobject]@{
            requested = [bool]($script:RestartInteractionManifestStatus -ne "NOT_REQUESTED")
            status = $script:RestartInteractionManifestStatus
            manifest = $Paths.RestartInteractionManifest
            evidenceRoot = $Paths.RestartInteractionEvidenceRoot
            requiredLabelPresent = [bool]($restartInteractionRaw -match [regex]::Escape("Restart check reloads saved USER Overlay Profile and Recording target mirror"))
            sameDisposableStatePath = $env:NEXUS_MONITORING_HUD_STATE_PATH
        }
        supplementalIssueProof = $script:SupplementalIssueProof
        shortVideoProof = $script:ShortVideoProof
        revisedOverlayProof = [pscustomobject]@{
            beforeLaunchFullVirtualDesktopScreenshot = [bool]$script:BeforeScreenshotPath
            afterLaunchFullVirtualDesktopScreenshot = [bool]$script:ScreenshotPath
            fullVirtualDesktopScreenshot = [bool]$script:ScreenshotPath
            userInspectableScreenshot = [bool]$script:ScreenshotEvidencePath
            beforeAfterDesktopComparisonReady = [bool]($script:BeforeScreenshotPath -and $script:ScreenshotPath)
            activeUserFacingClient = [bool]$ActiveUserFacingClient
            interactionSelfQA = $script:InteractionManifestStatus
            dashboardMinimalSplitReady = $observedMarkers -contains "MONITORING_HUD_DASHBOARD_MINIMAL_SPLIT_READY"
            edgelessOverlayCanvasReady = $observedMarkers -contains "MONITORING_HUD_EDGELESS_OVERLAY_CANVAS_READY"
            standaloneDashboardWindowReady = [bool]$standaloneDashboardWindowReady
            surfaceNativeIndependenceReady = [bool]$surfaceNativeIndependenceReady
            dashboardStandaloneWindowTravelReady = [bool]$dashboardStandaloneWindowTravelReady
            dashboardClippingBoundaryReady = [bool]$dashboardClippingBoundaryReady
            dashboardCoreOverlayDecouplingReady = [bool]$dashboardCoreOverlayDecouplingReady
            dashboardSettingsContentReady = [bool]$dashboardSettingsContentReady
            dashboardMonitorGroupClarityReady = [bool]$dashboardMonitorGroupClarityReady
            dashboardOverlayNonGatingCopyReady = [bool]$dashboardOverlayNonGatingCopyReady
            dashboardProviderTruthReady = [bool]$dashboardProviderTruthReady
            dashboardStateModelReady = [bool]$dashboardStateModelReady
            dashboardWarningControlsReady = [bool]$dashboardWarningControlsReady
            overlayCardsMovableReady = [bool]$overlayCardsMovableReady
            surfaceVirtualDesktopTravelReady = [bool]$surfaceVirtualDesktopTravelReady
            coreIndependentPresetMonitorReady = [bool]$coreIndependentPresetMonitorReady
            coreHudSurfaceSeparationReady = [bool]$coreHudSurfaceSeparationReady
            coreWorkerwCoordinateRebaseReady = [bool]$coreWorkerwCoordinateRebaseReady
            standaloneOverlayDisplayWindowReady = $observedMarkers -contains "MONITORING_HUD_STANDALONE_OVERLAY_DISPLAY_WINDOW_READY"
            anchoredOverlayUninteractableReady = $observedMarkers -contains "MONITORING_HUD_ANCHORED_OVERLAY_UNINTERACTABLE_READY"
            overlayPositionPreservedReady = $observedMarkers -contains "MONITORING_HUD_OVERLAY_POSITION_PRESERVED_READY"
            providerContractReady = $observedMarkers -contains "MONITORING_HUD_TELEMETRY_BOUNDARY_READY"
            noFakeTelemetryPosture = $observedMarkers -contains "MONITORING_HUD_STATUS_BEHAVIOR_READY"
        }
        observedMarkers = $observedMarkers
        cleanupNotes = @($script:CleanupNotes)
        failureMessage = $script:FailureMessage
        generatedAt = (Get-Date).ToUniversalTime().ToString("o")
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Paths.Manifest -Encoding utf8
}



function Quote-ProcessArgument([string]$Value) {
    '"' + ($Value -replace '"', '\"') + '"'
}

function Get-ExactUserDesktopShortcutPath {
    $defaultPath = "C:\Users\anden\OneDrive\Desktop\FAM-006 RED - Nexus Desktop AI Launcher.lnk"
    if ([string]::IsNullOrWhiteSpace($ExactDesktopShortcutPath)) {
        return $defaultPath
    }

    $expected = if (Test-Path -LiteralPath $defaultPath) {
        (Resolve-Path -LiteralPath $defaultPath).Path
    } else {
        $defaultPath
    }
    $provided = if (Test-Path -LiteralPath $ExactDesktopShortcutPath) {
        (Resolve-Path -LiteralPath $ExactDesktopShortcutPath).Path
    } else {
        $ExactDesktopShortcutPath
    }
    if (-not [string]::Equals($expected, $provided, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Live Validation requires the exact USER Desktop FAM-006 shortcut path: $defaultPath. Provided path is not allowed for LV1 proof: $ExactDesktopShortcutPath"
    }
    return $defaultPath
}

function Resolve-ExactDesktopShortcutForActiveRoot {
    param([string]$ShortcutPath)

    $result = [ordered]@{
        path = $ShortcutPath
        targetPath = ""
        workingDirectory = ""
        arguments = ""
        activeRoot = $rootDir
        status = "FAIL"
        detail = ""
    }

    if (-not (Test-Path -LiteralPath $ShortcutPath)) {
        $result.detail = "Exact USER Desktop shortcut is missing: $ShortcutPath"
        return $result
    }

    try {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($ShortcutPath)
        $targetPath = [string]$shortcut.TargetPath
        $workingDirectory = [string]$shortcut.WorkingDirectory
        $arguments = [string]$shortcut.Arguments
        $result.targetPath = $targetPath
        $result.workingDirectory = $workingDirectory
        $result.arguments = $arguments

        $resolvedRoot = (Resolve-Path -LiteralPath $rootDir).Path.TrimEnd('\')
        $targetMatches = $false
        $workingDirectoryMatches = $false
        if (-not [string]::IsNullOrWhiteSpace($targetPath) -and (Test-Path -LiteralPath $targetPath)) {
            $resolvedTarget = (Resolve-Path -LiteralPath $targetPath).Path
            $targetMatches = $resolvedTarget.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)
        }
        if (-not [string]::IsNullOrWhiteSpace($workingDirectory) -and (Test-Path -LiteralPath $workingDirectory)) {
            $resolvedWorkingDirectory = (Resolve-Path -LiteralPath $workingDirectory).Path.TrimEnd('\')
            $workingDirectoryMatches = $resolvedWorkingDirectory.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)
        }

        if ($targetMatches -and $workingDirectoryMatches) {
            $result.status = "PASS"
            $result.detail = "Exact USER Desktop shortcut target and working directory are rooted in the active FAM-006 worktree."
            return $result
        }

        $result.detail = "Exact USER Desktop shortcut is not rooted in the active FAM-006 worktree; targetMatches=$targetMatches; workingDirectoryMatches=$workingDirectoryMatches."
        return $result
    }
    catch {
        $result.detail = "Unable to inspect exact USER Desktop shortcut target: $($_.Exception.Message)"
        return $result
    }
}

function Get-ForeignNexusRuntimeProcesses {
    param(
        [string]$ActiveRoot
    )

    $resolvedActiveRoot = ""
    if (-not [string]::IsNullOrWhiteSpace($ActiveRoot) -and (Test-Path -LiteralPath $ActiveRoot)) {
        $resolvedActiveRoot = (Resolve-Path -LiteralPath $ActiveRoot).Path.TrimEnd('\')
    }
    $processes = @()
    try {
        $processes = @(
            Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" -ErrorAction SilentlyContinue |
                Where-Object {
                    $cmd = [string]$_.CommandLine
                    $cmd -match "\\Nexus Worktrees\\" -and
                    ($cmd -match "desktop\\orin_desktop_main\.py" -or $cmd -match "desktop\\desktop_renderer\.py")
                }
        )
    }
    catch {
        return @()
    }

    $foreign = @()
    foreach ($process in $processes) {
        $cmd = [string]$process.CommandLine
        $isActiveRootProcess = (-not [string]::IsNullOrWhiteSpace($resolvedActiveRoot)) -and
            ($cmd.IndexOf($resolvedActiveRoot, [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
        if (-not $isActiveRootProcess) {
            $foreign += $process
        }
    }
    return $foreign
}

function Assert-NoForeignNexusRuntimeCollision {
    param(
        [object]$Paths,
        [string]$Label
    )

    $foreign = @(Get-ForeignNexusRuntimeProcesses -ActiveRoot $rootDir)
    if ($foreign.Count -gt 0) {
        $summaries = @()
        foreach ($process in $foreign) {
            $cmd = ([string]$process.CommandLine).Trim()
            if ($cmd.Length -gt 260) {
                $cmd = $cmd.Substring(0, 260) + "..."
            }
            $summaries += "pid=$($process.ProcessId) name=$($process.Name) command=$cmd"
        }
        $detail = "$Label exact USER Desktop shortcut Live Validation blocked: another Nexus worktree runtime is active, so single-instance relaunch proof would not be attributable to FAM-006. Close or explicitly approve stopping the foreign runtime before renewed LV1. Foreign runtime(s): $($summaries -join ' | ')"
        Step $Paths $detail
        throw $detail
    }
}

function Assert-NoSingleInstanceRelaunchCollision {
    param(
        [object]$Paths,
        [string]$RuntimeLog,
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $RuntimeLog)) {
        return
    }
    try {
        $text = Get-Content -LiteralPath $RuntimeLog -Raw -ErrorAction Stop
        if ($text -match "SINGLE_INSTANCE_CONFLICT_DETECTED|RELAUNCH_SIGNAL_SENT|RELAUNCH_REPLACEMENT_SESSION_CONFIRMED") {
            $detail = "$Label exact USER Desktop shortcut Live Validation blocked: runtime log shows single-instance relaunch/replacement flow. This cannot be accepted as clean FAM-006 visual proof while another runtime may own the visible session. Runtime log: $RuntimeLog"
            Step $Paths $detail
            throw $detail
        }
    }
    catch {
        if ($_.Exception.Message -match "single-instance relaunch|Live Validation blocked") {
            throw
        }
        Step $Paths "$Label single-instance collision scan could not read runtime log: $($_.Exception.Message)"
    }
}

function Wait-ExactShortcutRuntimeLog {
    param(
        [object]$Paths,
        [datetime]$LaunchTime,
        [string]$Label,
        [string[]]$ExcludedRuntimeLogs = @(),
        [int[]]$ExcludedRendererProcessIds = @()
    )

    $deadline = (Get-Date).AddSeconds($MarkerTimeoutSeconds)
    $excludedRuntimeLogSet = @{}
    foreach ($excludedPath in @($ExcludedRuntimeLogs)) {
        if (-not [string]::IsNullOrWhiteSpace($excludedPath)) {
            $excludedRuntimeLogSet[(Join-Path (Split-Path -Parent $excludedPath) (Split-Path -Leaf $excludedPath)).ToLowerInvariant()] = $true
        }
    }
    $excludedPidSet = @{}
    foreach ($excludedPid in @($ExcludedRendererProcessIds)) {
        if ([int]$excludedPid -gt 0) {
            $excludedPidSet[[string][int]$excludedPid] = $true
        }
    }
    while ((Get-Date) -lt $deadline) {
        $candidates = @(
            Get-ChildItem -LiteralPath $Paths.Root -Filter "Runtime_*.txt" -File -ErrorAction SilentlyContinue |
                Where-Object { $_.LastWriteTime -ge $LaunchTime.AddSeconds(-2) } |
                Sort-Object LastWriteTime -Descending
        )
        foreach ($candidate in $candidates) {
            try {
                if ($excludedRuntimeLogSet.ContainsKey($candidate.FullName.ToLowerInvariant())) {
                    continue
                }
                $text = Get-Content -LiteralPath $candidate.FullName -Raw -ErrorAction Stop
                $pidMatch = [regex]::Match($text, "Renderer PID:\s*(\d+)")
                if ($pidMatch.Success -and $excludedPidSet.ContainsKey($pidMatch.Groups[1].Value)) {
                    continue
                }
                if ($text -match "RENDERER_MAIN\|START") {
                    Assert-NoSingleInstanceRelaunchCollision -Paths $Paths -RuntimeLog $candidate.FullName -Label $Label
                    Step $Paths "$Label exact Desktop shortcut runtime log detected: $($candidate.FullName)"
                    return $candidate.FullName
                }
            }
            catch {}
        }
        Check-Progress "waiting for $Label exact Desktop shortcut runtime log"
        Start-Sleep -Milliseconds 250
    }
    throw "Timed out waiting for $Label runtime log created through exact USER Desktop shortcut under $($Paths.Root)."
}

function Wait-RendererProcessFromRuntimeLog {
    param(
        [object]$Paths,
        [string]$RuntimeLog,
        [string]$Label
    )

    $deadline = (Get-Date).AddSeconds([Math]::Max(10, [Math]::Min($MarkerTimeoutSeconds, 30)))
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $RuntimeLog) {
            try {
                $text = Get-Content -LiteralPath $RuntimeLog -Raw -ErrorAction Stop
                $match = [regex]::Match($text, "Renderer PID:\s*(\d+)")
                if ($match.Success) {
                    $rendererPid = [int]$match.Groups[1].Value
                    $rendererProcess = Get-Process -Id $rendererPid -ErrorAction Stop
                    Step $Paths "$Label exact Desktop shortcut renderer process resolved: pid=$rendererPid"
                    return $rendererProcess
                }
            }
            catch {
                Step $Paths "$Label exact Desktop shortcut renderer process resolution pending: $($_.Exception.Message)"
            }
        }
        Check-Progress "waiting for $Label renderer process from exact Desktop shortcut runtime log"
        Start-Sleep -Milliseconds 250
    }
    throw "Timed out resolving $Label renderer process from exact USER Desktop shortcut runtime log: $RuntimeLog"
}

function Start-ExactDesktopShortcutRuntime {
    param(
        [object]$Paths,
        [string]$ShortcutPath,
        [string]$Label,
        [string[]]$ExcludedRuntimeLogs = @(),
        [int[]]$ExcludedRendererProcessIds = @()
    )

    $script:ShortcutResolution = Resolve-ExactDesktopShortcutForActiveRoot -ShortcutPath $ShortcutPath
    $script:LaunchProof.shortcutPath = $ShortcutPath
    $script:LaunchProof.shortcutResolution = $script:ShortcutResolution
    if ($script:ShortcutResolution.status -ne "PASS") {
        $script:LaunchProof.status = "FAIL"
        throw $script:ShortcutResolution.detail
    }

    Assert-NoForeignNexusRuntimeCollision -Paths $Paths -Label $Label
    $launchTime = Get-Date
    $launcherProcess = Start-Process -FilePath $ShortcutPath -PassThru
    Step $Paths "$Label launched through exact USER Desktop shortcut: $ShortcutPath pid=$($launcherProcess.Id)"
    $runtimeLog = Wait-ExactShortcutRuntimeLog -Paths $Paths -LaunchTime $launchTime -Label $Label -ExcludedRuntimeLogs $ExcludedRuntimeLogs -ExcludedRendererProcessIds $ExcludedRendererProcessIds | Select-Object -Last 1
    Assert-NoForeignNexusRuntimeCollision -Paths $Paths -Label $Label
    $rendererProcess = Wait-RendererProcessFromRuntimeLog -Paths $Paths -RuntimeLog $runtimeLog -Label $Label | Select-Object -Last 1
    $script:LaunchProof.status = "PASS"
    $script:LaunchProof.launcherProcessId = [int]$launcherProcess.Id
    $script:LaunchProof.rendererProcessId = [int]$rendererProcess.Id
    if ($Label -match "restart") {
        $script:LaunchProof.restartRuntimeLog = $runtimeLog
    }
    else {
        $script:LaunchProof.runtimeLog = $runtimeLog
    }
    return [pscustomobject]@{
        process = $rendererProcess
        launcherProcess = $launcherProcess
        runtimeLog = $runtimeLog
    }
}

$paths = New-Paths
$pythonExe = ""
$exitCode = 1
$effectiveRunInteractionSelfQA = [bool]($RunInteractionSelfQA -or $ActiveUserFacingClient)
$effectiveVisibleClient = [bool]($VisibleClient -or $ActiveUserFacingClient)
$effectiveRecordingFocusedLane = [bool]($RecordingOptionCSelfQA -or $Rar3DProof -or $Rar3EProof -or $SupplementalRuntimeProof -or $UserConfirmedACSupplementProof)
$effectiveFocusedLane = if ($Rar3EProof) { "recording-option-c-rar3e" } elseif ($Rar3DProof) { "recording-option-c-rar3d" } elseif ($effectiveRecordingFocusedLane) { "recording-option-c" } else { "full" }
$effectiveStepDelayMilliseconds = $InteractionStepDelayMilliseconds
$effectiveFinalHoldMilliseconds = $FinalClientHoldSeconds * 1000
if ($ActiveUserFacingClient) {
    if ($effectiveRecordingFocusedLane) {
        $effectiveStepDelayMilliseconds = [Math]::Max($effectiveStepDelayMilliseconds, 750)
        $effectiveFinalHoldMilliseconds = [Math]::Max($effectiveFinalHoldMilliseconds, 1000)
    }
    else {
        $effectiveStepDelayMilliseconds = [Math]::Max($effectiveStepDelayMilliseconds, 2500)
        $effectiveFinalHoldMilliseconds = [Math]::Max($effectiveFinalHoldMilliseconds, 20000)
    }
}
if ($effectiveRunInteractionSelfQA) {
    $MarkerTimeoutSeconds = [Math]::Max($MarkerTimeoutSeconds, 420)
    $NoProgressTimeoutSeconds = [Math]::Max($NoProgressTimeoutSeconds, 420)
}

$environmentNamesToRestore = @(
    "NEXUS_MONITORING_HUD_STATE_PATH",
    "NEXUS_MONITORING_HUD_RECORDING_VALIDATION_EXPORT_DIR",
    "NEXUS_MONITORING_HUD_LIVE_SELF_QA_MANIFEST",
    "NEXUS_MONITORING_HUD_LIVE_SELF_QA_ROOT",
    "NEXUS_MONITORING_HUD_LIVE_SELF_QA_STEP_DELAY_MS",
    "NEXUS_MONITORING_HUD_LIVE_SELF_QA_FINAL_HOLD_MS",
    "NEXUS_MONITORING_HUD_LIVE_SELF_QA_LANE",
    "NEXUS_HARNESS_LOG_ROOT",
    "NEXUS_HARNESS_DISABLE_DIAGNOSTICS",
    "NEXUS_HARNESS_DISABLE_VOICE",
    "NEXUS_HARNESS_AUTO_ACCEPT_RELAUNCH",
    "NEXUS_HARNESS_SUPPRESS_ALREADY_RUNNING_DIALOGS",
    "NEXUS_HARNESS_RELAUNCH_WAIT_SECONDS"
)
$previousEnvironment = @{}
foreach ($environmentName in $environmentNamesToRestore) {
    $previousEnvironment[$environmentName] = [Environment]::GetEnvironmentVariable($environmentName, "Process")
}
try {
    Step $paths "starting FAM-006 Monitoring/HUD live desktop validation"
    $pythonExe = Resolve-ValidationPython
    Step $paths "resolved Python: $pythonExe"
    Capture-Screen $paths "before_launch"
    $exactUserDesktopShortcut = Get-ExactUserDesktopShortcutPath
    $env:NEXUS_MONITORING_HUD_STATE_PATH = (Join-Path $paths.Root "monitoring_hud_state.json")
    $env:NEXUS_MONITORING_HUD_RECORDING_VALIDATION_EXPORT_DIR = (Join-Path $paths.Root "manual_exports")
    $env:NEXUS_HARNESS_LOG_ROOT = $paths.Root
    $env:NEXUS_HARNESS_DISABLE_DIAGNOSTICS = "1"
    $env:NEXUS_HARNESS_DISABLE_VOICE = "1"
    $env:NEXUS_HARNESS_AUTO_ACCEPT_RELAUNCH = "1"
    $env:NEXUS_HARNESS_SUPPRESS_ALREADY_RUNNING_DIALOGS = "1"
    $env:NEXUS_HARNESS_RELAUNCH_WAIT_SECONDS = "20"

    if ($effectiveRunInteractionSelfQA) {
        Assert-NoSyntheticLiveValidationInteraction $paths
        New-Item -ItemType Directory -Force -Path $paths.InteractionEvidenceRoot | Out-Null
        $script:InteractionManifestStatus = "PENDING"
    }
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_MANIFEST = if ($effectiveRunInteractionSelfQA) { $paths.InteractionManifest } else { "" }
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_ROOT = if ($effectiveRunInteractionSelfQA) { $paths.InteractionEvidenceRoot } else { "" }
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_STEP_DELAY_MS = [string]$effectiveStepDelayMilliseconds
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_FINAL_HOLD_MS = [string]$effectiveFinalHoldMilliseconds
    $env:NEXUS_MONITORING_HUD_LIVE_SELF_QA_LANE = $effectiveFocusedLane

    $launch = Start-ExactDesktopShortcutRuntime -Paths $paths -ShortcutPath $exactUserDesktopShortcut -Label "primary LV1" | Select-Object -Last 1
    $script:RuntimeProcess = $launch.process
    $script:RuntimeLauncherProcess = $launch.launcherProcess
    $paths.RuntimeLog = $launch.runtimeLog
    Step $paths "primary LV1 runtime log bound to exact USER Desktop shortcut launch: $($paths.RuntimeLog)"

    $requiredMarkers = @(
        "RENDERER_MAIN|START",
        "RENDERER_MAIN|QAPPLICATION_CREATED",
        "RENDERER_MAIN|CORE_VISUALIZATION_PRESET_MONITOR_SELECTION_READY",
        "RENDERER_MAIN|WINDOW_CONSTRUCTED",
        "RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_READY|surface=separate_persona_core",
        "RENDERER_MAIN|CORE_VISUALIZATION_DESKTOP_LAYER_READY|surface=separate_persona_core",
        "RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_GEOMETRY_READY",
        "RENDERER_MAIN|CORE_VISUALIZATION_WORKERW_COORDINATE_REBASE_READY",
        "RENDERER_MAIN|CORE_VISUALIZATION_FIXED_PRESET_MONITOR_READY",
        "RENDERER_MAIN|CORE_VISUALIZATION_INDEPENDENT_PRESET_MONITOR_READY",
        "RENDERER_MAIN|CORE_VISUALIZATION_WINDOW_VISIBLE|surface=separate_persona_core",
        "RENDERER_MAIN|VISUAL_PAGE_READY",
        "RENDERER_MAIN|CORE_VISUALIZATION_READY",
        "MONITORING_HUD_BASELINE_READY",
        "MONITORING_HUD_PRODUCT_VISIBILITY_READY",
        "MONITORING_HUD_DASHBOARD_SURFACE_READY",
        "MONITORING_HUD_OVERLAY_DEFERRAL_ENFORCED_READY",
        "MONITORING_HUD_MINIMAL_OVERLAY_READY",
        "MONITORING_HUD_DASHBOARD_MINIMAL_SPLIT_READY",
        "MONITORING_HUD_DASHBOARD_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MOTION_POLISH_READY",
        "MONITORING_HUD_DASHBOARD_SCROLLBAR_STYLE_READY",
        "MONITORING_HUD_DASHBOARD_SETTINGS_CONTENT_READY",
        "MONITORING_HUD_DASHBOARD_MONITOR_GROUP_CLARITY_READY",
        "MONITORING_HUD_DASHBOARD_OVERLAY_NON_GATING_COPY_READY",
        "MONITORING_HUD_DASHBOARD_PROVIDER_TRUTH_READY",
        "MONITORING_HUD_DASHBOARD_STATE_MODEL_READY",
        "MONITORING_HUD_DASHBOARD_WARNING_CONTROLS_READY",
        "MONITORING_HUD_EDGELESS_OVERLAY_CANVAS_READY",
        "MONITORING_HUD_TELEMETRY_BOUNDARY_READY",
        "MONITORING_HUD_PLACEMENT_OWNERSHIP_READY",
        "MONITORING_HUD_CONTROLS_VISIBILITY_READY",
        "MONITORING_HUD_STATUS_BEHAVIOR_READY",
        "MONITORING_HUD_CONTROL_STATE_READY",
        "RENDERER_MAIN|STARTUP_READY",
        "DESKTOP_OUTCOME|SETTLED|state=dormant"
    )
    $interactionSupportingMarkers = @(
        "MONITORING_HUD_WINDOW_STATUS_READY",
        "MONITORING_HUD_INTERACTION_MODE_READY"
    )
    $deferredOverlaySupportingMarkers = @(
        "MONITORING_HUD_MINIMAL_NATIVE_OVERLAY_READY",
        "MONITORING_HUD_STANDALONE_OVERLAY_DISPLAY_WINDOW_READY",
        "MONITORING_HUD_ANCHORED_OVERLAY_UNINTERACTABLE_READY",
        "MONITORING_HUD_OVERLAY_POSITION_PRESERVED_READY",
        "MONITORING_HUD_MINIMAL_ANCHORED_CLICK_THROUGH_READY",
        "MONITORING_HUD_MINIMAL_NON_FOCUS_READY",
        "MONITORING_HUD_VISIBLE_OVERLAY_READY",
        "DESKTOP_VISIBLE_OVERLAY_RESULT|success=true"
    )
    $trayLifecycleMarkers = @(
        "MONITORING_HUD_TRAY_ENABLE_RENDER_STABLE_READY",
        "MONITORING_HUD_TRAY_ENABLE_DISABLE_ROUNDTRIP_READY",
        "MONITORING_HUD_TRAY_DASHBOARD_OPEN_CLOSE_READY",
        "MONITORING_HUD_DISABLE_RECOVERY_READY"
    )
    foreach ($marker in $requiredMarkers) {
        Wait-Marker $paths $marker
    }
    foreach ($marker in $deferredOverlaySupportingMarkers) {
        $count = Marker-Count $paths $marker
        if ($count -gt 0) {
            $script:ObservedMarkers.Add($marker)
            Step $paths "observed optional deferred overlay marker: $marker count=$count"
        }
        else {
            Step $paths "optional deferred overlay marker absent (non-gating): $marker"
        }
    }
    foreach ($marker in $interactionSupportingMarkers) {
        $count = Marker-Count $paths $marker
        if ($count -gt 0) {
            $script:ObservedMarkers.Add($marker)
            Step $paths "observed interaction-supporting marker: $marker count=$count"
        }
        else {
            Step $paths "interaction-supporting marker not emitted in startup-only proof: $marker"
        }
    }

    if ($effectiveRunInteractionSelfQA) {
        Step $paths "waiting for live-client interaction self-QA markers"
        Wait-Marker $paths "MONITORING_HUD_LIVE_CLIENT_SELF_QA_READY"
        if (-not (Test-Path -LiteralPath $paths.InteractionManifest)) {
            throw "Interaction self-QA manifest was not written: $($paths.InteractionManifest)"
        }
        $interactionManifest = Get-Content -LiteralPath $paths.InteractionManifest -Raw | ConvertFrom-Json
        $interactionManifestRaw = Get-Content -LiteralPath $paths.InteractionManifest -Raw
        $script:InteractionManifestStatus = [string]$interactionManifest.status
        if ($script:InteractionManifestStatus -ne "PASS") {
            throw "Interaction self-QA did not pass. Status: $script:InteractionManifestStatus"
        }
        if ($interactionManifestRaw -match '"directJsClickUsed"\s*:\s*true' -or
            $interactionManifestRaw -match '"directJsMouseoverUsed"\s*:\s*true' -or
            $interactionManifestRaw -match '"nativeWebViewMessageFallbackUsed"\s*:\s*true' -or
            $interactionManifestRaw -match '"inputProof"\s*:\s*"automated-supporting-only:' -or
            $interactionManifestRaw -notmatch '"realOsInputProof"\s*:\s*true') {
            throw "Interaction self-QA lacks real OS-level mouse input proof. JavaScript clicks, synthetic DOM events, WebView native-message fallback, WebView handler calls, QTest widget-only events, and state mutation are banned as primary LV1 interaction proof."
        }
        if ($Rar3EProof) {
            $requiredInteractionLabels = @(
                "Dashboard Recording card target/status visual contract is focused before child windows",
                "real OS click opens Dashboard Recording Suite",
                "Recording Suite native window screenshot-capture readiness",
                "real OS click starts Dashboard Recording",
                "real OS click stops Dashboard Recording and requests local output",
                "Dashboard Recording stop writes local output and readback proof",
                "Recording Suite compact native/current-log tracking updates after save",
                "real OS click opens Dashboard Recording Log Viewer",
                "Dashboard Recording Log Viewer crosses backend native-window bridge",
                "Log Viewer native window screenshot-capture readiness",
                "RAR3D real OS hover HUD Dashboard close control",
                "RAR3D real OS hover Quick Access Start/Stop",
                "RAR3D real OS click opens Recording Studio for ordered proof",
                "RAR3D Recording Studio min/close ordered visual states",
                "RAR3D Recording Studio Start/Stop ordered visual states",
                "RAR3D Recording Studio literal geometry persistence sequence",
                "RAR3D real OS click opens Log Viewer for ordered proof",
                "RAR3D Log Viewer min/close ordered visual states",
                "RAR3D Log Viewer folder button ordered visual states",
                "RAR3D Log Viewer literal geometry persistence sequence",
                "RAR3E HUD Dashboard real drag close reopen geometry proof",
                "RAR3E HUD Dashboard close pressed/clicked proof",
                "RAR3E HUD Dashboard close keyboard activation proof",
                "RAR3E Quick Access hover proof",
                "RAR3E Quick Access keyboard start activation proof",
                "RAR3E Quick Access keyboard stop/saved activation proof",
                "RAR3E Recording Card Studio button hover proof",
                "RAR3E Recording Card Studio button keyboard activation proof",
                "RAR3E Recording Card Log Viewer button hover proof",
                "RAR3E Recording Card Log Viewer button keyboard activation proof",
                "RAR3E Recording Studio direct Start activation proof",
                "RAR3E Recording Studio direct Stop/saved activation proof",
                "RAR3E Recording Studio keyboard Start activation proof",
                "RAR3E Recording Studio keyboard Stop/saved activation proof",
                "RAR3E Log Viewer Open Native folder activation proof",
                "RAR3E Log Viewer Open Export folder activation proof",
                "RAR3E Recording Studio real title-bar drag geometry proof",
                "RAR3E Log Viewer real title-bar drag geometry proof",
                "RAR3E safe failure-state controlled-setup classification"
            )
        }
        elseif ($Rar3DProof) {
            $requiredInteractionLabels = @(
                "Dashboard Recording card target/status visual contract is focused before child windows",
                "real OS click opens Dashboard Recording Suite",
                "Recording Suite native window screenshot-capture readiness",
                "real OS click starts Dashboard Recording",
                "real OS click stops Dashboard Recording and requests local output",
                "Dashboard Recording stop writes local output and readback proof",
                "Recording Suite compact native/current-log tracking updates after save",
                "real OS click opens Dashboard Recording Log Viewer",
                "Dashboard Recording Log Viewer crosses backend native-window bridge",
                "Log Viewer native window screenshot-capture readiness",
                "RAR3D real OS hover HUD Dashboard close control",
                "RAR3D real OS hover Quick Access Start/Stop",
                "RAR3D real OS click opens Recording Studio for ordered proof",
                "RAR3D Recording Studio min/close ordered visual states",
                "RAR3D Recording Studio Start/Stop ordered visual states",
                "RAR3D Recording Studio literal geometry persistence sequence",
                "RAR3D real OS click opens Log Viewer for ordered proof",
                "RAR3D Log Viewer min/close ordered visual states",
                "RAR3D Log Viewer folder button ordered visual states",
                "RAR3D Log Viewer literal geometry persistence sequence",
                "RAR3D safe failure-state disposition summary"
            )
        }
        elseif ($effectiveRecordingFocusedLane) {
            $requiredInteractionLabels = @(
                "Dashboard Recording card target/status visual contract is focused before child windows",
                "real OS click opens Dashboard Recording Suite",
                "Recording Suite native window screenshot-capture readiness",
                "real OS click starts Dashboard Recording",
                "real OS click stops Dashboard Recording and requests local output",
                "Dashboard Recording stop writes local output and readback proof",
                "Recording Suite compact native/current-log tracking updates after save",
                "real OS click opens Dashboard Recording Log Viewer",
                "Dashboard Recording Log Viewer crosses backend native-window bridge",
                "Log Viewer native window screenshot-capture readiness",
                "C1 Log Viewer closed before repeated Start/Stop",
                "C1 real OS click starts recording after Log Viewer close",
                "C1 real OS click stops recording after Log Viewer close",
                "C1 Log Viewer remains closed and unfocused after Start/Stop",
                "C2 real OS click opens Log Viewer before minimize test",
                "C2 Log Viewer minimized before repeated Start/Stop",
                "C2 real OS click starts recording after Log Viewer minimize",
                "C2 real OS click stops recording after Log Viewer minimize",
                "C2 Log Viewer remains minimized and unfocused after Start/Stop",
                "C3 real OS click opens Log Viewer before unfocused-open test",
                "C3 Log Viewer open but unfocused before repeated Start/Stop",
                "C3 real OS click starts recording after Log Viewer open unfocused",
                "C3 real OS click stops recording after Log Viewer open unfocused",
                "C3 Log Viewer remains open and unfocused after Start/Stop",
                "Independent Recording Suite and Log Viewer windows are closed before Overlay Profile proof",
                "Dashboard child windows are closed before HUD Overlay selector proof",
                "HUD Overlay card Active Overlay Profile selector is visible after viewport restore",
                "real OS click opens HUD Overlay card Active Overlay Profile selector",
                "real OS click selects HUD Overlay card Active Overlay Profile option",
                "Recording Option C focused lane completed current-branch feature proof only"
            )
        }
        else {
            $requiredInteractionLabels = @(
                "Active child window prevents Dashboard click-through under overlapping controls",
                "Compact Overlay Profiles window preserves functional visible monitor row and action buttons",
                "Compact Overlay Profiles delete confirmation stays unclipped and non-overlapping",
                "Create Profile opens unsaved draft with empty monitor membership",
                "Dirty-change guard blocks close after created draft",
                "Manage Monitors dirty guard matches shared modal Save Discard Cancel contract",
                "Manage Monitors dirty guard Cancel returns to dirty draft without queued close",
                "Manage Monitors dirty guard Discard completes queued close and clears dirty state",
                "Create after delete reuses Monitor Group 3 instead of skipping to a higher number"
            )
        }
        foreach ($requiredLabel in $requiredInteractionLabels) {
            if ($interactionManifestRaw -notmatch [regex]::Escape($requiredLabel)) {
                throw "Interaction self-QA missing required real-input scenario: $requiredLabel"
            }
        }
        if (-not $effectiveRecordingFocusedLane) {
            Wait-Marker $paths "MONITORING_HUD_DASHBOARD_STANDALONE_WINDOW_TRAVEL_READY"
            Wait-Marker $paths "MONITORING_HUD_DASHBOARD_CLIPPING_BOUNDARY_READY"
            Wait-Marker $paths "MONITORING_HUD_DASHBOARD_CORE_OVERLAY_DECOUPLING_READY"
        }
        Wait-Marker $paths "MONITORING_HUD_LIVE_CLIENT_SELF_QA_INTERACTION_READY"
        Step $paths "interaction self-QA manifest PASS: $($paths.InteractionManifest)"
        if ($effectiveRecordingFocusedLane) {
            Run-RestartInteractionSelfQA $paths $exactUserDesktopShortcut $effectiveStepDelayMilliseconds $effectiveFinalHoldMilliseconds
        }
        $script:PerElementScreenshotProof = Copy-FocusedElementScreenshotsToUserEvidence -Paths $paths -FocusedLane $effectiveFocusedLane
        if ($script:PerElementScreenshotProof.status -ne "PASS") {
            throw "LV1 focused per-element screenshots missing or failed: $($script:PerElementScreenshotProof.reason)"
        }
        Step $paths "copied mandatory LV1 focused per-element screenshots to USER-inspectable folder: $($script:PerElementScreenshotProof.root)"
        if ($SupplementalRuntimeProof -or $UserConfirmedACSupplementProof) {
            if ($UserConfirmedACSupplementProof) {
                $script:SupplementalIssueProof = Copy-SupplementalIssueScreenshotsToUserEvidence -Paths $paths -IssueFilter @("A", "C") -ProofClass "user-confirmed-ac-supplemental-runtime-proof"
                Step $paths "copied USER-confirmed A/C issue evidence folders and manifest: $($script:SupplementalIssueProof.manifest)"
            }
            else {
                $script:SupplementalIssueProof = Copy-SupplementalIssueScreenshotsToUserEvidence -Paths $paths
                Step $paths "copied supplemental A-F issue evidence folders and manifest: $($script:SupplementalIssueProof.manifest)"
            }
        }
    }

    Step $paths "settling Dashboard-first client before full-desktop screenshot"
    Start-Sleep -Milliseconds 1500
    Capture-Screen $paths "after_launch"
    if ($effectiveRunInteractionSelfQA) {
        $script:ShortVideoProof = New-ShortVideoProof -Paths $paths -SourceRoots @($paths.ElementScreenshotEvidenceRoot, $paths.InteractionEvidenceRoot, $paths.Root) -MinimumFrames 5
        if ($script:ShortVideoProof.status -ne "PASS") {
            throw "LV1 short video/frame-sequence proof missing or failed: $($script:ShortVideoProof.reason)"
        }
        Step $paths "generated mandatory LV1 short video proof: $($script:ShortVideoProof.path)"
        Step $paths "copied mandatory LV1 user-inspectable short video proof: $($script:ShortVideoProof.userInspectablePath)"
    }
    $script:ManifestStatus = "PASS"
    $exitCode = 0
}
catch {
    $script:ManifestStatus = "FAIL"
    $script:FailureMessage = $_.Exception.Message
    Step $paths "failure: $script:FailureMessage"
}
finally {
    foreach ($environmentName in $environmentNamesToRestore) {
        $previousValue = $previousEnvironment[$environmentName]
        if ($null -eq $previousValue) {
            Remove-Item -LiteralPath ("Env:\{0}" -f $environmentName) -ErrorAction SilentlyContinue
        }
        else {
            [Environment]::SetEnvironmentVariable($environmentName, [string]$previousValue, "Process")
        }
    }
    Stop-TrackedDesktopRuntime $paths "final cleanup"
    Save-Manifest $paths $pythonExe
    if ($script:ManifestStatus -eq "PASS") {
        Write-Output "PASS: FAM-006 Monitoring/HUD live desktop proof captured at $($paths.Root)"
    }
    else {
        Write-Output "FAIL: FAM-006 Monitoring/HUD live desktop proof failed at $($paths.Root)"
    }
}

exit $exitCode
