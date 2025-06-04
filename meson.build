project('PyRATP', 'fortran',
  version : '0.1',
  default_options : ['warning_level=3'])

sources = files([
  'src/f90/mod_Cocnstant_ValuesF2PY.f90',
  'src/f90/mod_Grid3DF2PY_64bit.f90',
  'src/f90/mod_SkyvaultF2PY.f90',
  'src/f90/mod_Vegetation_TypesF2PY.f90',
  'src/f90/mod_Dir_InterceptionF2PY.f90',
  'src/f90/mod_Hemi_InterceptionF2PY.f90',
  'src/f90/mod_MicrometeoF2PY.f90',
  'src/f90/mod_Shortwave_BalanceF2PY.f90',
  'src/f90/mod_Energy_BalanceF2PY.f90',
  'src/f90/mod_PhotosynthesisF2PY.f90',
  'src/f90/mod_MinerPhenoF2PY.f90',
  'src/f90/mod_prog_RATP.f90'
])

shared_library('PyRATP', sources, install : true)

