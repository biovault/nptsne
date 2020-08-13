set(CONAN_LOGIN_USERNAME $ENV{CONAN_LOGIN_USERNAME})
set(CONAN_PASSWORD $ENV{CONAN_PASSWORD})

message(STATUS "Looking for: ${WHEEL_GLOB}")
file(GLOB NPTSNE_WHEEL "${WHEEL_GLOB}")
message(STATUS "Found files: ${NPTSNE_WHEEL}")

foreach(WHEEL IN LISTS NPTSNE_WHEEL)
    message(STATUS "Upload file: ${WHEEL}")
    file(MD5 ${WHEEL} NPTSNE_WHEEL_MD5)
    message(STATUS "${WHEEL} with md5: ${NPTSNE_WHEEL_MD5}")
    get_filename_component(NPTSNE_WHEEL_NAME ${WHEEL} NAME)
    file(UPLOAD ${WHEEL} "http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/latest/${NPTSNE_WHEEL_NAME}"
        USERPWD ${CONAN_LOGIN_USERNAME}:${CONAN_PASSWORD}
        HTTPHEADER "X-Checksum-md5: ${NPTSNE_WHEEL_MD5}")
endforeach()
