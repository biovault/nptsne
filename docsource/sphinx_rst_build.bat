REM sphinx-build [options] source output
rd /s /q .\source\generated
rd /s /q .\build\generated
rd /s /q .\nptsnedoc\source\generated
sphinx-build -b rst .\source .\build
xcopy /Y /S .\build\generated .\nptsnedoc\source\generated\
copy /Y .\build\nptsne_module.rst .\nptsnedoc\source\
copy /Y ..\version.txt .\nptsnedoc\