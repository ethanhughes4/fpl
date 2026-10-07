@echo off
rem Weekly brief: python -m fpl, then the page (D298). Never installs anything (D320).
rem Runs from the repo root wherever it is started (D321).
cd /d "%~dp0"
python -m fpl %*
if errorlevel 1 goto fail
cd web
npm run dev -- --open --strictPort --port 5173
if errorlevel 1 goto fail
exit /b 0

:fail
set CODE=%errorlevel%
if %CODE%==0 set CODE=1
rem Double-clicked from Explorer: keep the window open so the message can be read.
rem BRIEF_NO_PAUSE=1 turns this off (the tests set it).
if not defined BRIEF_NO_PAUSE echo %cmdcmdline% | find /i "%~nx0" >nul && pause
exit /b %CODE%
