cmake_minimum_required(VERSION 3.4.0)
file (STRINGS "version.txt" VERSION)
project(_nptsne LANGUAGES CXX)
# Invoke this using the command: 
#	python setup.py bdist_wheel
# within an environment containing the targeted python interpreter version
#
# A PEP 440 version is set in version.txt - this is not compatible with the CMAKE config

file(REMOVE_RECURSE ${CMAKE_CURRENT_SOURCE_DIR}/dist)
file(REMOVE_RECURSE _nptsne.egg-info)
file(REMOVE_RECURSE _skbuild)

file(GENERATE OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/_package/nptsne/_version.txt CONTENT "${VERSION}")

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

#set(BUILD_PYTHON_VERSION "" CACHE STRING "Python version to use for compiling the example library")

message(STATUS "Build Python version ${BUILD_PYTHON_VERSION}")
#include(FindPythonLibsNew)
#find_package(PythonLibsNew ${BUILD_PYTHON_VERSION} REQUIRED)
#include(FindPythonInterp)
#find_package(PythonInterp REQUIRED)
find_package(pybind11)

MESSAGE(STATUS "Python : ${PYTHON_LIBRARY}")

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

pybind11_add_module(${PROJECT_NAME} ${NPTSNE_FILES})

find_package(OpenGL REQUIRED)
if(UNIX)
    include(FindPkgConfig)
    find_package(PkgConfig REQUIRED)
    pkg_search_module(GLFW REQUIRED glfw3)
else()
    find_package(glfw3 REQUIRED)    
endif()    

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

target_compile_definitions(${PROJECT_NAME} PUBLIC "-DPYBIND11_PYTHON_VERSION=${PYTHON_MAJ_MIN}")  

if(UNIX)
	find_package(LZ4 REQUIRED)
endif(UNIX)	

if(NOT DEFINED HDI_BLD_ROOT) 
    set(HDI_BLD_ROOT "${CONAN_HDILIB_ROOT}")
    set(HDI_INCLUDE_ROOT "${CONAN_INCLUDE_DIRS_HDILIB}/HDILib")
    if(WIN32)
        set(FLANN_BUILD_DIR "${CONAN_FLANN_ROOT}")
        set(GLFW_ROOT "${CONAN_GLFW_ROOT}")
    endif()
endif()

message( STATUS "HDI_BLD_ROOT: ${HDI_BLD_ROOT}" )
message( STATUS "HDI_INCLUDE_ROOT: ${HDI_INCLUDE_ROOT}" )

include_directories ("${CMAKE_SOURCE_DIR}")
include_directories ("..")
include_directories ("${HDI_INCLUDE_ROOT}")

# Pass a filename - e.g path1/path2/mylib.1.2.3.ext and return mylib.1.2.ext 
function(get_short_version_number libname resultVar)
    get_filename_component(FILE_NAME ${libname} NAME)
    get_filename_component(FILE_TYPE ${FILE_NAME} LAST_EXT)
    get_filename_component(NAME_NO_TYPE ${FILE_NAME} NAME_WLE)
    get_filename_component(NAME_SHORT_VERSION ${NAME_NO_TYPE} NAME_WLE)
    set(${resultVar} "${NAME_SHORT_VERSION}${FILE_TYPE}" PARENT_SCOPE)
endfunction()    

# Pass a filename - e.g path1/path2/mylib.1.2.3.ext and return mylib.1.ext 
function(get_shorter_version_number libname resultVar)
    get_filename_component(FILE_NAME ${libname} NAME)
    get_filename_component(FILE_TYPE ${FILE_NAME} LAST_EXT)
    get_filename_component(NAME_NO_TYPE ${FILE_NAME} NAME_WLE)
    get_filename_component(NAME_SHORT_VERSION ${NAME_NO_TYPE} NAME_WLE)
    get_filename_component(NAME_SHORTER_VERSION ${NAME_SHORT_VERSION} NAME_WLE)    
    set(${resultVar} "${NAME_SHORTER_VERSION}${FILE_TYPE}" PARENT_SCOPE)
endfunction()  

# VisualStudio (or similar IDE) folder
set_target_properties(${PROJECT_NAME} PROPERTIES FOLDER "Python bindings")

# Setup RPATHs for loading the python extension dependencies on Linux and Macos
# Path is relative to the extension.
if(APPLE)
  set(_rpath_value "@loader_path")
elseif(UNIX)
  set(_rpath_value "$ORIGIN")
endif()

