from conans.client.command import Command, Conan
from conans.client import conan_api
import pprint
import urllib.request
import tarfile
import shutil
import os
import pycurl
import subprocess
import argparse

# Retrieve the nptsne conan packages for all the supported os
# versions and python versions. Extract the *.whl files from
# the dist dir in the conan_package.tgz. Arrange the *whl files
# into separate subdirectories based on the python version.

def main(pypi, to_arti):
    remote="conan-hdim"  # conan-hdim: http://cytosplore.lumc.nl:8081/artifactory/api/conan/conan-local
    remote_url_base="http://cytosplore.lumc.nl:8081/artifactory/conan-local"
    version="1.0.0rc5"
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
    
    for vers in python_versions:
        ver_dir = './{}'.format(vers)
        if os.path.exists(ver_dir):
            shutil.rmtree(ver_dir)
 
        
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
                # Simply using tarfile.open seems to be robust.
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


    if to_arti:
        # Don't forget to setup the netrc with login & password for the artifactory
        c = pycurl.Curl()
        for wheel_name in os.listdir('./linuxwheels'):
            c.setopt(c.URL, 'http://cytosplore.lumc.nl:8081/artifactory/wheels/nptsne/{}'.format(wheel_name))
            c.setopt(c.UPLOAD, 1)
            c.setopt(c.NETRC, 1)
            with open('./linuxwheels/{}'.format(wheel_name), 'rb') as file:
                c.setopt(c.READDATA, file)
                c.perform()
            print('Uploaded {}'.format(wheel_name))
        c.close()

    if pypi == "testpypi":
        subprocess.run(["twine", "upload", "--verbose", "-r", "testpypi", "wheels/*{}*".format(version)])
    if pypi == "releasepypi":
        subprocess.run(["twine", "upload", "--verbose", "wheels/*{}*".format(version)])
        
if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(description='Distribute the wheels from the Artifactory')
    parser.add_argument('--pypi', help='Upload Win and Mac wheels to test (default) or release pypi', default='testpypi', choices=['testpypi', 'releasepypi'])
    parser.add_argument('--lart', help='Upload linux wheels to artifactory', action="store_true")
    args = parser.parse_args()
    
    main(args.pypi, args.lart)

# To discove platform tags: 
# python -c "import pprint;from wheel import pep425tags;pprint.pprint(pep425tags.get_supported())"