if(NOT NPTSNE_BUILD_WITH_CONAN)
    return()
endif()

message(STATUS "Start ConanSetup")
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
# remove build_type from settings HDILib is build_type-less
list(FILTER settings EXCLUDE REGEX build_type=.*)

# Not CMakeDeps is not pulling transitive dependencies?
conan_cmake_configure(REQUIRES HDILib/${HDILib_VERSION}@biovault/stable
                  flann/${FLANN_VERSION}@lkeb/stable
                  # lz4/${LZ4_VERSION}
                  GENERATORS CMakeDeps)

if(UNIX AND NOT APPLE)
    conan_cmake_install(PATH_OR_REFERENCE .
        PROFILE default)
else()
    conan_cmake_install(PATH_OR_REFERENCE .
                    SETTINGS ${CONAN_SETTINGS})
endif()

set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR} ${CMAKE_MODULE_PATH})
set(CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR} ${CMAKE_PREFIX_PATH})
find_package(ConanHDILib)
set(HDILib_DIR "${HDILib_PACKAGE_FOLDER_NONE}")
message (STATUS "HDILib path: ${HDILib_PACKAGE_FOLDER_NONE}")
# find_package(lz4 REQUIRED)
# set(lz4_LIB_DIRS ${lz4_LIB_DIRS_NONE})

message(STATUS "End ConanSetup")

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
