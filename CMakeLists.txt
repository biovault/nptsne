## Currently no APPLE build support
cmake_minimum_required(VERSION 3.4.0)
project(nptsne VERSION 0.1.0)

# pybind11 is included as a submodule
add_subdirectory(pybind11)

include(FindPythonInterp)
find_package(PythonInterp REQUIRED)
set(PYBIND11_PYTHON_VERSION "${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}" CACHE STRING "" FORCE)
message (STATUS "The pybind version is ${PYBIND11_PYTHON_VERSION}") 
message (STATUS "The python executable is at ${PYTHON_EXECUTABLE}") 

include(FindOpenGL)
list(APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
if(WIN32)
	get_filename_component(PYDIR "${PYTHON_EXECUTABLE}" DIRECTORY) 
	set (PYCMAKE "${PYDIR}/../../Library/lib/cmake")
	list(APPEND CMAKE_PREFIX_PATH  "${PYCMAKE}")
	message (STATUS "Prefix path ${CMAKE_PREFIX_PATH}")
endif() 
set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)

#set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake) 
# Need at least C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(SKBUILD)
  message(STATUS "The project is built using scikit-build")
endif()


set(PYBIND11_PYTHON_VERSION "3" CACHE STRING "")



if(WIN32) 
	set(PYBIND11_CPP_STANDARD "/std:c++14" CACHE STRING "" FORCE) 
else(WIN32)
	set(PYBIND11_CPP_STANDARD "-std=c++14" CACHE STRING "" FORCE)
	if(EXISTS "/etc/centos-release")
		set(GCC_EXPECTED_VERSION 7.3.1)
		set(PLATFORM_IS_CENTOS TRUE CACHE BOOL "TRUE if build platform is centOS" FORCE)
	else()
		set(GCC_EXPECTED_VERSION 5.4.0)
		set(PLATFORM_IS_CENTOS FALSE CACHE BOOL "TRUE if build platform is centOS" FORCE)		 
	endif()
	if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS GCC_EXPECTED_VERSION)
		message(FATAL_ERROR "GCC: nptsne requires version ${GCC_EXPECTED_VERSION} to build but found ${CMAKE_CXX_COMPILER_VERSION}")
		if(PLATFORM_IS_CENTOS)
			message(FATAL_ERROR "GCC: On CentOS remember to scl enable devtoolset-7")
		endif()
	endif()
endif(WIN32)

message(STATUS "${PYBIND11_CPP_STANDARD}")



set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set(NPTSNE_FILES 
	nptsne_src/TextureTsne.cpp
	nptsne_src/TextureTsneExtended.cpp
	nptsne_src/LibInfo.cpp
	nptsne_src/nptSNEBind.cpp
)

pybind11_add_module(nptsne ${NPTSNE_FILES})
if(WIN32) 
	set(HDI_BLD_ROOT "../bld/hdi" CACHE STRING "Root of hdi build directory" FORCE) 
else()
	# HDI LINUX builds target two separate directories bld_centos & bld_ubuntu
	if(PLATFORM_IS_CENTOS) 
		set(HDI_BLD_ROOT "../bld_centos/hdi" CACHE STRING "Root of hdi build directory" FORCE)  	
	else()
		set(HDI_BLD_ROOT "../bld_ubuntu/hdi" CACHE STRING "Root of hdi build directory" FORCE)  	
	endif()
endif()

target_compile_definitions(nptsne PUBLIC "-DPYBIND11_PYTHON_VERSION=${PYTHON_MAJ_MIN}")  



