# Copy from apexpy on github

project('PyRATP', 'c',
  version : '0.12',
  license: 'CeCILL-C',
  meson_version: '>=0.64.0',
  default_options: [
    'buildtype=debugoptimized',
    # TODO: the below -Wno flags are all needed to silence warnings in
    # f2py-generated code. This should be fixed in f2py itself.
    'c_args=-Wno-unused-function -Wno-conversion -Wno-misleading-indentation -Wno-incompatible-pointer-types',
    'fortran_args=-Wno-conversion',  # silence "conversion from REAL(8) to INTEGER(4)"
    'fortran_std=legacy',
  ],
)

add_languages('fortran', native: false)

ff = meson.get_compiler('fortran')
cc = meson.get_compiler('c')

if ff.has_argument('-Wno-conversion')
  add_project_arguments('-Wno-conversion', language: 'fortran')
endif


if host_machine.system() == 'darwin' and cc.has_link_argument('-Wl,-ld_classic')
  # New linker introduced in macOS 14 not working yet, see gh-19357 and gh-19387
  add_project_link_arguments('-Wl,-ld_classic', language : ['c', 'cpp', 'fortran'])
endif

numpy_nodepr_api = '-DNPY_NO_DEPRECATED_API=NPY_1_9_API_VERSION'

# This argument is called -Wno-unused-but-set-variable by GCC, however Clang
# doesn't recognize that.
if cc.has_argument('-Wno-unused-but-set-variable')
  add_global_arguments('-Wno-unused-but-set-variable', language : 'c')
endif

# https://mesonbuild.com/Python-module.html
py_mod = import('python')
py3 = py_mod.find_installation()
py3_dep = py3.dependency()
message(py3.full_path())
message(py3.get_install_dir())


incdir_numpy = run_command(py3,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

incdir_f2py = run_command(py3,
  ['-c', 'import os; os.chdir(".."); from numpy import f2py; print(f2py.get_include())'],
  check : true
).stdout().strip()

inc_dirs = include_directories(incdir_numpy, incdir_f2py)

# Don't use the deprecated NumPy C API. Define this to a fixed version instead of
# NPY_API_VERSION in order not to break compilation for released SciPy versions
# when NumPy introduces a new deprecation. Use in a meson.build file::
#
#   py3.extension_module('_name',
#     'source_fname',
#     numpy_nodepr_api)
#
c_flags = ['-DNPY_NO_DEPRECATED_API=NPY_1_9_API_VERSION']

# Check the python headers
cc.check_header('Python.h', dependencies: [py3_dep], required: true)

# Unlike distutils, meson doesn't yet include some of the f2py stuff
fortranobject_c = incdir_f2py / 'fortranobject.c'


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
    'src/f90/prog_RATP.f90'
  ])


ratp_source = custom_target('pyratp.pyf',
  input : sources,  # .f so no F90 wrappers
  output : ['pyratp.pyf'],
  command : [py3, '-m', 'numpy.f2py', '-m', 'pyratp', '-h', '@OUTPUT@', '@INPUT@', '--lower']
)


ratp_lib = custom_target('libpyratp',
  input : [ratp_source, sources],  # .f so no F90 wrappers
  output : ['pyratp.cpython-312-darwin.so'],
  command : [py3, '-m', 'numpy.f2py', '-c',  '@INPUT@', '--backend', 'meson'],
  install : true,
  install_dir: 'alinea/pyratp/',
)

# Declare the sources
py3.install_sources([
  'src/alinea/pyratp/__init__.py',
  'src/alinea/pyratp/can2riri.py',
  'src/alinea/pyratp/clumping_index.py',
  'src/alinea/pyratp/energy_balance.py',
  'src/alinea/pyratp/grid.py',
  'src/alinea/pyratp/hemi_interception.py',
  'src/alinea/pyratp/interception.py',
  'src/alinea/pyratp/IOtable.py',
  'src/alinea/pyratp/micrometeo.py',
  'src/alinea/pyratp/mtg2ratp.py',
  'src/alinea/pyratp/Nallocate.py',
  'src/alinea/pyratp/photosynthesis.py',
  'src/alinea/pyratp/RATP2VTK.py',
  'src/alinea/pyratp/RatpScene.py',],
  pure: false,
  subdir:'alinea/pyratp')