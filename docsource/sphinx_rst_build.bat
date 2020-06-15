REM sphinx-build [options] source output
rd /s /q %~dp0\source\generated
rd /s /q %~dp0\build\generated
rd /s /q %~dp0\nptsnedoc\source\generated
sphinx-build -b rst %~dp0\source %~dp0\build
