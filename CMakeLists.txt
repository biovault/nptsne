cmake_minimum_required(VERSION 3.15.0)

file (STRINGS "version.txt" VERSION)
project(_nptsne LANGUAGES CXX)

# Disallow in-source builds. 
# Build in sub dir e.g. source/build* is still allowed!
#if("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
#   message(FATAL_ERROR "In-source builds are not allowed!\n"
#    "Make sure to remove CMakeCache.txt and CMakeFiles/ "
#    "from the source directory!")
#endif()

option(NPTSNE_BUILD_WITH_CONAN "Should Conan package manager be used?" ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
  "${PROJECT_SOURCE_DIR}/cmake")

if(WIN32)
    set(CMAKE_CONFIGURATION_TYPES ${CMAKE_BUILD_TYPE})
endif()    

# A PEP 440 version is set in version.txt - this is not compatible with the CMAKE config
message(STATUS "Building in ${CMAKE_BINARY_DIR}")

# Find and the git branch name for tracing purposes
execute_process(
  COMMAND git rev-parse --abbrev-ref HEAD
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE GIT_BRANCH
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Working on branch ${GIT_BRANCH}")

file(REMOVE_RECURSE ${CMAKE_BINARY_DIR}/dist)
file(REMOVE_RECURSE _nptsne.egg-info)

# The python files for the package
#file(COPY "${PROJECT_SOURCE_DIR}/dist_root" 
#    DESTINATION "${CMAKE_BINARY_DIR}" 
#    FILES_MATCHING REGEX ".*\.py|.*\.md|.*\.txt|.*\.in")
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/dist_root)
    
file(GENERATE OUTPUT ${CMAKE_BINARY_DIR}/dist_root/nptsne/_version.txt CONTENT "${VERSION}")

# CONAN is only used if the NPTSNE_BUILD_WITH_CONAN is ON
include(ConanSetup)

message(STATUS "Processing directory: ${CMAKE_CURRENT_SOURCE_DIR}")

#find_package (Python3 REQUIRED COMPONENTS Interpreter Development)

if (WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS True)
endif()

#set(BUILD_PYTHON_VERSION "${Python3_VERSION}")
#set(PYBIND11_PYTHON_VERSION "${Python3_VERSION}")
#set(PY_TAG "cp${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR}")

#message(STATUS "Build Python version ${BUILD_PYTHON_VERSION}")
add_subdirectory(external/pybind11)
#find_package(pybind11 REQUIRED)

#MESSAGE(STATUS "Python : ${PYTHON_LIBRARY}")

#message (STATUS "The pybind version is ${PYBIND11_PYTHON_VERSION}") 
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
 
# Prefer C++14
if (APPLE)
    set(CMAKE_CXX_STANDARD 11)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(PYBIND11_CPP_STANDARD -std=c++11)
else()
    set(CMAKE_CXX_STANDARD 14)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
endif()

set(PYBIND11_PYTHON_VERSION "3" CACHE STRING "")

#set_property(GLOBAL PROPERTY USE_FOLDERS ON)

pybind11_add_module(${PROJECT_NAME}
    src/cpp/.editorconfig
    src/cpp/nptSNEBind.cpp
    src/cpp/Analysis.cpp
    src/cpp/HSne.cpp
    src/cpp/SparseTsne.cpp
    src/cpp/TextureTsne.cpp
    src/cpp/TextureTsneExtended.cpp
)

