cmake_minimum_required(VERSION 3.4.0)
project(nptsne VERSION 0.0.2)

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

add_subdirectory(pybind11)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set(NPTSNE_FILES 
	src/TextureTsne.cpp
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
if(WIN32)
	get_target_property(QT_PLATFORM_PLUGIN_location Qt5::QWindowsIntegrationPlugin LOCATION)
	message(STATUS "Plugin Qt5::QWindowsIntegrationPlugin is at location ${QT_PLATFORM_PLUGIN_location}")
else()
	get_target_property(QT_PLATFORM_PLUGIN_location Qt5::QXcbIntegrationPlugin LOCATION)
	message(STATUS "Plugin Qt5::QXcbIntegrationPlugin is at location ${QT_PLATFORM_PLUGIN_location}")
endif()

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


set(HDIDR_BUILD_DIR "${HDI_BLD_ROOT}/dimensionality_reduction") 
set(HDICL_BUILD_DIR "${HDI_BLD_ROOT}/clustering") 
set(HDIDA_BUILD_DIR "${HDI_BLD_ROOT}/data") 
set(HDIUI_BUILD_DIR "${HDI_BLD_ROOT}/utils") 

find_library(HDIDR NAMES hdidimensionalityreduction.lib PATHS ${HDIDR_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE}) 
find_library(HDICL NAMES hdiclustering.lib PATHS ${HDICL_BUILD_DIR}  PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
find_library(HDIDA NAMES hdidata.lib PATHS ${HDIDA_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
find_library(HDIUI NAMES hdiutils.lib PATHS ${HDIUI_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})

target_link_libraries(nptsne PUBLIC ${HDIDR} ${HDICL} ${HDIDA} ${HDIUI})
target_link_libraries(nptsne PUBLIC ${Qt5Widgets_LIBRARIES} ${QtCore_LIBRARIES} ${QtOpenGL_LIBRARIES})
target_link_libraries(nptsne PUBLIC pybind11::module)

IF(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	target_link_libraries (nptsne PUBLIC "${FLANN_BUILD_DIR}/${CMAKE_BUILD_TYPE}/flann_cpp_s.lib")
ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	target_link_libraries(nptsne PUBLIC ${OPENGL_LIBRARIES})
	target_link_libraries(nptsne PUBLIC "${FLANN_BUILD_DIR}/${CMAKE_BUILD_TYPE}/lib/libflann_cpp.so")
ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")

MESSAGE( STATUS "Command line project: " nptsne )

# VisualStudio (or similar IDE) folder
set_target_properties(nptsne PROPERTIES FOLDER "Python bindings")
IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	set_target_properties(nptsne PROPERTIES 
		BUILD_WITH_INSTALL_RPATH TRUE
		INSTALL_RPATH_USE_LINK_PATH TRUE
		INSTALL_RPATH "\$ORIGIN/")
ENDIF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")

INSTALL(TARGETS nptsne LIBRARY DESTINATION nptsne)
message(STATUS "adding ${QT_PLATFORM_PLUGIN_location}")
INSTALL(FILES ${QT_PLATFORM_PLUGIN_location}  DESTINATION nptsne/platform)
INSTALL(FILES ${QtCore_location} ${Qt5OpenGL_location} ${Qt5Widgets_location}  DESTINATION nptsne)
INSTALL(FILES ./src/py/__init__.py DESTINATION nptsne)
