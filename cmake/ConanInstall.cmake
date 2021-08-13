if(NOT NPTSNE_BUILD_WITH_CONAN)
    return()
endif()

message(STATUS "Start Conan dependencies install")
if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
   message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
   file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/v0.16.1/conan.cmake"
                 "${CMAKE_BINARY_DIR}/conan.cmake")
endif()

include(${CMAKE_BINARY_DIR}/conan.cmake)

conan_check(VERSION 1.37.0 REQUIRED)
set(CONAN_SETTINGS "")
conan_cmake_autodetect(settings)
list(LENGTH settings num_settings)
message(STATUS "Detected settings: ${settings} number settings: ${num_settings}")
list(TRANSFORM settings REPLACE "build_type.*" "_delete_")
list(TRANSFORM settings REPLACE "compiler\.runtime.*" "_delete_")
list(REMOVE_ITEM settings "_delete_")
list(LENGTH settings num_settings)
message(STATUS "Adjusted settings: ${settings} number settings: ${num_settings}")
# list(JOIN settings " " SETTINGS_STRING)

# remove build_type from settings HDILib is build_type-less
list(FILTER settings EXCLUDE REGEX build_type=.*)

# Not CMakeDeps is not pulling transitive dependencies?
message("Generate conanfile.txt ")
conan_cmake_configure(REQUIRES HDILib/${HDILib_VERSION}@lkeb/testing
                  flann/${FLANN_VERSION}@lkeb/testing)

message("Run conan install and generate conanbuildinfo.txt")
if(UNIX AND NOT APPLE)
    conan_cmake_install(PATH_OR_REFERENCE .
        PROFILE action_build)
else()
    conan_cmake_install(PATH_OR_REFERENCE .
        PROFILE action_build SETTINGS build_type=Release)
endif()

message("Set CMAKE_MODULE_PATH and CMAKE_PREFIX_PATH for FindPackage")
set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR} ${CMAKE_MODULE_PATH})
set(CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR} ${CMAKE_PREFIX_PATH})

SET(Python_ADDITIONAL_VERSIONS 3)
FIND_PACKAGE(PythonInterp)

IF (NOT PYTHONINTERP_FOUND)
    MESSAGE(FATAL_ERROR "Python3 not found.")
ENDIF()

# Extract the prefixes for the cmake config files
# conanbuildinfo.txt is a type of config file.
set(PYTHON_PARSE_BUILDINFO "from configparser import ConfigParser
parser = ConfigParser(allow_no_value=True, delimiters=('='))
parser.read('conanbuildinfo.txt')
print(';'.join([key for key in parser['builddirs'].keys()]))")

execute_process(
    COMMAND ${PYTHON_EXECUTABLE} "-c" "${PYTHON_PARSE_BUILDINFO}" 
    OUTPUT_VARIABLE CONAN_BUILDINFO ERROR_VARIABLE PYERROR OUTPUT_STRIP_TRAILING_WHITESPACE)

# Add directories 
foreach(LIB_PATH IN LISTS CONAN_BUILDINFO)
    list(APPEND CMAKE_MODULE_PATH ${LIB_PATH})
    list(APPEND CMAKE_PREFIX_PATH ${LIB_PATH})
endforeach()

find_package(HDILib CONFIG REQUIRED)
set(HDILib_DIR "${HDILib_PACKAGE_FOLDER_NONE}")
message (STATUS "HDILib path: ${HDILib_PACKAGE_FOLDER_NONE}")

message(STATUS "End Conan dependencies install")

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
