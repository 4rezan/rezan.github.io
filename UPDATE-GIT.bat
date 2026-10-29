@echo off
setlocal
cd /d "%~dp0"

echo Starting Rezan Portfolio GitHub uploader...
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0github_updater.py"
  goto :eof
)
where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0github_updater.py"
  goto :eof
)
echo Python was not found. Install Python 3 and enable the Python launcher or add Python to PATH.
pause