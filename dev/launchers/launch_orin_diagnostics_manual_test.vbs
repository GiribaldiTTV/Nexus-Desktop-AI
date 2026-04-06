Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

PythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
ScriptDir = Fso.GetParentFolderName(WScript.ScriptFullName)
DevDir = Fso.GetParentFolderName(ScriptDir)
RootDir = Fso.GetParentFolderName(DevDir)
DiagnosticsScript = Fso.BuildPath(Fso.BuildPath(RootDir, "desktop"), "orin_diagnostics.pyw")
RuntimeLogPath = Fso.BuildPath(Fso.BuildPath(Fso.BuildPath(DevDir, "logs"), "diagnostics_ui"), "Runtime_manual_diagnostics_test.txt")

WshShell.Run """" & PythonwPath & """ """ & DiagnosticsScript & """ --manual-test --runtime-log """ & RuntimeLogPath & """", 0

Set Fso = Nothing
Set WshShell = Nothing
