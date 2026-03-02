cmake_minimum_required(VERSION 3.25.0)
if(${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.27.0")
    cmake_policy(SET CMP0144 NEW)    # Remove once we set min cmake version accordingly
endif()

message(STATUS "1 CMAKE LIB OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "1 CMAKE LIB RELEASE OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE}")

file (STRINGS "version.txt" VERSION) 
project(_nptsne)

option(NPTSNE_BUILD_WITH_CONAN "Should Conan package manager be used?" ON)
option(USE_ARTIFACTORY_LIBS "Use the prebuilt libraries from artifactory" ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
  "${CMAKE_SOURCE_DIR}/cmake")

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



# CONAN is only used to install dependencies if the NPTSNE_BUILD_WITH_CONAN is ON
#if (NPTSNE_BUILD_WITH_CONAN)
if (USE_ARTIFACTORY_LIBS) 
    set(LIBRARY_INSTALL_DIR ${PROJECT_BINARY_DIR})
    message(STATUS "Installing artifactory packages to: ${LIBRARY_INSTALL_DIR}")

    set(HDILib_VERSION 2.0.0a1)
    set(flann_VERSION 1.9.2)
    set(lz4_VERSION 1.10.0)

    include(FetchContent)
    # Use the ManiVaultStudio github-action tools to get the pre-built packages from artifactory
    FetchContent_Declare(cmakesupport
        GIT_REPOSITORY https://github.com/ManiVaultStudio/github-actions
        GIT_TAG libcxx_abi
        GIT_SHALLOW TRUE
        SOURCE_SUBDIR CMakeSupport
    )
    FetchContent_MakeAvailable(cmakesupport)

    message(STATUS "FetchContent: ${cmakesupport_SOURCE_DIR} ${cmakesupport_BINARY_DIR}")
    include("${cmakesupport_SOURCE_DIR}/CMakeSupport/InstallArtifactoryPackage.cmake")

    if(DEFINED ENV{HDILib_channel})
        install_artifactory_package(HDILib ${HDILib_VERSION} biovault TRUE "$ENV{HDILib_channel}") 
    else()
        install_artifactory_package(HDILib ${HDILib_VERSION} biovault TRUE stable)  
    endif()
    install_artifactory_package(flann ${flann_VERSION} lkeb TRUE stable)
    install_artifactory_package(lz4 ${lz4_VERSION} lkeb TRUE stable)

    set(lz4_ROOT "${LIBRARY_INSTALL_DIR}/lz4/lib/cmake")
    set(flann_ROOT "${LIBRARY_INSTALL_DIR}/flann/lib/cmake/")
    set(HDILIB_ROOT "${LIBRARY_INSTALL_DIR}/HDILib/lib/cmake/HDILib")
    set(kompute_ROOT "${LIBRARY_INSTALL_DIR}/HDILib/lib/cmake/kompute")
    set(fmt_ROOT "${LIBRARY_INSTALL_DIR}/HDILib/lib/cmake/fmt")

endif()

find_package(lz4 1.10.0 CONFIG REQUIRED)

if (WIN32)
    get_target_property(LZ4_static_Location LZ4::lz4_static IMPORTED_LOCATION_RELEASE)
endif()

find_package(flann 1.9.2 REQUIRED)
find_package(fmt REQUIRED)
find_package(kompute REQUIRED)
find_package(HDILib COMPONENTS hdidimensionalityreduction hdiutils hdidata CONFIG REQUIRED PATHS ${HDILIB_ROOT})

message(STATUS "All build targets: ${BUILDSYSTEM_TARGETS}")
message(STATUS "All import targets: ${IMPORT_TARGETS}")

set(LZ4_LIBRARY "LZ4::lz4_static")
set(FLANNCPP_LIBRARY "flann::flann_cpp_s")


message(STATUS "Processing directory: ${CMAKE_CURRENT_SOURCE_DIR}")

if (WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS True)
endif()

add_subdirectory(external/pybind11)
#
message (STATUS "The python executable is at ${PYTHON_EXECUTABLE}")
message(STATUS "2 CMAKE LIB OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "2 CMAKE LIB RELEASE OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE}")

include(FindOpenGL)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
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

# Utility for installing GLFW headers from the submodule
macro(install_headers source)
    install(DIRECTORY   "${CMAKE_CURRENT_SOURCE_DIR}/${source}"
            DESTINATION "${CMAKE_INSTALL_PREFIX}/include/${CMAKE_PROJECT_NAME}/3rdparty"
            PATTERN     "*.c"           EXCLUDE
            PATTERN     "*.cmake"       EXCLUDE
            PATTERN     "*.cpp"         EXCLUDE
            PATTERN     "*.in"          EXCLUDE
            PATTERN     "*.m"           EXCLUDE
            PATTERN     "*.txt"         EXCLUDE
            PATTERN     ".gitignore"    EXCLUDE)
endmacro()

if(TRUE)
    message(STATUS, "Will build GLFW")
    set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "disable GLFX examples")
    set(GLFW_BUILD_TESTS OFF CACHE BOOL "disable GLFX tests")
    set(GLFW_BUILD_DOCS OFF CACHE BOOL "disable GLFX docs")
    set(GLFW_INSTALL OFF CACHE BOOL "disable GLFX installation target")
    add_subdirectory(external/glfw)
    # install_headers(external/glfw)
endif()

pybind11_add_module(_nptsne
    src/cpp/.editorconfig
    src/cpp/nptSNEBind.cpp
    src/cpp/Analysis.cpp
    src/cpp/HSne.cpp
    src/cpp/KnnAlgorithm.cpp
    src/cpp/SparseTsne.cpp
    src/cpp/TextureTsne.cpp
    src/cpp/TextureTsneExtended.cpp
)


message(STATUS "Linking ${LZ4_LIBRARY}")
#target_link_libraries(_nptsne PRIVATE ${LZ4_LIBRARY} )
#target_link_libraries(_nptsne PRIVATE ${FLANNCPP_LIBRARY} )
target_link_libraries(_nptsne PRIVATE "${OPENGL_gl_LIBRARY}")
if (WIN32)
  target_compile_options(_nptsne PRIVATE "/utf-8") # for fmt compatibility
endif()

message(STATUS "3 CMAKE LIB OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "3 CMAKE LIB RELEASE OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE}")
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

target_compile_definitions(_nptsne
        PUBLIC "-DPYBIND11_PYTHON_VERSION=${PYTHON_MAJ_MIN}")

if(UNIX)
    message(STATUS "pThreads for Linux")
    find_package(Threads REQUIRED)
endif(UNIX)

if(NOT WIN32)
    set_property(TARGET _nptsne PROPERTY POSITION_INDEPENDENT_CODE ON)
endif()

if(NOT DEFINED HDILib_DIR)
    #set the following variables to allow the build (building with conan does this)
    set(HDILib_DIR "***FILL THIS IN***")     # root of the HDILib build directory
    set(HDILib_INCLUDE_DIR "***FILL THIS IN***")  # subdirectory containing HDILib headers
    set(HDILib_LINK_LIBS "***FILL THIS IN***")  # listo of $<CONFIGURATON> correct static libs
    if(WIN32)
        set(FLANN_BUILD_DIR "")
        set(GLFW_ROOT "")
    endif()
endif()

include_directories ("${CMAKE_SOURCE_DIR}")
include_directories ("..")
include_directories (${HDILib_INCLUDE_DIR})

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
set_target_properties(_nptsne PROPERTIES FOLDER "Python bindings")

# Prevent glfw including the OpenGL headers
# On Windows and Linux these come from glad in the HDILib
add_definitions(-DGLFW_INCLUDE_NONE)

# Silences OpenGL deprecation warnings (in GLFW)
add_definitions(-DGL_SILENCE_DEPRECATION)
set(GLFW_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/external/glfw/include")
message(STATUS "GLFW include at : ${GLFW_INCLUDE_DIRS}")
target_include_directories(_nptsne PRIVATE ${GLFW_INCLUDE_DIRS})
target_link_libraries(_nptsne PRIVATE glfw)
target_link_libraries(_nptsne PRIVATE pybind11::module)

message(STATUS "CXX compiler ${CMAKE_CXX_COMPILER}")
if (CMAKE_GENERATOR STREQUAL Xcode)
    # Assumption libomp, has been installed
    # probably using brew.
    # If using conan we use the conan built flann
    set(MAC_INSTALL_PREFIX "/usr/local")

    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.12" CACHE STRING "Minimum OS X deployment version")

     #### Find flann
    if(NOT NPTSNE_BUILD_WITH_CONAN)
        # Conan brings flann via HDILib requirements
        message(STATUS "looking for flann static library ")
        find_library(FLANNCPP_LIBRARY flann_cpp HINTS ${flann_PACKAGE_FOLDER_NONE}/lib/${CMAKE_BUILD_TYPE} REQUIRED)
        message(STATUS "flann static library ${FLANNCPP_LIBRARY}")
        get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH)
    endif()
    
    get_short_version_number(${FLANNCPP_LIBRARY_PATH} FLANNCPP_SHORTNAME)
    message(STATUS, "Flann path: long - ${FLANNCPP_LIBRARY_PATH}, truncated - ${FLANNCPP_SHORTNAME}")

    #### Find lz4
    include_directories("${MAC_INSTALL_PREFIX}/opt/lz4/include")
    find_library(LZ4_LIBRARY lz4 HINTS "${MAC_INSTALL_PREFIX}/lib")
    get_filename_component(LZ4_LIBRARY_PATH ${LZ4_LIBRARY} REALPATH)

    get_filename_component(LZ4_LINK_PATH ${LZ4_LIBRARY} DIRECTORY)
    get_filename_component(FLANN_LINK_PATH ${FLANNCPP_LIBRARY_PATH} DIRECTORY)
    link_directories(${FLANN_LINK_PATH})
    link_directories(${LZ4_LINK_PATH})
    #target_link_libraries(_nptsne PRIVATE ${LZ4_LIBRARY} )
    #target_link_libraries(_nptsne PRIVATE ${FLANNCPP_LIBRARY_PATH} )
    message(STATUS "Flann library ${FLANNCPP_LIBRARY}")

endif()

# Set the OMP root (assume installed via brew)
if(APPLE)
    execute_process(COMMAND brew --prefix libomp
        OUTPUT_VARIABLE OpenMP_ROOT
        OUTPUT_STRIP_TRAILING_WHITESPACE)
    message (STATUS "OpenMP root: ${OpenMP_ROOT}")
endif()    
find_package(OpenMP)

if(OPENMP_FOUND)
    message (STATUS "OpenMP found libname: ${OpenMP_CXX_LIBRARIES}")
    include_directories(${OpenMP_CXX_INCLUDE_DIRS})
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    if (APPLE)
        target_link_libraries(_nptsne PRIVATE "${OpenMP_CXX_LIBRARIES}")
        get_filename_component(OpenMP_REALPATH "${OpenMP_CXX_LIBRARIES}" REALPATH)
    else()
        target_link_libraries(_nptsne PRIVATE OpenMP::OpenMP_CXX)
    endif()
else()
    message(WARNING, "OpenMP not found!")
    if(APPLE)
        message(WARNING "OpenMP support could not be detected, using Grand Central Dispatch instead.")
        add_definitions( -D__USE_GCD__)
    endif(APPLE)
endif()

target_link_libraries(_nptsne PRIVATE ${HDILib_LINK_LIBS})

if(WIN32)
    # Windows uses static flann lib
    target_link_libraries (_nptsne PRIVATE "${FLANNCPP_LIBRARY}")
    #find_library(LZ4_LIBRARY lz4 HINTS ${lz4_LIB_DIRS})
    message(STATUS "Linking LZ4_LIBRARY - ${LZ4_LIBRARY}")
    target_link_libraries (_nptsne PRIVATE "${LZ4_LIBRARY}")
    target_link_libraries(_nptsne PRIVATE ${GLFW_STATIC_LIBRARIES})
endif()

if(CMAKE_SYSTEM_NAME STREQUAL Linux)
    target_link_libraries(_nptsne PRIVATE ${OPENGL_LIBRARIES})
    if(FALSE)
        if(PLATFORM_IS_CENTOS)
            # centos
            find_library(LZ4_LIBRARY lz4 HINTS /usr/lib64)
            if(NOT NPTSNE_BUILD_WITH_CONAN)
                find_library(FLANNCPP_LIBRARY flann_cpp HINTS /usr/lib64 REQUIRED)
                get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH)
            endif()
            find_package(PkgConfig REQUIRED)
            message(STATUS "Flann library ${FLANNCPP_LIBRARY}")
        else()
            # ubuntu
            find_library(LZ4_LIBRARY lz4 HINTS /usr/lib/x86_64-linux-gnu)
            if(NOT NPTSNE_BUILD_WITH_CONAN)
                find_library(FLANNCPP_LIBRARY flann_cpp HINTS /usr/lib/x86_64-linux-gnu REQUIRED)
                get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH)
            endif()
            message(STATUS "Flann library ${FLANNCPP_LIBRARY}")
        endif()
    endif()
    # get_filename_component(LZ4_LIBRARY_PATH ${LZ4_LIBRARY} REALPATH)
    set(LZ4_LIBRARY "LZ4::lz4_static")
    set(FLANNCPP_LIBRARY "flann::flann_cpp_s")
    #target_link_libraries(_nptsne PRIVATE ${LZ4_LIBRARY} )
    #target_link_libraries(_nptsne PRIVATE ${FLANNCPP_LIBRARY} )
    #target_link_libraries(_nptsne PRIVATE "${OPENGL_gl_LIBRARY}")
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
message(STATUS "4 CMAKE LIB OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "4 CMAKE LIB RELEASE OUTPUT: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE}")

