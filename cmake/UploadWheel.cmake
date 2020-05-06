set(CONAN_LOGIN_USERNAME $ENV{CONAN_LOGIN_USERNAME})
set(CONAN_PASSWORD $ENV{CONAN_PASSWORD})

message(STATUS "Looking for: ${WHEEL_GLOB}")
file(GLOB NPTSNE_WHEEL "${WHEEL_GLOB}")
message(STATUS "About to upload: ${NPTSNE_WHEEL}")
get_filename_component(NPTSNE_WHEEL_NAME ${NPTSNE_WHEEL} NAME)
file(UPLOAD ${NPTSNE_WHEEL} "http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/latest/${NPTSNE_WHEEL_NAME}" USERPWD ${CONAN_LOGIN_USERNAME}:${CONAN_PASSWORD})
