@echo off
title Instalador OfficeIA Pro
echo Instalando integracao com Microsoft Word, Excel e Adobe PDF...

mkdir "C:\OfficeIA" 2>nul
copy /Y "%~dp0manifest.xml" "C:\OfficeIA\manifest.xml" >nul

reg add "HKCU\Software\Microsoft\Office\16.0\WEF\Developer" /v "OfficeIA_Addin" /t REG_SZ /d "C:\OfficeIA\manifest.xml" /f >nul

if exist "C:\Program Files\Adobe\Acrobat DC\Acrobat\Javascripts" (
copy /Y "%~dp0OfficeIA_Adobe.js" "C:\Program Files\Adobe\Acrobat DC\Acrobat\Javascripts\OfficeIA_Adobe.js" >nul
)
if exist "C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\Javascripts" (
copy /Y "%~dp0OfficeIA_Adobe.js" "C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\Javascripts\OfficeIA_Adobe.js" >nul
)
echo.
echo ====================================================
echo  INSTALACAO CONCLUIDA COM SUCESSO!
echo  Abra o Word, Excel ou Adobe PDF para usar.
echo ====================================================
pause
