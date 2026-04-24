Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

RootDir = Fso.GetParentFolderName(WScript.ScriptFullName)
LauncherPath = Fso.BuildPath(RootDir, "desktop\orin_desktop_launcher.pyw")
PreferredPythonwPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Python\pythoncore-3.14-64\pythonw.exe"

Function Quote(value)
    Quote = """" & value & """"
End Function

Function CommandExists(commandName)
    Dim exec
    On Error Resume Next
    Set exec = WshShell.Exec("cmd /c where /Q " & commandName)
    If Err.Number <> 0 Then
        Err.Clear
        CommandExists = False
        Exit Function
    End If
    On Error GoTo 0

    Do While exec.Status = 0
        WScript.Sleep 25
    Loop

    CommandExists = (exec.ExitCode = 0)
    Set exec = Nothing
End Function

Function EnvFlagEnabled(name)
    Dim value
    value = LCase(Trim(WshShell.ExpandEnvironmentStrings("%" & name & "%")))
    EnvFlagEnabled = (value = "1" Or value = "true" Or value = "yes" Or value = "on")
End Function

Function PyLauncherSupportsPython3()
    Dim exec
    Dim output

    On Error Resume Next
    Set exec = WshShell.Exec("cmd /c py -0p")
    If Err.Number <> 0 Then
        Err.Clear
        PyLauncherSupportsPython3 = False
        Exit Function
    End If
    On Error GoTo 0

    Do While exec.Status = 0
        WScript.Sleep 25
    Loop

    output = ""
    If Not exec.StdOut.AtEndOfStream Then
        output = output & exec.StdOut.ReadAll()
    End If
    If Not exec.StdErr.AtEndOfStream Then
        output = output & vbCrLf & exec.StdErr.ReadAll()
    End If
    output = LCase(output)

    PyLauncherSupportsPython3 = (exec.ExitCode = 0 And InStr(output, "-v:3") > 0)
    Set exec = Nothing
End Function

Function ResolvePythonLaunchCommand()
    If Not EnvFlagEnabled("NEXUS_DESKTOP_SKIP_PREFERRED_PYTHONW") And Fso.FileExists(PreferredPythonwPath) Then
        ResolvePythonLaunchCommand = Quote(PreferredPythonwPath)
        Exit Function
    End If

    If CommandExists("pyw.exe") And PyLauncherSupportsPython3() Then
        ResolvePythonLaunchCommand = "pyw.exe -3"
        Exit Function
    End If

    If CommandExists("pythonw.exe") Then
        ResolvePythonLaunchCommand = "pythonw.exe"
        Exit Function
    End If

    ResolvePythonLaunchCommand = ""
End Function

If Not Fso.FileExists(LauncherPath) Then
    MsgBox "Nexus Desktop AI could not start because the desktop launcher script was not found:" & vbCrLf & vbCrLf & LauncherPath, vbCritical, "Nexus Desktop AI"
    WScript.Quit 1
End If

PythonLaunchCommand = ResolvePythonLaunchCommand()

If PythonLaunchCommand = "" Then
    MsgBox "Nexus Desktop AI could not start because a windowed Python launcher was not found." & vbCrLf & vbCrLf & "Checked:" & vbCrLf & PreferredPythonwPath & vbCrLf & "pyw.exe -3 with a registered Python 3 launcher" & vbCrLf & "pythonw.exe", vbCritical, "Nexus Desktop AI"
    WScript.Quit 1
End If

WshShell.Run PythonLaunchCommand & " " & Quote(LauncherPath), 0

Set Fso = Nothing
Set WshShell = Nothing
