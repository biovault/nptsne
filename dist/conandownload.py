from conans.client.command import Command, Conan
from conans.client import conan_api
import pprint
import urllib.request
import tarfile
import shutil
import os

# Retrieve the nptsne conan packages for all the supported os
# versions and python versions. Extract the *.whl files from
# the dist dir in the conan_package.tgz. Arrange the *whl files
# into separate subdirectories based on the python version.

remote="conan-hdim"  # conan-hdim: http://cytosplore.lumc.nl:8081/artifactory/api/conan/conan-local
remote_url_base="http://cytosplore.lumc.nl:8081/artifactory/conan-local"
version="1.0.0rc3"
package_reference = "nptsne/" + version + "@lkeb/stable"
url_reference = "lkeb/nptsne/" + version + "/stable"
packages_queries=["os=Windows", "os=Linux", "os=Macos"]
python_versions=["3.6", "3.7"]
conan_api, cache, user_io = Conan.factory()

command = Command(conan_api)

if os.path.exists('./linuxwheels'):
    shutil.rmtree('./linuxwheels')
os.makedirs('./linuxwheels')
    
if os.path.exists('./wheels'):
    shutil.rmtree('./wheels')
os.makedirs('./wheels')    
    
# Get the conan tgz for each package
for query in packages_queries:
    print(package_reference, query,'\n')
    ret = conan_api.search_packages(package_reference, remote_name=remote, query=query)
    result_list = ret['results'] 
    package_list = result_list[0]['items'][0]['packages']
    for package in package_list:
        if package['options'].get('python_version', None) in python_versions:
            pyver = package['options']['python_version']
            print(query, pyver, package['id'])
            reference = "{}:{}".format(package_reference, package['id'])
            print(reference)
            url_path = "{}/{}/0/package/{}/0/conan_package.tgz".format(remote_url_base, url_reference, package['id'])
            local_filename, headers = urllib.request.urlretrieve(url_path, filename=pyver + "_" + package['id'] + ".tgz")
            print(local_filename)
            
            # Open the complete package tgz file. 
            # Using the TarFile init does not work - settings problem?
            # SImply using tarfile.open seems to be robust.
            conantar = tarfile.open(local_filename)
            print("Get members")
            mems = conantar.getmembers()
            print("total contents: ", len(mems))
            
            #Extract the wheel from the dist directory.
            whls = [mem for mem in mems if mem.name.startswith("dist") and mem.name.endswith(".whl")]
            print("wheels: ", len(whls))
            conantar.extract(whls[0], path=pyver)
            # Skip linux for pypi upload 
            # TODO make manylinux2010 wheels
            if "linux" in whls[0].name:
                shutil.copy(os.path.join('./', pyver, whls[0].name), './linuxwheels')
            else:
                shutil.copy(os.path.join('./', pyver, whls[0].name), './wheels')
                
            conantar.close()
                

# Move the whl to the wheels directory and run
# twine upload --verbose -r testpypi wheels/nptsne-1.0.0rc2*
# To discove platform tags: 
# python -c "import pprint;from wheel import pep425tags;pprint.pprint(pep425tags.get_supported())"