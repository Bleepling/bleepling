Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

base = fso.GetParentFolderName(WScript.ScriptFullName)
cmd = """" & base & "\start_bleepling_silent.bat" & """"

shell.Run cmd, 0, False