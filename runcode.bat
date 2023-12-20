@echo off
setlocal enabledelayedexpansion

FOR /F %%i IN (commands.txt) DO (
    echo %%i
    %%i
    echo %%i >> log.txt
    echo %date% %time% >> log.txt
)