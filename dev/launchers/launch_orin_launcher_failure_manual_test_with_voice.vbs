Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")
Set Env = WshShell.Environment("PROCESS")

PythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
ScriptDir = Fso.GetParentFolderName(WScript.ScriptFullName)
DevDir = Fso.GetParentFolderName(ScriptDir)
RootDir = Fso.GetParentFolderName(DevDir)

Env("JARVIS_HARNESS_TARGET_SCRIPT") = Fso.BuildPath(Fso.BuildPath(DevDir, "targets"), "orin_manual_failure_target.pyw")
Env("JARVIS_HARNESS_LOG_ROOT") = Fso.BuildPath(Fso.BuildPath(DevDir, "logs"), "manual_launcher_failure_test_with_voice")

LauncherPath = Fso.BuildPath(Fso.BuildPath(RootDir, "desktop"), "orin_desktop_launcher.pyw")
WshShell.Run """" & PythonwPath & """ """ & LauncherPath & """", 0

Set Env = Nothing
Set Fso = Nothing
Set WshShell = Nothing
