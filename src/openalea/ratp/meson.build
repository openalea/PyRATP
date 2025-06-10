

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

sources = files([
  '../../f90/mod_Constant_ValuesF2PY.f90',
  '../../f90/mod_Grid3DF2PY_64bit.f90',
  '../../f90/mod_SkyvaultF2PY.f90',
  '../../f90/mod_Vegetation_TypesF2PY.f90',
  '../../f90/mod_Dir_InterceptionF2PY.f90',
  '../../f90/mod_Hemi_InterceptionF2PY.f90',
  '../../f90/mod_MicrometeoF2PY.f90',
  '../../f90/mod_Shortwave_BalanceF2PY.f90',
  '../../f90/mod_Energy_BalanceF2PY.f90',
  '../../f90/mod_PhotosynthesisF2PY.f90',
  '../../f90/mod_MinerPhenoF2PY.f90',
  '../../f90/mod_prog_RATP.f90'
])

# manage the numpy lib and include
incdir_numpy = run_command(py, [
    '-c',
    '''import os, numpy as np
try:
    print(os.path.abspath(np.get_include()))
except:
    print(np.get_include())
    ''',
], check: true).stdout().strip()
incdir_f2py = incdir_numpy / '..' / '..' / 'f2py' / 'src'
fortranobject_c = incdir_f2py / 'fortranobject.c'



ratp_source = custom_target('pyratpmodule.c',
  input : sources,
  output : ['pyratpmodule.c', 'pyratp-f2pywrappers2.f90'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'pyratp', '--build-dir', '@OUTDIR@', '--lower']
)

inc_np = include_directories(incdir_numpy, incdir_f2py)

py.extension_module('pyratp',
  [sources, ratp_source],
  fortranobject_c,
  include_directories: inc_np,
  dependencies : py_dep,
  install : true,
  link_language: 'fortran',
  subdir: 'openalea/ratp',
)

python_sources = [
  '__init__.py',
  'can2riri.py',
  'clumping_index.py', 
  'energy_balance.py',
  'grid.py',
  'hemi_interception.py',
  'interception.py',
  'IOtable.py',
  'micrometeo.py',
  'miner_pheno.py',
  'mtg_extract.py',
  'mtg2ratp.py',
  'Nallocate.py',
  'photosynthesis.py',
  'RATP2VTK.py',
  'RatpScene.py',
  'runratp.py',
  'shortwave_balance.py',
  'skyvault.py',
  'vegetation_types.py',
  'vegetation.py',  
  'vege3D.py',
]

py.install_sources(
  python_sources,
  pure: false,
  subdir: 'openalea/ratp'
)

subdir('interface')
