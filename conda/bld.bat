:: Working Dir
mkdir build
cd build

:: Build
cd ..
make  mode=develop
if errorlevel 1 exit 1