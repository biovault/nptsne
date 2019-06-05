cmake_minimum_required(VERSION 3.4.0)
project(nptsne VERSION 0.1.0)

include(FindOpenGL)
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
set(CMAKE_BUILD_TYPE Debug CACHE STRING "" FORCE)

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
endif(WIN32)

message(STATUS "${PYBIND11_CPP_STANDARD}")

# pybind11 is included as a submodule
add_subdirectory(pybind11)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set(NPTSNE_FILES 
	src/TextureTsne.cpp
	src/TextureTsneExtended.cpp
	src/LibInfo.cpp
	src/nptSNEBind.cpp
)

pybind11_add_module(nptsne ${NPTSNE_FILES})
set(QT_ROOT_DIR "C:/tools/Anaconda3/Library/bin")

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
IF(UNIX AND NOT APPLE)
  #Qt5XcbQpa
  FIND_LIBRARY(Qt5XcbQpa_LIBRARIES NAMES Qt5XcbQpa PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  GET_FILENAME_COMPONENT(Qt5XcbQpa_location ${Qt5XcbQpa_LIBRARIES} REALPATH)
  message(STATUS "Qt5XcbQpa: ${Qt5XcbQpa_location}")
  FIND_LIBRARY(ICUI18N_LIB NAMES icui18n PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  GET_FILENAME_COMPONENT(ICUI18N_location ${ICUI18N_LIB} REALPATH)
  message(STATUS "ICUI18N: ${ICUI18N_location}")  
  FIND_LIBRARY(ICUUC_LIB NAMES icuuc PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  GET_FILENAME_COMPONENT(ICUUC_location ${ICUUC_LIB} REALPATH)
  message(STATUS "ICUUC: ${ICUUC_location}")  
  FIND_LIBRARY(ICUDATA_LIB NAMES icudata PATHS "${Qt5_lib_dir}" NO_DEFAULT_PATH)
  GET_FILENAME_COMPONENT(ICUDATA_location ${ICUDATA_LIB} REALPATH)
  message(STATUS "ICUDATA: ${ICUDATA_location}")    
ENDIF(UNIX AND NOT APPLE)

#	libicui18n.so.58 => not found
#	libicuuc.so.58 => not found
#	libicudata.so.58 => not found

find_package(OpenGL)

if (UNIX)
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
if (OPENMP_FOUND)
	message (STATUS "OpenMP found")
	set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

MESSAGE( STATUS "HDI_BLD_ROOT: ${HDI_BLD_ROOT}" )

set(HDIDR_BUILD_DIR "${HDI_BLD_ROOT}/dimensionality_reduction") 
set(HDICL_BUILD_DIR "${HDI_BLD_ROOT}/clustering") 
set(HDIDA_BUILD_DIR "${HDI_BLD_ROOT}/data") 
set(HDIUI_BUILD_DIR "${HDI_BLD_ROOT}/utils") 

if (WIN32)
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

IF(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	target_link_libraries (nptsne PUBLIC "${FLANN_BUILD_DIR}/${CMAKE_BUILD_TYPE}/flann_cpp_s.lib")
ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	target_link_libraries(nptsne PUBLIC ${OPENGL_LIBRARIES})
	target_link_libraries(nptsne PUBLIC "/usr/lib/x86_64-linux-gnu/liblz4.so" )
	target_link_libraries(nptsne PUBLIC "${FLANN_BUILD_DIR}/lib/libflann_cpp.so")
	#MESSAGE( STATUS "Linking LZ4_LIBRARIES: ${LZ4_LIBRARIES}" )
	#target_link_libraries(nptsne PUBLIC ${LZ4_LIBRARIES})
	target_link_libraries(nptsne PUBLIC "${OPENGL_gl_LIBRARY}")
ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")

MESSAGE( STATUS "Command line project: " nptsne )

# VisualStudio (or similar IDE) folder
set_target_properties(nptsne PROPERTIES FOLDER "Python bindings")
IF(UNIX)
	set_target_properties(nptsne PROPERTIES 
		SKIP_BUILD_RPATH FALSE
		BUILD_WITH_INSTALL_RPATH ON
		INSTALL_RPATH "\$ORIGIN")
      set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,origin")
      set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-z,origin")
      set(CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG "-Wl,-z,origin,-rpath,")
ENDIF(UNIX)
message(STATUS "SHARED_LINKER_FLAGS: ${CMAKE_SHARED_LINKER_FLAGS}")
INSTALL(TARGETS nptsne LIBRARY DESTINATION nptsne)
message(STATUS "adding ${QT_PLATFORM_PLUGIN_location}")
INSTALL(FILES ${QT_PLATFORM_PLUGIN_location}  DESTINATION nptsne/platforms)

if (WIN32)
	INSTALL(FILES ${QtCore_location} ${Qt5OpenGL_location} ${Qt5Widgets_location} ${Qt5Gui_location} ${Qt5DBus_location} DESTINATION nptsne)
else(WIN32)
	INSTALL(FILES ${QtCore_location} DESTINATION nptsne RENAME libQt5Core.so.5)
	INSTALL(FILES ${Qt5OpenGL_location} DESTINATION nptsne RENAME libQt5OpenGL.so.5)
	INSTALL(FILES ${Qt5Widgets_location} DESTINATION nptsne RENAME libQt5Widgets.so.5)
	INSTALL(FILES ${Qt5Gui_location} DESTINATION nptsne RENAME libQt5Gui.so.5)	
	INSTALL(FILES ${Qt5DBus_location} DESTINATION nptsne RENAME libQt5DBus.so.5)	
	INSTALL(FILES ${Qt5XcbQpa_location} DESTINATION nptsne RENAME libQt5XcbQpa.so.5)
	INSTALL(FILES ${ICUDATA_location}  DESTINATION nptsne RENAME libicudata.so.58)
	INSTALL(FILES ${ICUI18N_location}  DESTINATION nptsne RENAME libicui18n.so.58)
	INSTALL(FILES ${ICUUC_location}  DESTINATION nptsne RENAME libicuuc.so.58)
	INSTALL(DIRECTORY DESTINATION nptsne/plugins)
	INSTALL(DIRECTORY DESTINATION nptsne/plugins/xcbglintegrations)
	INSTALL(FILES ${Qt5_lib_dir}/../plugins/xcbglintegrations/libqxcb-egl-integration.so
        PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ
                    GROUP_EXECUTE GROUP_READ
					WORLD_EXECUTE WORLD_READ
			DESTINATION nptsne/plugins/xcbglintegrations )
    INSTALL(FILES ${Qt5_lib_dir}/../plugins/xcbglintegrations/libqxcb-glx-integration.so
        PERMISSIONS OWNER_EXECUTE OWNER_WRITE OWNER_READ
                    GROUP_EXECUTE GROUP_READ
					WORLD_EXECUTE WORLD_READ
			DESTINATION nptsne/plugins/xcbglintegrations )		
endif(WIN32)

# Shouldn't lz4 this be a static link?
if (UNIX)
	#string (REPLACE ";" " " LZLIST "${LZ4_LIBRARIES}")
	message(STATUS "LZLIST: /usr/lib/x86_64-linux-gnu/liblz4.so.1.7.1")
	INSTALL(FILES "/usr/lib/x86_64-linux-gnu/liblz4.so.1.7.1" DESTINATION nptsne RENAME liblz4.so)
	INSTALL(FILES "${FLANN_BUILD_DIR}/lib/libflann_cpp.so.1.8.4" DESTINATION nptsne RENAME libflann_cpp.so)
endif(UNIX)	
INSTALL(FILES ./src/py/__init__.py DESTINATION nptsne)
