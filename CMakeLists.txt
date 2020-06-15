cmake_minimum_required(VERSION 3.15.0)

file (STRINGS "version.txt" VERSION)
project(_nptsne LANGUAGES CXX)

# Disallow in-source builds. 
# Build in sub dir e.g. source/build* is still allowed!
if("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
   message(FATAL_ERROR "In-source builds are not allowed!\n"
    "Make sure to remove CMakeCache.txt and CMakeFiles/ "
    "from the source directory!")
endif()

option(NPTSNE_BUILD_WITH_CONAN "Should Conan package manager be used?" ON)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
  "${PROJECT_SOURCE_DIR}/cmake")

set(CMAKE_CONFIGURATION_TYPES ${CMAKE_BUILD_TYPE})

# A PEP 440 version is set in version.txt - this is not compatible with the CMAKE config
message(STATUS "Building in ${CMAKE_BINARY_DIR}")

execute_process(
  COMMAND git rev-parse --abbrev-ref HEAD
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE GIT_BRANCH
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Working on branch ${GIT_BRANCH}")

file(REMOVE_RECURSE ${CMAKE_BINARY_DIR}/dist)
file(REMOVE_RECURSE _nptsne.egg-info)
file(REMOVE_RECURSE _skbuild)

# The python files for the package
#file(COPY "${PROJECT_SOURCE_DIR}/dist_root" 
#    DESTINATION "${CMAKE_BINARY_DIR}" 
#    FILES_MATCHING REGEX ".*\.py|.*\.md|.*\.txt|.*\.in")
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/dist_root)
    
file(GENERATE OUTPUT ${CMAKE_BINARY_DIR}/dist_root/nptsne/_version.txt CONTENT "${VERSION}")

# CONAN is only used if the NPTSNE_BUILD_WITH_CONAN is ON
include(ConanSetup)

message(STATUS "Processing directory: ${CMAKE_CURRENT_SOURCE_DIR}")

find_package (Python3 COMPONENTS Interpreter Development)

if (WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS True)
endif()

set(BUILD_PYTHON_VERSION "${Python3_VERSION}")
set(PYBIND11_PYTHON_VERSION "${Python3_VERSION}")
set(PY_TAG "cp${Python3_VERSION_MAJOR}${Python3_VERSION_MINOR}")

message(STATUS "Build Python version ${BUILD_PYTHON_VERSION}")
find_package(pybind11 REQUIRED)

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
    nptsne_src/.editorconfig
	nptsne_src/nptSNEBind.cpp
    nptsne_src/Analysis.cpp
    nptsne_src/HSne.cpp
    nptsne_src/SparseTsne.cpp    
	nptsne_src/TextureTsne.cpp
	nptsne_src/TextureTsneExtended.cpp
)

# In VisualStudio we show the python files in the bdist_wheel 
# custom targetfor ease of editing and debug
if(MSVC_IDE)
    file(GLOB_RECURSE DIST_ROOT_FILES "dist_root/*.*")
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

    GroupSources("dist_root")
else()
    set(DIST_ROOT_FILES "")    
endif()    

message(STATUS "DIST_ROOT_FILES: ${DIST_ROOT_FILES}")

pybind11_add_module(${PROJECT_NAME} ${NPTSNE_FILES})

find_package(OpenGL REQUIRED)
if(NOT APPLE)
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
endif()
    
