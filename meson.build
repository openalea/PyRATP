project('PyRATP', 'c',
  version : '0.1',
  license: 'CeCILL-C',
  meson_version: '>=0.64.0',
  default_options : ['warning_level=2'],
)

add_languages('fortran')

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

incdir_numpy = run_command(py,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

incdir_f2py = run_command(py,
    ['-c', 'import os; os.chdir(".."); import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

inc_np = include_directories(incdir_numpy, incdir_f2py)

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
  command : [py, '-m', 'numpy.f2py', '-m', 'pyratp', '-h', '@OUTPUT@', '@INPUT@', '--lower']
)

ratp_lib = custom_target('libpyratp',
  input : [ratp_source, sources],  # .f so no F90 wrappers
  output : ['libpyratp'],
  command : [py, '-m', 'numpy.f2py', '-c',  '@INPUT@', '--backend', 'meson']
)

'''
py.extension_module('pyratp',
  [ratp_source, sources],
  incdir_f2py / 'fortranobject.c',
  c_args:NUMPY_NOPR_API,
  include_directories: inc_np,
  link_language: 'fortran',
  dependencies : py_dep,
  install : true
)
'''