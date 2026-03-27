@echo off
title QR Code Generator
color 0A

echo.
echo ========================================
echo   Encrypted QR Code Generator
echo ========================================
echo.

REM Set your password here
set PASSWORD=Canada..2026

echo Generating QR codes for 84 attendees...
echo.

REM Run the Python script (from parent directory)
cd ..
py generate_qr_codes.py qr-generator\attendees.xlsx -o qr-generator\qr_output -p "%PASSWORD%"
cd qr-generator

echo.
echo ========================================
echo   QR codes generated successfully!
echo ========================================
echo.
echo Your QR code files are in: qr_output/
echo.
pause
