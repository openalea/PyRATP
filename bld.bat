@echo off

REM Add list of fortran files to variable %fortranfiles%
set fortranfiles=src\f90\mod_Cocnstant_ValuesF2PY.f90 ^
src\f90\mod_Grid3DF2PY_64bit.f90 ^
src\f90\mod_SkyvaultF2PY.f90 ^
src\f90\mod_Vegetation_TypesF2PY.f90 ^
src\f90\mod_Dir_InterceptionF2PY.f90 ^
src\f90\mod_Hemi_InterceptionF2PY.f90 ^
src\f90\mod_MicrometeoF2PY.f90 ^
src\f90\mod_Shortwave_BalanceF2PY.f90 ^
src\f90\mod_Energy_BalanceF2PY.f90 ^
src\f90\mod_PhotosynthesisF2PY.f90 ^
src\f90\mod_MinerPhenoF2PY.f90 ^
%SRC_DIR%\f90\prog_RATP.f90

echo:

REM display current directory
echo:"current directory: " %cd%

echo:

echo:"creation of the header
%PYTHON% -m numpy.f2py -m pyratp -h %fortranfiles% --lower
if errorlevel 1 echo Unsuccessful
echo:

echo:"library compilation into build-folder"
%PYTHON% -m numpy.f2py -c pyratp.pyf %fortranfiles%  --fcompiler=gnu95 --backend meson
if errorlevel 1 echo Unsuccessful
echo:

echo:"moving pyratp*.pyd to %SRC_DIR%/alinea/pyratp/pyratp.pyd"
move /Y pyratp*.pyd %SRC_DIR%/alinea/pyratp/pyratp.pyd
if errorlevel 1 echo Unsuccessful
echo:

echo:"setup.py install"
%PYTHON% setup.py install --prefix=%PREFIXM%
if errorlevel 1 echo Unsuccessful
echo:
