cmake_minimum_required(VERSION 3.4.0)
project(nptsne LANGUAGES CXX)
# Invoke this using the command: 
#	python setup.py bdist_wheel
# within an environment containing the targeted python interpreter version
#
# A PEP 440 version is set in nptsne_src/version.py 

file(REMOVE_RECURSE ${CMAKE_CURRENT_SOURCE_DIR}/dist)
file(REMOVE_RECURSE nptsne.egg-info)
file(REMOVE_RECURSE _skbuild)

# Conan declared variables
message(STATUS "Processing directory: ${CMAKE_CURRENT_SOURCE_DIR}")

# Download automatically, you can also just copy the conan.cmake file
if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
   message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
   file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.14/conan.cmake"
                 "${CMAKE_BINARY_DIR}/conan.cmake")
endif()

include(${CMAKE_BINARY_DIR}/conan.cmake)

conan_cmake_run(CONANFILE conanfile.py
				BASIC_SETUP 
                BUILD missing)

message(STATUS "Conan CONAN_PYBIND11_ROOT***: ${CONAN_PYBIND11_ROOT} ***")
message(STATUS "Conan CONAN_INCLUDE_DIRS_HDILIB***: ${CONAN_INCLUDE_DIRS_HDILIB} ***")
message(STATUS "Conan CONAN_HDILIB_ROOT***: ${CONAN_HDILIB_ROOT} ***")

find_package(pybind11 REQUIRED)

set(BUILD_PYTHON_VERSION "" CACHE STRING "Python version to use for compiling the example library")

message(STATUS "Build Python version ${BUILD_PYTHON_VERSION}")
include(FindPythonLibsNew)
find_package(PythonLibsNew ${BUILD_PYTHON_VERSION} REQUIRED)
include(FindPythonInterp)
find_package(PythonInterp REQUIRED)

MESSAGE(STATUS "Python : ${PYTHON_LIBRARY}")

set(PYBIND11_PYTHON_VERSION "${BUILD_PYTHON_VERSION}" CACHE STRING "" FORCE)
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

find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)

set( GLFW_BUILD_EXAMPLES OFF CACHE BOOL  "GLFW lib only" )
set( GLFW_BUILD_TESTS OFF CACHE BOOL  "GLFW lib only" )
set( GLFW_BUILD_DOCS OFF CACHE BOOL  "GLFW lib only" )
set( GLFW_BUILD_INSTALL OFF CACHE BOOL  "GLFW lib only" )

target_link_libraries(glfw PRIVATE ${glfw_LIBRARIES})

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

if(NOT DEFINED HDI_BLD_ROOT) 
    set(HDI_BLD_ROOT "${CONAN_HDILIB_ROOT}")
    set(HDI_INCLUDE_ROOT "${CONAN_INCLUDE_DIRS_HDILIB}/HDILib")
    if(WIN32)
        set(FLANN_BUILD_DIR "${CONAN_FLANN_ROOT}")
    endif()
    set(GLFW_ROOT "${CONAN_GLFW_ROOT}")
endif()

message( STATUS "HDI_BLD_ROOT: ${HDI_BLD_ROOT}" )
message( STATUS "HDI_INCLUDE_ROOT: ${HDI_INCLUDE_ROOT}" )

include_directories ("${CMAKE_SOURCE_DIR}")
include_directories ("..")
include_directories ("${HDI_INCLUDE_ROOT}")