message(STATUS "CXX compiler ${CMAKE_CXX_COMPILER}")
if (APPLE)
  add_definitions(-DGL_SILENCE_DEPRECATION)
  set(CMAKE_OSX_DEPLOYMENT_TARGET "10.12" CACHE STRING "Minimum OS X deployment version")
  if(DEFINED ENV{TRAVIS_OS_NAME} AND ("$ENV{TRAVIS_OS_NAME}" STREQUAL "osx"))
    find_program(BREW NAMES brew)
    set(BREW "HOMEBREW_NO_AUTO_UPDATE=1 ${BREW}")
    message(STATUS, "In Macos with ${BREW}")
    
    #### Install LIBOMP
    execute_process(COMMAND ${BREW} --prefix libomp OUTPUT_VARIABLE BREW_LIBOMP_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    message(STATUS, "BREW LIBOMP ${BREW_LIBOMP_PREFIX}")
    set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp")
    set(OpenMP_CXX_LIB_NAMES "omp")
    set(OpenMP_omp_LIBRARY "${BREW_LIBOMP_PREFIX}/lib/libomp.dylib")
    include_directories("${BREW_LIBOMP_PREFIX}/include") 
    
    #### Install flann
    execute_process(COMMAND ${BREW} --prefix flann OUTPUT_VARIABLE BREW_FLANN_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    include_directories("${BREW_FLANN_PREFIX}/include")  
	find_library(FLANNCPP_LIBRARY flann_cpp HINTS "${BREW_FLANN_PREFIX}")
    get_filename_component(FLANNCPP_LIBRARY_PATH ${FLANNCPP_LIBRARY} REALPATH) 
    get_short_version_number(${FLANNCPP_LIBRARY_PATH} FLANNCPP_SHORTNAME)
    
    #### Install lz4    
    execute_process(COMMAND ${BREW} --prefix lz4 OUTPUT_VARIABLE BREW_LZ4_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    include_directories("${BREW_LZ4_PREFIX}/include") 
    find_library(LZ4_LIBRARY lz4 HINTS "${BREW_LZ4_PREFIX}")    
    get_filename_component(LZ4_LIBRARY_PATH ${LZ4_LIBRARY} REALPATH)
    # lz4 link chops two digits from the version 
    # (this probably a bug due to the library name ending in a digit)
    get_shorter_version_number(${LZ4_LIBRARY_PATH} LZ4_SHORTNAME)
   
    #### Install glfw
    execute_process(COMMAND ${BREW} --prefix glfw OUTPUT_VARIABLE BREW_GLFW_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    include_directories("${BREW_GLFW_PREFIX}/include") 
    find_library(GLFW_LIBRARY glfw HINTS "${BREW_GLFW_PREFIX}")    
    get_filename_component(GLFWLIBRARY_PATH ${GLFW_LIBRARY} REALPATH)
    get_short_version_number(${GLFWLIBRARY_PATH} GLFW_SHORTNAME)    
    include_directories(${GLFW_INCLUDE_DIRS} "/usr/local/include")     

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

set(HDIDR_BUILD_DIR "${HDI_LIB_ROOT}/dimensionality_reduction")  
set(HDIDA_BUILD_DIR "${HDI_LIB_ROOT}/data") 
set(HDIUI_BUILD_DIR "${HDI_LIB_ROOT}/utils") 

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

message(STATUS "SHARED_LINKER_FLAGS: ${CMAKE_SHARED_LINKER_FLAGS}")

# Install phase - move the extension plus and libraries necessary to
# an install destination where they can be bundled in a separate invocation
# of python setup.py bdist_wheel
# P.S. This is using the CMake install for moving files around prior to bundling
# the python wheel. 

# Move the binary extension - .pyd, .so, or .dylib (depending on OS) for wheel building
install(TARGETS ${PROJECT_NAME} DESTINATION "${CMAKE_BINARY_DIR}/dist_root/nptsne/libs/")

#  For MacOs or Linux the binary extension needs to load the glfw flann and lz4 from its own directory
# use the intall_name_tool to fix this. This code makes two scripts getname.sh and fixup.sh
# which are used to get the path to the extension and to modify it.
if(APPLE)
    message(STATUS "Otool fixup for OSX")
	install(CODE "
		execute_process(
            COMMAND ${CMAKE_COMMAND} -E echo \"Install target file:\"
            COMMAND ${CMAKE_COMMAND} -E echo $<TARGET_FILE:${PROJECT_NAME}>)
        execute_process(    
			COMMAND sh -c \"echo 'A=`ls ${CMAKE_BINARY_DIR}/dist_root/nptsne/libs/*.so` && echo $A' > ~/getname.sh && cat ~/getname.sh\"
            WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})
		execute_process(
			COMMAND sh -c \"chmod +x ~/getname.sh\"
			WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX})
		execute_process(
			COMMAND sh -c \"rm -f ~/fixup.sh && otool -L `~/getname.sh` | grep -E 'glfw|flann|lz4' | cut -f 1 -d ' ' | xargs -I ! sh -c 'A=! && A=`basename $A` && echo install_name_tool -change $A @loader_path/$A `~/getname.sh` >> ~/fixup.sh'\"
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
  

# Platform specific libs
if(CMAKE_SYSTEM_NAME STREQUAL Linux)
    # In linux bundle prebuilt libflann and liblz4
    install(FILES ${LZ4_LIBRARY_PATH} DESTINATION "dist_root/nptsne/libs" RENAME liblz4.so)
    install(FILES ${FLANNCPP_LIBRARY_PATH} DESTINATION "dist_root/nptsne/libs" RENAME libflann_cpp.so)
    install(FILES ${GLFWLIBRARY_PATH} DESTINATION "dist_root/nptsne/libs" RENAME libglfw.so)
endif()	

if(APPLE)
	message(STATUS "Will deploy lz4, flann_cpp and glfw as: ${LZ4_SHORTNAME} ${FLANNCPP_SHORTNAME} ${GLFW_SHORTNAME}")
    install(FILES ${LZ4_LIBRARY_PATH} DESTINATION "dist_root/nptsne/libs" RENAME ${LZ4_SHORTNAME})
    install(FILES ${FLANNCPP_LIBRARY_PATH} DESTINATION "dist_root/nptsne/libs" RENAME ${FLANNCPP_SHORTNAME})
    install(FILES ${GLFWLIBRARY_PATH} DESTINATION "dist_root/nptsne/libs" RENAME ${GLFW_SHORTNAME})
    file(GLOB_RECURSE PACKAGE_FILES RELATIVE "dist_root/nptsne" "*.*")
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

set(CAT_COMMAND cat)
if(APPLE)
  set(PLAT_NAME "macosx-10.6-intel")
elseif(UNIX)
  set(PLAT_NAME "linux_x86_64")
elseif(WIN32)
  set(PLAT_NAME "win_amd64") 
  set(CAT_COMMAND echo)
endif()

# -- .whl creation
add_custom_target (bdist_wheel
    COMMAND ${CMAKE_COMMAND} -E echo "Building wheel for platform: ${PLAT_NAME} and python version: ${BUILD_PYTHON_VERSION}"
    # To debug install uncomment the following
    # COMMAND ${CAT_COMMAND} \"${CMAKE_BINARY_DIR}/cmake_install.cmake\"
    # First use install to move all the build outputs and libraries to the dist_root dir (needs at least CMake 3.15)
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${PROJECT_SOURCE_DIR}/dist_root ${CMAKE_BINARY_DIR}/dist_root
    COMMAND ${CMAKE_COMMAND} --install ${CMAKE_BINARY_DIR} --prefix ${CMAKE_BINARY_DIR} 
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_BINARY_DIR}/dist_root/setup.py bdist_wheel --plat-name=${PLAT_NAME} --dist-dir=${CMAKE_BINARY_DIR}/dist --python-tag=${PY_TAG} WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/dist_root
    DEPENDS ${PROJECT_NAME}  #depends on the pybind11 module (see pybind11_add_module above)
    SOURCES ${DIST_ROOT_FILES}
)

# -- module docstring extraction and upload - only in the windows build - we only have to do this once
if(WIN32)
add_custom_target(extract_module_docstring
    # Install the wheel to allow docstring extraction with autodoc
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/docsource/nptsnedoc
    COMMAND ${GIT_EXECUTABLE} 
    COMMAND cmd //c cd ${PROJECT_SOURCE_DIR}/docsource && pip --version && pip install --force-reinstall --find-links ${CMAKE_BINARY_DIR}/dist nptsne==${VERSION} && pip install -r ${PROJECT_SOURCE_DIR}/docsource/requirements.txt && ${PROJECT_SOURCE_DIR}/docsource/sphinx_rst_build.bat
    COMMENT "Extract the reStructuredText from the module" 
    DEPENDS bdist_wheel
)
endif()

if(WIN32 AND $ENV{CI})
find_package(Git REQUIRED)
add_custom_target(commit_doc    
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/docsource/nptsnedoc
    # Make sure the nptsnedoc has a branch matching this one
    COMMAND ${GIT_EXECUTABLE} switch -c $ENV{APPVEYOR_REPO_BRANCH}
    COMMAND ${PROJECT_SOURCE_DIR}/docsource/copy_generated_to_nptsnedoc.bat
    COMMAND ${GIT_EXECUTABLE} add --all . 
    COMMAND ${GIT_EXECUTABLE} commit --allow-empty -m "Update to nptsne ${VERSION}"
    COMMAND ${GIT_EXECUTABLE} push --set-upstream origin $ENV{APPVEYOR_REPO_BRANCH}
    COMMENT "Add any new doc files and commit + push to the nptsnedoc branch ${APPVEYOR_REPO_BRANCH} creating if necessary"
    DEPENDS extract_module_docstring
)
endif()

# -- Upload of latest whl
add_custom_target (upload_wheel
    COMMAND ${CMAKE_COMMAND} -D WHEEL_GLOB=${CMAKE_BINARY_DIR}/dist/nptsne*.whl -P ${CMAKE_CURRENT_LIST_DIR}/cmake/UploadWheel.cmake
)
