Set WshShell = CreateObject("WScript.Shell")
Set Fso = CreateObject("Scripting.FileSystemObject")

PythonwPath = "C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"
RootDir = Fso.GetParentFolderName(WScript.ScriptFullName)
LauncherPath = Fso.BuildPath(RootDir, "desktop\orin_desktop_launcher.pyw")

WshShell.Run """" & PythonwPath & """ """ & LauncherPath & """", 0

Set Fso = Nothing
Set WshShell = Nothing
