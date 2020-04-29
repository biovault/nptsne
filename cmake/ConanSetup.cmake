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

set(CONAN_REQUIRES
    pybind11/2.2.4@conan/stable
    HDILib/latest@biovault/stable
    glfw/3.3.2@bincrafters/stable
    lz4/1.9.2
    CACHE INTERNAL ""
)

set(CONAN_OPTIONS
    HDILib:shared=False
    CACHE INTERNAL ""
)  

set(CONAN_IMPORTS "")
if(APPLE)
    set(CONAN_IMPORTS ${CONAN_IMPORTS} "lib, *.dylib* -> ./lib")
endif()
if(MSVC)
    set(CONAN_IMPORTS ${CONAN_IMPORTS} "bin, *.dll* -> ./bin")
endif()
if(UNIX AND NOT APPLE)
    set(CONAN_IMPORTS ${CONAN_IMPORTS} "lib, *.so* -> ./lib")
    set(CONAN_IMPORTS ${CONAN_IMPORTS} "plugins/platforms, *.so* -> ./bin/platforms")
endif()

file(TIMESTAMP ${CMAKE_BINARY_DIR}/conan_install_timestamp.txt file_timestamp "%Y.%m.%d")
string(TIMESTAMP timestamp "%Y.%m.%d")

# Run conan install update only once a day
if("${file_timestamp}" VERSION_LESS ${timestamp} OR IS_CI)
    file(WRITE ${CMAKE_BINARY_DIR}/conan_install_timestamp.txt "${timestamp}\n")
    set(CONAN_UPDATE UPDATE)
    conan_add_remote(NAME conan-hdim INDEX 0 
        URL http://cytosplore.lumc.nl:8081/artifactory/api/conan/conan-local)
    conan_add_remote(NAME bincrafters INDEX 1
        URL https://api.bintray.com/conan/bincrafters/public-conan)
else()
    message(STATUS "Conan: Skipping update step.")
endif()

if(MSVC)
    set(CC_CACHE $ENV{CC})
    set(CXX_CACHE $ENV{CXX})
    unset(ENV{CC}) # Disable clcache, e.g. for building qt
    unset(ENV{CXX})
endif()
conan_cmake_run(
    BASIC_SETUP
    ${CONAN_UPDATE}
    KEEP_RPATHS
    REQUIRES ${CONAN_REQUIRES}
    OPTIONS ${CONAN_OPTIONS}
    BUILD ${OGS_CONAN_BUILD}
    IMPORTS ${CONAN_IMPORTS}
    GENERATORS virtualrunenv
    BUILD_TYPE ${CMAKE_BUILD_TYPE}
)

if(MSVC)
    set(ENV{CC} ${CC_CACHE}) # Restore vars
    set(ENV{CXX} ${CXX_CACHE})
endif()

message(STATUS "End ConanSetup")
