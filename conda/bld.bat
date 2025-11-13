@echo off
call "%ProgramFiles%\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat"
set "CC=cl"
set "FC=flang-new"
set "MESON_RSP_THRESHOLD=320000"
%python% -m pip install . --no-deps --ignore-installed --no-build-isolation -vv