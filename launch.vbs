' launch.vbs — Silent launcher for Bugzilla Tracker
' Runs server.py via pythonw.exe (no console window).
' Used by Task Scheduler on user logon.

Dim shell, scriptDir, cmd
Set shell = WScript.CreateObject("WScript.Shell")

' Resolve directory of this script
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

' Build command: pythonw hides the console window natively
cmd = "pythonw.exe """ & scriptDir & "server.py"""

' Run with window style 0 = hidden, bWaitOnReturn = False
shell.Run cmd, 0, False

Set shell = Nothing
