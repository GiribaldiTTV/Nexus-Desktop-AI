Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

PythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
ScriptDir = Fso.GetParentFolderName(WScript.ScriptFullName)
TargetScript = Fso.BuildPath(ScriptDir, "orin_dev_launcher.pyw")

WshShell.Run """" & PythonwPath & """ """ & TargetScript & """", 0

Set Fso = Nothing
Set WshShell = Nothing
