Set WshShell = CreateObject("WScript.Shell")
Set Env = WshShell.Environment("PROCESS")
Env("JARVIS_HARNESS_TARGET_SCRIPT") = "C:\Jarvis\dev\targets\jarvis_manual_startup_abort_target.pyw"
Env("JARVIS_HARNESS_LOG_ROOT") = "C:\Jarvis\dev\logs\manual_launcher_startup_abort_test"
Env("JARVIS_HARNESS_DISABLE_VOICE") = "1"
WshShell.Run """C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"" ""C:\Jarvis\desktop\jarvis_desktop_launcher.pyw""", 0
Set Env = Nothing
Set WshShell = Nothing