# Platform specific libs
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
    # In linux bundle prebuilt libflann and liblz4
    install(FILES ${LZ4_LIBRARY_PATH} DESTINATION ${TEMP_LIBS_DIR} RENAME liblz4.so)
    install(FILES ${FLANNCPP_LIBRARY_PATH} DESTINATION ${TEMP_LIBS_DIR} RENAME "libflann_cpp.so.${flann_VERSION}")
    install(FILES ${GLFWLIBRARY_PATH} DESTINATION ${TEMP_LIBS_DIR} RENAME libglfw.so.3)
endif()

# Platform specific libs
if (CMAKE_SYSTEM_NAME STREQUAL Darwin)
    install(FILES ${FLANNCPP_LIBRARY_PATH} DESTINATION ${TEMP_LIBS_DIR} RENAME "libflann_cpp.${flann_VERSION}.dylib")
endif()

# Install the extra binaries to the desired liboutput
if(CMAKE_SYSTEM_NAME STREQUAL Linux OR CMAKE_SYSTEM_NAME STREQUAL Darwin)
    add_custom_target (bundle_libs
        COMMAND ${CMAKE_COMMAND} -E echo "Run install for binary dir ${CMAKE_BINARY_DIR} and the pre-built libs."
        COMMAND ${CMAKE_COMMAND} --install ${CMAKE_BINARY_DIR}
    )
else()
    add_custom_target (bundle_libs
        COMMAND ${CMAKE_COMMAND} -E echo "No conan libs for wheel fixup"
    )
endif()

message(STATUS "End of CMAKE")
