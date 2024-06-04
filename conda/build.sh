
cd ${SRC_DIR}/src/f90

echo "Building interface pyratp.pyf"
${PYTHON}  -m numpy.f2py -m pyratp -h pyratp.pyf mod_Cocnstant_ValuesF2PY.f90 \
 mod_Grid3DF2PY_64bit.f90 mod_SkyvaultF2PY.f90 \
 mod_Vegetation_TypesF2PY.f90 \
 mod_Dir_InterceptionF2PY.f90 \
 mod_Hemi_InterceptionF2PY.f90 \
 mod_MicrometeoF2PY.f90  \
 mod_Shortwave_BalanceF2PY.f90\
 mod_Energy_BalanceF2PY.f90 \
 mod_PhotosynthesisF2PY.f90 \
 mod_MinerPhenoF2PY.f90 \
 prog_RATP.f90 --lower

${PYTHON}  -m numpy.f2py -c --fcompiler=gnu95 --build-dir $BUILD_PREFIX  pyratp.pyf mod_Cocnstant_ValuesF2PY.f90 \
                mod_Grid3DF2PY_64bit.f90 \
                mod_SkyvaultF2PY.f90 \
                mod_Vegetation_TypesF2PY.f90 \
                mod_Dir_InterceptionF2PY.f90 \
                mod_Hemi_InterceptionF2PY.f90 \
                mod_MicrometeoF2PY.f90  \
                mod_Shortwave_BalanceF2PY.f90\
                mod_Energy_BalanceF2PY.f90 \
                mod_PhotosynthesisF2PY.f90 mod_MinerPhenoF2PY.f90 prog_RATP.f90 --backend meson



echo "MOVE pyratp.so"

mv pyratp.*so ../alinea/pyratp/.

cd ${SRC_DIR}

echo "pip install"
pip install .