if(UNIX)
    set_target_properties(${PROJECT_NAME} PROPERTIES 
        INSTALL_RPATH ${_rpath_value}
        BUILD_WITH_INSTALL_RPATH ON)
    set(CMAKE_INSTALL_RPATH ${_rpath_value})
    #set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,origin")
    #set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-z,origin")
    #set(CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG "-Wl,-z,origin,-rpath")
endif()
    
message(STATUS "CXX compiler ${CMAKE_CXX_COMPILER}")
if (APPLE)
  add_definitions(-DGL_SILENCE_DEPRECATION)
  set(CMAKE_OSX_DEPLOYMENT_TARGET "10.12" CACHE STRING "Minimum OS X deployment version")
  if(DEFINED ENV{CONAN_IS_TRAVIS_OSX})
    find_program(BREW NAMES brew)
    message(STATUS, "In Macos with ${BREW}")
    
    #### Find LIBOMP
    execute_process(COMMAND ${BREW} --prefix libomp OUTPUT_VARIABLE BREW_LIBOMP_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    message(STATUS, "BREW LIBOMP ${BREW_LIBOMP_PREFIX}")
    set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp")
    set(OpenMP_CXX_LIB_NAMES "omp")
    set(OpenMP_omp_LIBRARY "${BREW_LIBOMP_PREFIX}/lib/libomp.dylib")
    include_directories("${BREW_LIBOMP_PREFIX}/include") 
    
    #### Find flann
    execute_process(COMMAND ${BREW} --prefix flann OUTPUT_VARIABLE BREW_FLANN_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    include_directories("${BREW_FLANN_PREFIX}/include")  
	find_library(FLANNCPP_LIBRARY flann_cpp HINTS "${BREW_FLANN_PREFIX}")
    get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH) 
    get_short_version_number(${FLANNCPP_LIBRARY_PATH} FLANNCPP_SHORTNAME)
    
    #### Find lz4    
    execute_process(COMMAND ${BREW} --prefix lz4 OUTPUT_VARIABLE BREW_LZ4_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    include_directories("${BREW_LZ4_PREFIX}/include") 
    find_library(LZ4_LIBRARY lz4 HINTS "${BREW_LZ4_PREFIX}")    
    get_filename_component(LZ4_LIBRARY_PATH ${LZ4_LIBRARY} REALPATH)
    # lz4 link chops two digits from the version 
    # (this probably a bug due to the library name ending in a digit)
    get_shorter_version_number(${LZ4_LIBRARY_PATH} LZ4_SHORTNAME)
   
    #### Check glfw - was found using PkgConfig
    find_library(GLFW_LIBRARY glfw HINTS "${GLFW_LIBRARY_DIRS}") 
    get_filename_component(GLFWLIBRARY_PATH ${GLFW_LIBRARY} REALPATH)
    get_short_version_number(${GLFWLIBRARY_PATH} GLFW_SHORTNAME)    
    include_directories(${GLFW_INCLUDE_DIRS})     

    target_link_libraries(${PROJECT_NAME} PUBLIC ${LZ4_LIBRARY} )
    target_link_libraries(${PROJECT_NAME} PUBLIC ${FLANNCPP_LIBRARY} )   
    target_link_libraries(${PROJECT_NAME} PUBLIC ${GLFW_LIBRARY})     
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

target_link_libraries(${PROJECT_NAME} PUBLIC ${HDIDR} ${HDIDA} ${HDIUI})
target_link_libraries(${PROJECT_NAME} PUBLIC pybind11::module)

if(WIN32)
	target_link_libraries (${PROJECT_NAME} PUBLIC "${FLANN_BUILD_DIR}/lib/flann_cpp_s.lib") 
    target_link_libraries(${PROJECT_NAME} PRIVATE pybind11::module "${GLFW_ROOT}/lib/glfw3.lib")
    #static GLFW
    target_link_libraries(${PROJECT_NAME} PUBLIC ${GLFW_STATIC_LIBRARIES})    
endif()

if(CMAKE_SYSTEM_NAME STREQUAL Linux)
	target_link_libraries(${PROJECT_NAME} PUBLIC ${OPENGL_LIBRARIES}) 
	if(PLATFORM_IS_CENTOS)
		# centos
		find_library(LZ4_LIBRARY lz4 HINTS /usr/lib64)
		find_library(FLANNCPP_LIBRARY flann_cpp HINTS /usr/lib64)
		find_library(GLFW_LIBRARY glfw HINTS /usr/lib64)
	else()
		# ubuntu
		find_library(LZ4_LIBRARY lz4 HINTS /usr/lib/x86_64-linux-gnu)
		find_library(FLANNCPP_LIBRARY flann_cpp HINTS /usr/lib/x86_64-linux-gnu)
		find_library(GLFW_LIBRARY glfw HINTS /usr/lib/x86_64-linux-gnu)
	endif()
    get_filename_component(LZ4_LIBRARY_PATH ${LZ4_LIBRARY} REALPATH)
    get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH) 
    get_filename_component(GLFWLIBRARY_PATH ${GLFW_LIBRARY} REALPATH)
    target_link_libraries(${PROJECT_NAME} PUBLIC ${LZ4_LIBRARY} )
    target_link_libraries(${PROJECT_NAME} PUBLIC ${FLANNCPP_LIBRARY} )   
    target_link_libraries(${PROJECT_NAME} PUBLIC ${GLFW_LIBRARY}) 
    target_link_libraries(${PROJECT_NAME} PUBLIC "${OPENGL_gl_LIBRARY}")    
endif()

if (UNIX)
    # shared GLFW
    if(GLFW_FOUND AND OPENGL_FOUND)
        message(STATUS "Using installed GLFW ${GLFW_VERSION}")
    endif()
else()
    message(STATUS "Using static GLFW ")
endif()

message( STATUS "Command line project: " ${PROJECT_NAME} )


message(STATUS "SHARED_LINKER_FLAGS: ${CMAKE_SHARED_LINKER_FLAGS}")

# Install phase - move the extension plus and libraries necessary to
# an install destination where they can be bundled in a separate invocation
# of python setup.py bdist_wheel


# The binary extension
install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION "_package/nptsne/libs")

