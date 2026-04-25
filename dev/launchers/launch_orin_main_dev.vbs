Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

PythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
ScriptDir = Fso.GetParentFolderName(WScript.ScriptFullName)
DevDir = Fso.GetParentFolderName(ScriptDir)
RootDir = Fso.GetParentFolderName(DevDir)
MainPath = Fso.BuildPath(RootDir, "main.py")

WshShell.Run """" & PythonwPath & """ """ & MainPath & """ --boot-profile manual --audio-mode voice", 0

Set Fso = Nothing
Set WshShell = Nothing
