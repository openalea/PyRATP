cd src/f90

python -m numpy.f2py -m pyratp -h pyratp.pyf mod_Cocnstant_ValuesF2PY.f90 \
 mod_Grid3DF2PY_64bit.f90 \
 mod_SkyvaultF2PY.f90 \
 mod_Vegetation_TypesF2PY.f90 \
 mod_Dir_InterceptionF2PY.f90 \
 mod_Hemi_InterceptionF2PY.f90 \
 mod_MicrometeoF2PY.f90  \
 mod_Shortwave_BalanceF2PY.f90\
 mod_Energy_BalanceF2PY.f90 \
 mod_PhotosynthesisF2PY.f90 mod_MinerPhenoF2PY.f90 prog_RATP.f90 --lower

python -m numpy.f2py -c pyratp.pyf mod_Cocnstant_ValuesF2PY.f90 \
 mod_Grid3DF2PY_64bit.f90 \
 mod_SkyvaultF2PY.f90 \
 mod_Vegetation_TypesF2PY.f90 \
 mod_Dir_InterceptionF2PY.f90 \
 mod_Hemi_InterceptionF2PY.f90 \
 mod_MicrometeoF2PY.f90  \
 mod_Shortwave_BalanceF2PY.f90\
 mod_Energy_BalanceF2PY.f90 \
 mod_PhotosynthesisF2PY.f90 mod_MinerPhenoF2PY.f90 prog_RATP.f90 --backend meson


 cp pyratp*.so ../alinea/pyratp/.