# The binary extension needs to load the glfw flann and lz4 from its own directory
# use the intall_name_tool to fix this. This code makes two scripts getname.sh and fixup.sh
# which are used to get the path to the extension and to modify it.
if(APPLE)
	install(CODE "
		execute_process(
			COMMAND sh -c \"echo 'A=`ls ${CMAKE_INSTALL_PREFIX}/_package/nptsne/libs/*.so` && echo $A' > ~/getname.sh\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})
		execute_process(
			COMMAND sh -c \"chmod +x ~/getname.sh\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})
		execute_process(
			COMMAND sh -c \"rm -f ~/fixup.sh && otool -L `~/getname.sh` | grep -E 'glfw|flann|lz4' | cut -f 1 -d ' ' | xargs -I ! sh -c 'A=! && echo install_name_tool -change $A @loader_path/$\{A##*/} `~/getname.sh` >> ~/fixup.sh'\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})			
		execute_process(
			COMMAND sh -c \"chmod +x ~/fixup.sh\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})
		execute_process(
			COMMAND sh -c \"cat ~/getname.sh\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})		
		execute_process(
			COMMAND sh -c \"cat ~/fixup.sh\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})	            
	")
endif()

# The associated python module and wrappers    
install(DIRECTORY "_package/" DESTINATION "_package"
         FILES_MATCHING REGEX ".*\.py|.*\.md|.*\.txt|.*\.in")    

# Platform specific libs
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
    # In linux bundle prebuilt libflann and liblz4
    install(FILES ${LZ4_LIBRARY_PATH} DESTINATION "_package/nptsne/libs" RENAME liblz4.so)
    install(FILES ${FLANNCPP_LIBRARY_PATH} DESTINATION "_package/nptsne/libs" RENAME libflann_cpp.so)
    install(FILES ${GLFWLIBRARY_PATH} DESTINATION "_package/nptsne/libs" RENAME libglfw.so)
endif()	

if(APPLE)
	message(STATUS "Will deploy lz4, flann_cpp and glfw as: ${LZ4_SHORTNAME} ${FLANNCPP_SHORTNAME} ${GLFW_SHORTNAME}")
    install(FILES ${LZ4_LIBRARY_PATH} DESTINATION "_package/nptsne/libs" RENAME ${LZ4_SHORTNAME})
    install(FILES ${FLANNCPP_LIBRARY_PATH} DESTINATION "_package/nptsne/libs" RENAME ${FLANNCPP_SHORTNAME})
    install(FILES ${GLFWLIBRARY_PATH} DESTINATION "_package/nptsne/libs" RENAME ${GLFW_SHORTNAME})
    file(GLOB_RECURSE PACKAGE_FILES RELATIVE "_package/nptsne" "*.*")
    message(STATUS "Files in package: ${PACKAGE_FILES}")
endif()

# For APPLE now fixup the binary extension to load the dylibs from a relative @loader_path
if(APPLE)
	install(CODE "
			execute_process(COMMAND sh -c \"otool -L `~/getname.sh`\")
			execute_process(COMMAND sh -c \"~/fixup.sh\")
			execute_process(COMMAND sh -c \"otool -L `~/getname.sh`\")
	")
endif()
