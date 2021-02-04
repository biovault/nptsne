if(NOT NPTSNE_BUILD_WITH_CONAN)
    return()
endif()

message(STATUS "Start ConanSetup")
# Download the conan cmake macros automatically.
if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
   message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
   file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.15/conan.cmake"
                 "${CMAKE_BINARY_DIR}/cmake/conan.cmake")
endif()

include(${CMAKE_BINARY_DIR}/cmake/conan.cmake)


file(TIMESTAMP ${CMAKE_BINARY_DIR}/conan_install_timestamp.txt file_timestamp "%Y.%m.%d")
string(TIMESTAMP timestamp "%Y.%m.%d")

# Run conan install update only once a day
if("${file_timestamp}" VERSION_LESS ${timestamp} OR IS_CI)
    file(WRITE ${CMAKE_BINARY_DIR}/conan_install_timestamp.txt "${timestamp}\n")
    set(CONAN_UPDATE UPDATE)
    conan_add_remote(NAME lkeb-artifactory INDEX 0
        URL https://lkeb-artifactory.lumc.nl/artifactory/api/conan/conan-local)
    conan_add_remote(NAME bincrafters INDEX 1
        URL https://api.bintray.com/conan/bincrafters/public-conan)
else()
    message(STATUS "Conan: Skipping update step.")
endif()

if(MSVC)
    set(CC_CACHE $ENV{CC})
    set(CXX_CACHE $ENV{CXX})
    unset(ENV{CC}) # Disable cl cache, e.g. for building qt
    unset(ENV{CXX})
endif()

set(CONAN_SETTINGS "")

if(UNIX)
    if(LIBCXX)
        set(CONAN_SETTINGS ${CONAN_SETTINGS} "compiler.libcxx=${LIBCXX}")
    endif()
endif()

message(STATUS "Install dependencies with conan")
# NO_OUTPUT_DIRS - ensures that the output dirs (e.g. CMAKE_LIBRARY_OUTPUT_DIRECTORY)
# which are set in setup.py are left alone
conan_cmake_run(
    CONANFILE conanfile.py
    BASIC_SETUP ${CONAN_UPDATE}
    KEEP_RPATHS
    NO_OUTPUT_DIRS
    CONFIGURATION_TYPES ${CMAKE_BUILD_TYPE}
    SETTINGS ${CONAN_SETTINGS}
)

set(HDI_LIB_ROOT "${CONAN_HDILIB_ROOT}")
set(HDI_INCLUDE_ROOT "${CONAN_INCLUDE_DIRS_HDILIB}/HDILib")
if(WIN32)
    set(FLANN_BUILD_DIR "${CONAN_FLANN_ROOT}")
endif()

if(MSVC)
    set(ENV{CC} ${CC_CACHE}) # Restore vars
    set(ENV{CXX} ${CXX_CACHE})
endif()

message(STATUS "End ConanSetup")

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
