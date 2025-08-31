@echo off
title Pharmacy POS System
cd /d D:\POS

echo Pharmacy POS System
echo ===================
echo Starting application...

python main.py

if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start the application
    echo Please check if Python is installed and in your PATH
    echo.
    pause
)