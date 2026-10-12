param(
    [string]$PythonPath = $env:NEXUS_VALIDATION_PYTHON
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

function Resolve-ValidationPython {
    $candidates = @()

    if ($PythonPath) {
        $candidates += $PythonPath
    }

    $repoKnownPython = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    $candidates += $repoKnownPython

    $pathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($pathPython -and $pathPython.Source) {
        $candidates += $pathPython.Source
    }

    foreach ($candidate in $candidates) {
        if (-not $candidate) {
            continue
        }

        if (-not (Test-Path -LiteralPath $candidate)) {
            continue
        }

        try {
            & $candidate -c "import PySide6" | Out-Null
            if ($LASTEXITCODE -eq 0) {
                return (Resolve-Path -LiteralPath $candidate).Path
            }
        }
        catch {
            continue
        }
    }

    throw "No Qt-capable Python interpreter found. Set NEXUS_VALIDATION_PYTHON to a python.exe with PySide6 installed."
}

function Invoke-ValidationStep {
    param(
        [string]$Label,
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    Write-Output ("FB038_SEAM2_VALIDATION|START|step=" + $Label)
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Validation step failed: $Label"
    }
    Write-Output ("FB038_SEAM2_VALIDATION|PASS|step=" + $Label)
}

$python = Resolve-ValidationPython
Push-Location $rootDir
try {
    Write-Output ("FB038_SEAM2_VALIDATION|PYTHON|" + $python)
    Invoke-ValidationStep -Label "pyside6_import" -FilePath $python -Arguments @("-c", "import PySide6; print(PySide6.__version__)")
    Invoke-ValidationStep -Label "desktop_entrypoint" -FilePath $python -Arguments @("dev\orin_desktop_entrypoint_validation.py")
    Invoke-ValidationStep -Label "interaction_baseline" -FilePath $python -Arguments @("dev\orin_interaction_baseline_validation.py")
    Invoke-ValidationStep -Label "saved_action_authoring_ui" -FilePath $python -Arguments @("dev\orin_saved_action_authoring_ui_validation.py")
    Invoke-ValidationStep -Label "diff_check" -FilePath "git" -Arguments @("diff", "--check")

    Write-Output "FB038_SEAM2_VALIDATION|PASS|all"
}
finally {
    Pop-Location
}
