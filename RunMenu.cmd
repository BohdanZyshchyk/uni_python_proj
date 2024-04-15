@echo off
set REPOSITORY_DIR=%~dp0
call "python" menu/Menu.py || goto :do_exit

:do_exit
popd
pause
exit /b %ERRORLEVEL%