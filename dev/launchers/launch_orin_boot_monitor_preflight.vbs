Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

PythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
ScriptDir = Fso.GetParentFolderName(WScript.ScriptFullName)
DevDir = Fso.GetParentFolderName(ScriptDir)
TargetScript = Fso.BuildPath(DevDir, "orin_boot_monitor_preflight.py")

WshShell.Run """" & PythonwPath & """ """ & TargetScript & """", 0

Set Fso = Nothing
Set WshShell = Nothing
