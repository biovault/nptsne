set(CONAN_LOGIN_USERNAME $ENV{CONAN_LOGIN_USERNAME})
set(CONAN_PASSWORD $ENV{CONAN_PASSWORD})

find_file(NPTSNE_WHEEL "${WHEEL_GLOB}")
message(STATUS "About to upload: ${NPTSNE_WHEEL}")
file(UPLOAD ${NPTSNE_WHEEL} "http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/latest" USERPWD ${CONAN_LOGIN_USERNAME}:${CONAN_PASSWORD})