find_package(Qt5Core REQUIRED)
get_target_property(QtCore_location Qt5::Core LOCATION)
find_package(Qt5OpenGL REQUIRED)
get_target_property(Qt5OpenGL_location Qt5::OpenGL LOCATION)
find_package(Qt5Widgets REQUIRED)
get_target_property(Qt5Widgets_location Qt5::Widgets LOCATION)
find_package(Qt5Gui REQUIRED)
get_target_property(Qt5Gui_location Qt5::Gui LOCATION)
find_package(Qt5DBus REQUIRED)
get_target_property(Qt5DBus_location Qt5::DBus LOCATION) 
get_filename_component(Qt5_lib_dir "${QtCore_location}" DIRECTORY)
message(STATUS "Path for qt libs: ${Qt5_lib_dir}")
if(UNIX)
  find_library(Qt5XcbQpa_LIBRARIES NAMES Qt5XcbQpa PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  get_filename_component(Qt5XcbQpa_location ${Qt5XcbQpa_LIBRARIES} REALPATH)
  message(STATUS "Qt5XcbQpa: ${Qt5XcbQpa_location}")
  find_library(ICUI18N_LIB NAMES icui18n PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  get_filename_component(ICUI18N_location ${ICUI18N_LIB} REALPATH)
  message(STATUS "ICUI18N: ${ICUI18N_location}")  
  find_library(ICUUC_LIB NAMES icuuc PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  get_filename_component(ICUUC_location ${ICUUC_LIB} REALPATH)
  message(STATUS "ICUUC: ${ICUUC_location}")  
  find_library(ICUDATA_LIB NAMES icudata PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  get_filename_component(ICUDATA_location ${ICUDATA_LIB} REALPATH)
  message(STATUS "ICUDATA: ${ICUDATA_location}")    
endif(UNIX)

find_package(OpenGL)

if(UNIX)
	find_package(LZ4 REQUIRED)
endif(UNIX)	

if(WIN32)
	get_target_property(QT_PLATFORM_PLUGIN_location Qt5::QWindowsIntegrationPlugin LOCATION)
	message(STATUS "Plugin Qt5::QWindowsIntegrationPlugin is at location ${QT_PLATFORM_PLUGIN_location}")
else(WIN32)
	get_target_property(QT_PLATFORM_PLUGIN_location Qt5::QXcbIntegrationPlugin LOCATION)
	message(STATUS "Plugin Qt5::QXcbIntegrationPlugin is at location ${QT_PLATFORM_PLUGIN_location}")
endif(WIN32)

include_directories ("${Qt5Widgets_INCLUDE_DIRS}")
include_directories ("${CMAKE_SOURCE_DIR}")
include_directories ("..")
include_directories ("${CMAKE_CURRENT_BINARY_DIR}/../../../hdi/visualization")

find_package(OpenMP REQUIRED)
if(OPENMP_FOUND)
	message (STATUS "OpenMP found")
	set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()
	
message( STATUS "HDI_BLD_ROOT: ${HDI_BLD_ROOT}" )

set(HDIDR_BUILD_DIR "${HDI_BLD_ROOT}/dimensionality_reduction") 
set(HDICL_BUILD_DIR "${HDI_BLD_ROOT}/clustering") 
set(HDIDA_BUILD_DIR "${HDI_BLD_ROOT}/data") 
set(HDIUI_BUILD_DIR "${HDI_BLD_ROOT}/utils") 

if(WIN32)
	find_library(HDIDR NAMES hdidimensionalityreduction.lib PATHS ${HDIDR_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE}) 
	find_library(HDICL NAMES hdiclustering.lib PATHS ${HDICL_BUILD_DIR}  PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
	find_library(HDIDA NAMES hdidata.lib PATHS ${HDIDA_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
	find_library(HDIUI NAMES hdiutils.lib PATHS ${HDIUI_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
else(WIN32)
	find_library(HDIDR NAMES libhdidimensionalityreduction.a PATHS ${HDIDR_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE}) 
	find_library(HDICL NAMES libhdiclustering.a PATHS ${HDICL_BUILD_DIR}  PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
	find_library(HDIDA NAMES libhdidata.a PATHS ${HDIDA_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
	find_library(HDIUI NAMES libhdiutils.a PATHS ${HDIUI_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})	
endif(WIN32)

target_link_libraries(nptsne PUBLIC ${HDIDR} ${HDICL} ${HDIDA} ${HDIUI})
target_link_libraries(nptsne PUBLIC ${Qt5Widgets_LIBRARIES} ${QtCore_LIBRARIES} ${QtOpenGL_LIBRARIES})
target_link_libraries(nptsne PUBLIC pybind11::module)

if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	target_link_libraries (nptsne PUBLIC "${FLANN_BUILD_DIR}/${CMAKE_BUILD_TYPE}/flann_cpp_s.lib")
endif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	target_link_libraries(nptsne PUBLIC ${OPENGL_LIBRARIES})
	if(PLATFORM_IS_CENTOS)
		# centos
		target_link_libraries(nptsne PUBLIC "/usr/lib64/liblz4.so" )
		target_link_libraries(nptsne PUBLIC "/usr/lib64/libflann_cpp.so.1.8.4" )
	else()
		# ubuntu
		target_link_libraries(nptsne PUBLIC "/usr/lib/x86_64-linux-gnu/liblz4.so" )
		target_link_libraries(nptsne PUBLIC "/usr/lib/x86_64-linux-gnu/libflann_cpp.so.1.8.4" )		
	endif()
	target_link_libraries(nptsne PUBLIC "${OPENGL_gl_LIBRARY}")
#	target_link_libraries(nptsne PUBLIC efence)
endif(${CMAKE_SYSTEM_NAME} MATCHES "Linux")

message( STATUS "Command line project: " nptsne )

# VisualStudio (or similar IDE) folder
set_target_properties(nptsne PROPERTIES FOLDER "Python bindings")
if(UNIX)
	set_target_properties(nptsne PROPERTIES 
		SKIP_BUILD_RPATH FALSE
		BUILD_WITH_INSTALL_RPATH ON
		INSTALL_RPATH "\$ORIGIN")
      set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,origin")
      set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-z,origin")
      set(CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG "-Wl,-z,origin,-rpath")
endif(UNIX)
message(STATUS "SHARED_LINKER_FLAGS: ${CMAKE_SHARED_LINKER_FLAGS}")
install(TARGETS nptsne LIBRARY DESTINATION nptsne)
message(STATUS "adding ${QT_PLATFORM_PLUGIN_location}")
install(FILES ${QT_PLATFORM_PLUGIN_location}  DESTINATION nptsne/plugins/platforms)

if(WIN32)
	install(FILES ${QtCore_location} ${Qt5OpenGL_location} ${Qt5Widgets_location} ${Qt5Gui_location} ${Qt5DBus_location} DESTINATION nptsne)
else(WIN32)
	install(FILES ${QtCore_location} DESTINATION nptsne RENAME libQt5Core.so.5)
	install(FILES ${Qt5OpenGL_location} DESTINATION nptsne RENAME libQt5OpenGL.so.5)
	install(FILES ${Qt5Widgets_location} DESTINATION nptsne RENAME libQt5Widgets.so.5)
	install(FILES ${Qt5Gui_location} DESTINATION nptsne RENAME libQt5Gui.so.5)	
	install(FILES ${Qt5DBus_location} DESTINATION nptsne/lib RENAME libQt5DBus.so.5)	
	install(FILES ${Qt5XcbQpa_location} DESTINATION nptsne/lib RENAME libQt5XcbQpa.so.5)
	install(FILES ${ICUDATA_location}  DESTINATION nptsne RENAME libicudata.so.58)
	install(FILES ${ICUI18N_location}  DESTINATION nptsne RENAME libicui18n.so.58)
	install(FILES ${ICUUC_location}  DESTINATION nptsne RENAME libicuuc.so.58)
	install(DIRECTORY DESTINATION nptsne/plugins)
	install(DIRECTORY DESTINATION nptsne/plugins/xcbglintegrations)
	install(FILES ${Qt5_lib_dir}/../plugins/xcbglintegrations/libqxcb-egl-integration.so
        PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ
                    GROUP_EXECUTE GROUP_READ
					WORLD_EXECUTE WORLD_READ
			DESTINATION nptsne/plugins/xcbglintegrations )
    install(FILES ${Qt5_lib_dir}/../plugins/xcbglintegrations/libqxcb-glx-integration.so
        PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ
                    GROUP_EXECUTE GROUP_READ
					WORLD_EXECUTE WORLD_READ
			DESTINATION nptsne/plugins/xcbglintegrations )	
endif(WIN32)

# Use prebuilt libflann and liblz4
if(UNIX)
	message(STATUS "Deploying lz4")
	if(PLATFORM_IS_CENTOS)
		install(FILES "/usr/lib64/liblz4.so.1.7.5" DESTINATION nptsne RENAME liblz4.so)
		install(FILES "/usr/lib64/libflann_cpp.so.1.8.4" DESTINATION nptsne RENAME libflann_cpp.so.1.8)
		install(FILES "${Qt5_lib_dir}/libpcre.so.1.2.11" DESTINATION nptsne RENAME libpcre.so.1)
		install(FILES "${Qt5_lib_dir}/libz.so.1.2.11" DESTINATION nptsne RENAME libz.so.1)	
		install(FILES "${Qt5_lib_dir}/libpng16.so.16.37.0" DESTINATION nptsne RENAME libpng16.so.16)	
		install(FILES "${Qt5_lib_dir}/libxcb.so.1.1.0" DESTINATION nptsne RENAME libxcb.so.1)	
		install(FILES "${Qt5_lib_dir}/libglib-2.0.so.0.5600.2" DESTINATION nptsne RENAME libglib-2.0.so.0)	
		install(FILES "${Qt5_lib_dir}/libgthread-2.0.so.0.5600.2" DESTINATION nptsne RENAME libgthread-2.0.so.0)
		install(FILES "${Qt5_lib_dir}/libstdc++.so.6.0.25" DESTINATION nptsne RENAME libstdc++.so.6)	
		install(FILES "${Qt5_lib_dir}/libgcc_s.so.1" DESTINATION nptsne RENAME libgcc_s.so.1)							
		install(FILES "${Qt5_lib_dir}/libgcc_s.so.1" DESTINATION nptsne RENAME libgthread-2.0.so.0)	
	else()
		install(FILES "/usr/lib/x86_64-linux-gnu/liblz4.so.1.7.1" DESTINATION nptsne RENAME liblz4.so)
		install(FILES "/usr/lib/x86_64-linux-gnu/libflann_cpp.so.1.8.4" DESTINATION nptsne RENAME libflann_cpp.so)
	endif()	
endif(UNIX)	
install(FILES ./nptsne/deploy__init__.py DESTINATION nptsne RENAME __init__.py)