# In VisualStudio we show the python files in the bdist_wheel 
# custom targetfor ease of editing and debug
if(MSVC_IDE)
    macro(GroupSources curdir)
       file(GLOB children RELATIVE ${PROJECT_SOURCE_DIR}/${curdir} ${PROJECT_SOURCE_DIR}/${curdir}/*)
       foreach(child ${children})
              if(IS_DIRECTORY ${PROJECT_SOURCE_DIR}/${curdir}/${child})
                      GroupSources(${curdir}/${child})
              else()
                      string(REPLACE "/" "\\" groupname ${curdir})
                source_group(${groupname} FILES ${PROJECT_SOURCE_DIR}/${curdir}/${child})
              endif()
       endforeach()
    endmacro()
    
    file(GLOB_RECURSE DIST_ROOT_FILES "dist_root/*.*")
    GroupSources("dist_root")
        
    file(GLOB_RECURSE EXTERN_DOC_FILES "docsource/nptsnedoc/*.*")
    GroupSources("docsource/nptsnedoc")
else()
    set(DIST_ROOT_FILES "")
    set(EXTERN_DOC_FILES "")
endif()    

message(STATUS "DIST_ROOT_FILES: ${DIST_ROOT_FILES}")
message(STATUS "EXTERN_DOC_FILES: ${EXTERN_DOC_FILES}")

find_package(OpenGL REQUIRED)
if(NOT APPLE)
    if(NOT NPTSNE_BUILD_WITH_CONAN)
        find_package(glfw3 REQUIRED)
    endif()
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

target_compile_definitions(${PROJECT_NAME} 
        PUBLIC "-DPYBIND11_PYTHON_VERSION=${PYTHON_MAJ_MIN}")  

if(UNIX)
    find_package(LZ4 REQUIRED)
endif(UNIX)    

if(NOT DEFINED HDI_LIB_ROOT) 
    #set the following variables to allow the build (building with conan does this)
    set(HDI_LIB_ROOT "")
    set(HDI_INCLUDE_ROOT "")
    if(WIN32)
        set(FLANN_BUILD_DIR "")
        set(GLFW_ROOT "")
    endif()
endif()

message( STATUS "HDI_LIB_ROOT: ${HDI_LIB_ROOT}" )
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

# Prevent glfw including the OpenGL headers
# On Windows and Linux these come from glad in the HDILib
add_definitions(-DGLFW_INCLUDE_NONE)

message(STATUS "CXX compiler ${CMAKE_CXX_COMPILER}")
if (CMAKE_GENERATOR STREQUAL Xcode)
    # Assumption libomp, glfw and have been installed
    # probably using brew.
    # If using conan we use the conan build flann
    set(MAC_INSTALL_PREFIX "/usr/local")
    
    # Silences OpenGL deprecation warnings (in GLFW)
    add_definitions(-DGL_SILENCE_DEPRECATION)
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.12" CACHE STRING "Minimum OS X deployment version")
    
     #### Find flann
    if(NOT NPTSNE_BUILD_WITH_CONAN)
        include_directories("${MAC_INSTALL_PREFIX}/opt/flann/include")  
        find_library(FLANNCPP_LIBRARY flann_cpp HINTS "${MAC_INSTALL_PREFIX}/lib")
    else()
        # Conan brings flann via HDILib requirements
        find_library(FLANNCPP_LIBRARY flann_cpp HINTS "${CONAN_FLANN_ROOT}")
    endif()
    get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH) 
    get_short_version_number(${FLANNCPP_LIBRARY_PATH} FLANNCPP_SHORTNAME)
    message(STATUS, "Flann path: long - ${FLANNCPP_LIBRARY_PATH}, truncated - ${FLANNCPP_SHORTNAME}") 
    
    #### Find lz4    
    include_directories("${MAC_INSTALL_PREFIX}/opt/lz4/include") 
    find_library(LZ4_LIBRARY lz4 HINTS "${MAC_INSTALL_PREFIX}/lib")    
    get_filename_component(LZ4_LIBRARY_PATH ${LZ4_LIBRARY} REALPATH)
    # lz4 link chops two digits from the version 
    # (this probably a bug due to the library name ending in a digit)
    get_shorter_version_number(${LZ4_LIBRARY_PATH} LZ4_SHORTNAME)
   
    #### Find glfw
    find_library(GLFW_LIBRARY glfw HINTS "${MAC_INSTALL_PREFIX}/lib")    
    get_filename_component(GLFWLIBRARY_PATH ${GLFW_LIBRARY} REALPATH)
    get_short_version_number(${GLFWLIBRARY_PATH} GLFW_SHORTNAME)    
    include_directories(${GLFW_INCLUDE_DIRS} "${MAC_INSTALL_PREFIX}/opt/glfw/include")     

    get_filename_component(LZ4_LINK_PATH ${LZ4_LIBRARY} DIRECTORY)
    get_filename_component(FLANN_LINK_PATH ${FLANNCPP_LIBRARY_PATH} DIRECTORY)
    get_filename_component(GLFW_LINK_PATH ${GLFW_LIBRARY} DIRECTORY)
    link_directories(${FLANN_LINK_PATH})
    link_directories(${LZ4_LINK_PATH})
    link_directories(${GLFW_LINK_PATH})
    target_link_libraries(${PROJECT_NAME} PUBLIC ${LZ4_LIBRARY} )
    target_link_libraries(${PROJECT_NAME} PUBLIC ${FLANNCPP_LIBRARY_PATH} )   
    target_link_libraries(${PROJECT_NAME} PUBLIC ${GLFW_LIBRARY}) 
endif()

find_package(OpenMP)

if(OPENMP_FOUND)
    message (STATUS "OpenMP found libname: ${OpenMP_CXX_LIBRARIES}")
    include_directories(${OpenMP_CXX_INCLUDE_DIRS})
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}") 
    if (APPLE) 
        target_link_libraries(${PROJECT_NAME} PUBLIC "${OpenMP_CXX_LIBRARIES}")
        get_filename_component(OpenMP_REALPATH "${OpenMP_CXX_LIBRARIES}" REALPATH)
    else()
        target_link_libraries(${PROJECT} OpenMP::OpenMP_CXX)
    endif()
else()
    message(WARNING, "OpenMP not found!") 
    if(APPLE)
        message(WARNING "OpenMP support could not be detected, using Grand Central Dispatch instead.")
        add_definitions( -D__USE_GCD__)
    endif(APPLE)
endif()

set(HDIDR_BUILD_DIR "${HDI_LIB_ROOT}/dimensionality_reduction")
set(HDIDA_BUILD_DIR "${HDI_LIB_ROOT}/data")
set(HDIUI_BUILD_DIR "${HDI_LIB_ROOT}/utils")

if(WIN32)
    find_library(HDIDR NAMES hdidimensionalityreduction.lib PATHS ${HDIDR_BUILD_DIR}) 
    find_library(HDIDA NAMES hdidata.lib PATHS ${HDIDA_BUILD_DIR})
    find_library(HDIUI NAMES hdiutils.lib PATHS ${HDIUI_BUILD_DIR})
else(WIN32)
    find_library(HDIDR NAMES libhdidimensionalityreduction.a PATHS ${HDIDR_BUILD_DIR} ) 
    find_library(HDIDA NAMES libhdidata.a PATHS ${HDIDA_BUILD_DIR})
    find_library(HDIUI NAMES libhdiutils.a PATHS ${HDIUI_BUILD_DIR})
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

message(STATUS "SHARED_LINKER_FLAGS: ${CMAKE_SHARED_LINKER_FLAGS}")
