@echo off

REM Add list of fortran files to variable %fortranfiles%
set fortranfiles=%SRC_DIR%\src\f90\mod_Cocnstant_ValuesF2PY.f90 ^
%SRC_DIR%\src\f90\mod_Grid3DF2PY_64bit.f90 ^
%SRC_DIR%\src\f90\mod_SkyvaultF2PY.f90 ^
%SRC_DIR%\src\f90\mod_Vegetation_TypesF2PY.f90 ^
%SRC_DIR%\src\f90\mod_Dir_InterceptionF2PY.f90 ^
%SRC_DIR%\src\f90\mod_Hemi_InterceptionF2PY.f90 ^
%SRC_DIR%\src\f90\mod_MicrometeoF2PY.f90 ^
%SRC_DIR%\src\f90\mod_Shortwave_BalanceF2PY.f90 ^
%SRC_DIR%\src\f90\mod_Energy_BalanceF2PY.f90 ^
%SRC_DIR%\src\f90\mod_PhotosynthesisF2PY.f90 ^
%SRC_DIR%\src\f90\mod_MinerPhenoF2PY.f90 ^
%SRC_DIR%\src\f90\prog_RATP.f90

echo:

REM display current directory
echo:"current directory: " %cd%

echo:

echo:"creation of the header
%PYTHON% -m numpy.f2py -m pyratp -h pyratp.pyf %fortranfiles% --lower
if errorlevel 1 echo Unsuccessful
echo:

echo:"library compilation into build-folder"
%PYTHON% -m numpy.f2py -c --compiler=mingw32 --fcompiler=gnu95 -DNPY_OS_MINGW=1 pyratp.pyf %fortranfiles%  
if errorlevel 1 echo Unsuccessful
echo:

echo:"moving pyratp*.pyd to %SRC_DIR%/src/alinea/pyratp/pyratp.pyd"
move /Y pyratp*.pyd %SRC_DIR%\src\alinea\pyratp\pyratp.pyd
if errorlevel 1 echo Unsuccessful
echo:

echo:"pip install"
python -m pip install  .
if errorlevel 1 echo Unsuccessful
echo:
