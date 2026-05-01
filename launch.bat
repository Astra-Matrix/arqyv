@echo off
:: ARQYV launcher — no console window, native Windows Qt plugin forced.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set QT_QPA_PLATFORM=windows
start "" "C:\Python313\pythonw.exe" "%~dp0run.py"
