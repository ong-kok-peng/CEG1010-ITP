@echo off
echo Checking if Python 3 is installed...
where /r "%PROGRAMFILES%" python3* > nul
if ERRORLEVEL 0 (
    echo Python 3 is installed! Launching the program.
    timeout /t 2 /nobreak > nul
    start /b pythonw.exe GUIMainProgram.py
    exit
)
if ERRORLEVEL 1 (
    echo Python 3 is not installed; cannot launch the program.
    echo Download and install now at https://www.python.org/downloads/
    pause
)
