Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"" ""C:\Jarvis\main.py"" --boot-profile auto_handoff_skip_import --audio-mode quiet", 0
Set WshShell = Nothing