message(STATUS "CXX compiler ${CMAKE_CXX_COMPILER}")
if (CMAKE_GENERATOR STREQUAL Xcode)
  add_definitions(-DGL_SILENCE_DEPRECATION)
  set(CMAKE_OSX_DEPLOYMENT_TARGET "10.12" CACHE STRING "Minimum OS X deployment version")
  if(DEFINED ENV{CONAN_IS_TRAVIS_OSX})
    find_program(BREW NAMES brew)
    message(STATUS, "In Darwin with ${BREW}")
    execute_process(COMMAND ${BREW} --prefix libomp OUTPUT_VARIABLE BREW_LIBOMP_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    message(STATUS, "BREW LIBOMP ${BREW_LIBOMP_PREFIX}")
    set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp")
    set(OpenMP_CXX_LIB_NAMES "omp")
    set(OpenMP_omp_LIBRARY "${BREW_LIBOMP_PREFIX}/lib/libomp.dylib")
    include_directories("${BREW_LIBOMP_PREFIX}/include") 
    execute_process(COMMAND ${BREW} --prefix flann OUTPUT_VARIABLE BREW_FLANN_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    include_directories("${BREW_FLANN_PREFIX}/include")     
  else() 
      find_package(LLVM)
      if( LLVM_FOUND )
        include_directories (${LLVM_LIBRARY_DIRS}/clang/${LLVM_VERSION_BASE_STRING}/include)
        
        set(CMAKE_CXX_COMPILER "/usr/local/opt/llvm/bin/clang++")
        set(CMAKE_C_COMPILER "/usr/local/opt/llvm/bin/clang")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp")
        set(CMAKE_XCODE_ATTRIBUTE_CC "/usr/local/opt/llvm/bin/clang")
        set(CMAKE_XCODE_ATTRIBUTE_CXX "/usr/local/opt/llvm/bin/clang++")

        find_library(IOMP5LIB
          NAMES "iomp5" "iomp5md" "libiomp5" "libiomp5md"
          HINTS ${LLVM_LIBRARY_DIRS})
        set (OMP_LIBRARIES ${OMP_LIBRARIES} ${IOMP5LIB})
      else(LLVM_FOUND)
        message("OS is macOS, no OpenMP support detected, using Grand Central Dispatch instead.")
        add_definitions( -D__USE_GCD__)
 
     endif( LLVM_FOUND )
  endif()
else()
    find_package(OpenMP REQUIRED)
endif()

if(OPENMP_FOUND)
	message (STATUS "OpenMP found")
	set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

set(HDIDR_BUILD_DIR "${HDI_BLD_ROOT}/dimensionality_reduction")  
set(HDIDA_BUILD_DIR "${HDI_BLD_ROOT}/data") 
set(HDIUI_BUILD_DIR "${HDI_BLD_ROOT}/utils") 

if(WIN32)
	find_library(HDIDR NAMES hdidimensionalityreduction.lib PATHS ${HDIDR_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE}) 
	find_library(HDIDA NAMES hdidata.lib PATHS ${HDIDA_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
	find_library(HDIUI NAMES hdiutils.lib PATHS ${HDIUI_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
else(WIN32)
	find_library(HDIDR NAMES libhdidimensionalityreduction.a PATHS ${HDIDR_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE}) 
	find_library(HDIDA NAMES libhdidata.a PATHS ${HDIDA_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})
	find_library(HDIUI NAMES libhdiutils.a PATHS ${HDIUI_BUILD_DIR} PATH_SUFFIXES ${CMAKE_BUILD_TYPE})	
endif(WIN32)

target_link_libraries(nptsne PUBLIC ${HDIDR} ${HDIDA} ${HDIUI})
target_link_libraries(nptsne PUBLIC pybind11::module)

if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	target_link_libraries (nptsne PUBLIC "${FLANN_BUILD_DIR}/lib/flann_cpp_s.lib") 
    target_link_libraries(nptsne PRIVATE pybind11::module "${GLFW_ROOT}/lib/glfw3.lib")
endif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	target_link_libraries(nptsne PUBLIC ${OPENGL_LIBRARIES})
    find_package(lz4 REQUIRED)
    message(STATUS "LZ4 ${LZ4_FIND_VERSION}")
    find_package(flann_cpp REQUIRED)
    message(STATUS "LZ4 ${FLANN_CPP_FIND_VERSION}")    
    #TODO GLFW3.lib
	if(PLATFORM_IS_CENTOS)
		# centos
		target_link_libraries(nptsne PUBLIC "/usr/lib64/liblz4.so" )
		target_link_libraries(nptsne PUBLIC "/usr/lib64/libflann_cpp.so" )
	else()
		# ubuntu
		target_link_libraries(nptsne PUBLIC "/usr/lib/x86_64-linux-gnu/liblz4.so" )
		target_link_libraries(nptsne PUBLIC "/usr/lib/x86_64-linux-gnu/libflann_cpp.so" )		
	endif()
	target_link_libraries(nptsne PUBLIC "${OPENGL_gl_LIBRARY}")
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

# Install phase - move the extension plus and libraries necessary to
# an install destination where they can be bundled in a separate invocation
# of python setup.py bdist_wheel


# The binary extension
install(TARGETS nptsne 
    ARCHIVE DESTINATION "_package/nptsne"
    LIBRARY DESTINATION "_package/nptsne")

# The associated python module and wrappers    
install(DIRECTORY "_package/" DESTINATION "_package"
         FILES_MATCHING REGEX ".*\.py|.*\.md|.*\.txt")    

# Platform specific libs
if(UNIX)
    # In linux bundle prebuilt libflann and liblz4
	message(STATUS "Deploying lz4")
	if(PLATFORM_IS_CENTOS)
		install(FILES "/usr/lib64/liblz4.so.1.7.5" DESTINATION "_package" RENAME liblz4.so)
		install(FILES "/usr/lib64/libflann_cpp.so" DESTINATION "_package" RENAME libflann_cpp.so)
	else()
		install(FILES "/usr/lib/x86_64-linux-gnu/liblz4.so.1.8.3" DESTINATION "_package" RENAME liblz4.so)
		install(FILES "/usr/lib/x86_64-linux-gnu/libflann_cpp.so.1.9.1" DESTINATION "_package" RENAME libflann_cpp.so)
	endif()	
endif(UNIX)	



