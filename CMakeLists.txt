## Currently no APPLE build support
cmake_minimum_required(VERSION 3.4.0)
project(nptsne VERSION 0.2.0)

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

set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set(NPTSNE_FILES 
	nptsne_src/TextureTsne.cpp
	nptsne_src/TextureTsneExtended.cpp
	nptsne_src/nptSNEBind.cpp
)

pybind11_add_module(nptsne ${NPTSNE_FILES})

find_package(OpenGL)

include_directories ("glfw/include")

set( GLFW_BUILD_EXAMPLES OFF CACHE BOOL  "GLFW lib only" )
set( GLFW_BUILD_TESTS OFF CACHE BOOL  "GLFW lib only" )
set( GLFW_BUILD_DOCS OFF CACHE BOOL  "GLFW lib only" )
set( GLFW_BUILD_INSTALL OFF CACHE BOOL  "GLFW lib only" )

add_subdirectory(glfw)

target_link_libraries(glfw PRIVATE ${glfw_LIBRARIES})
#pybind11_add_module(glfw SHARED ${glfw_SOURCES})

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

target_compile_definitions(nptsne PUBLIC "-DPYBIND11_PYTHON_VERSION=${PYTHON_MAJ_MIN}")  

if(UNIX)
	find_package(LZ4 REQUIRED)
endif(UNIX)	


message( STATUS "HDI_BLD_ROOT: ${HDI_BLD_ROOT}" )
message( STATUS "HDI_INCLUDE_ROOT: ${HDI_INCLUDE_ROOT}" )

#include_directories ("${Qt5Widgets_INCLUDE_DIRS}")
include_directories ("${CMAKE_SOURCE_DIR}")
include_directories ("..")
include_directories ("${HDI_INCLUDE_ROOT}")

find_package(OpenMP REQUIRED)
if(OPENMP_FOUND)
	message (STATUS "OpenMP found")
	set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

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
target_link_libraries(nptsne PUBLIC pybind11::module)



if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	target_link_libraries (nptsne PUBLIC "${FLANN_BUILD_DIR}/${CMAKE_BUILD_TYPE}/flann_cpp_s.lib") 
    target_link_libraries(nptsne PRIVATE pybind11::module "glfw/src/glfw3")
endif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	target_link_libraries(nptsne PUBLIC ${OPENGL_LIBRARIES})
    #TODO GLFW3.lib
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

# Use prebuilt libflann and liblz4
if(UNIX)
	message(STATUS "Deploying lz4")
	if(PLATFORM_IS_CENTOS)
		install(FILES "/usr/lib64/liblz4.so.1.7.5" DESTINATION nptsne RENAME liblz4.so)
		install(FILES "/usr/lib64/libflann_cpp.so.1.8.4" DESTINATION nptsne RENAME libflann_cpp.so.1.8)
	else()
		install(FILES "/usr/lib/x86_64-linux-gnu/liblz4.so.1.7.1" DESTINATION nptsne RENAME liblz4.so)
		install(FILES "/usr/lib/x86_64-linux-gnu/libflann_cpp.so.1.8.4" DESTINATION nptsne RENAME libflann_cpp.so)
	endif()	
endif(UNIX)	
install(FILES ./nptsne_src/deploy__init__.py DESTINATION nptsne RENAME __init__.py)
