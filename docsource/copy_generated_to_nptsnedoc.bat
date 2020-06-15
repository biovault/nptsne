xcopy /Y /S %~dp0\build\generated %~dp0\nptsnedoc\source\generated\
copy /Y %~dp0\build\nptsne_module.rst %~dp0\nptsnedoc\source\
copy /Y %~dp0\..\version.txt %~dp0\nptsnedoc\