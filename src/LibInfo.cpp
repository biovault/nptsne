#include "LibInfo.h"

#if !defined(_WIN64) && !defined(_WIN32) 

#include <dlfcn.h>
QFileInfo LibInfo::get_lib_info() {
	Dl_info dlInfo;
	dladdr(reinterpret_cast<const void *>(QApplication::beep), &dlInfo);
	if (dlInfo.dli_sname != NULL && dlInfo.dli_saddr != NULL) {
		return QFileInfo(QString::fromLocal8Bit(dlInfo.dli_fname));
	}
	return QFileInfo("");
}

#else
#include <windows.h>
EXTERN_C IMAGE_DOS_HEADER __ImageBase;

QFileInfo LibInfo::get_lib_info() {
	wchar_t fileName[MAX_PATH];
	GetModuleFileNameW(
		reinterpret_cast<HINSTANCE>(&__ImageBase),
		fileName,
		MAX_PATH 
	);
	return QFileInfo(QString::fromWCharArray(fileName));
}

	
#endif