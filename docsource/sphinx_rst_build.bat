REM sphinx-build [options] source output
rd /s /q %~dp0\source\generated
rd /s /q %~dp0\build\generated
rd /s /q %~dp0\nptsnedoc\source\generated
set SPHINX_BUILD=sphinx-build
IF "%1"=="" GOTO Default
    set SPHINX_BUILD=%1
:Default
%SPHINX_BUILD% -b rst %~dp0\source %~dp0\build
