REM sphinx-build [options] source output
rd /s /q %~dp0\source\generated
rd /s /q %~dp0\build\generated
rd /s /q %~dp0\nptsnedoc\source\generated
sphinx-build -b rst %~dp0\source %~dp0\build
xcopy /Y /S %~dp0\build\generated %~dp0\nptsnedoc\source\generated\
copy /Y %~dp0\build\nptsne_module.rst %~dp0\nptsnedoc\source\
copy /Y %~dp0\..\version.txt %~dp0\nptsnedoc\