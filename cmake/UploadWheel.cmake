# Provide the following defines
# WHEEL_GLOB - a glob wildcard expression that will resolve to a list of wheel files
# BUILD_NUMBER - a unique number for this build used to store the wheels
# CERT_FILE - the certificate file for the artifactory (needed due to CA issues)
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
    file(UPLOAD ${WHEEL} "https://lkeb-artifactory.lumc.nl/artifactory/wheels/nptsne/build_${BUILD_NUMBER}/${NPTSNE_WHEEL_NAME}"
        USERPWD ${CONAN_LOGIN_USERNAME}:${CONAN_PASSWORD}
        HTTPHEADER "X-Checksum-md5: ${NPTSNE_WHEEL_MD5}"
        TLS_VERIFY ON
        TLS_CAINFO ${CERT_FILE})
endforeach()
