py_mod = import('python')
py = py_mod.find_installation(pure: false)


python_sources = [
  '__init__.py',
  '__wralea__.py',
]

py.install_sources(
  python_sources,
  pure: false,
  subdir: 'openalea/ratp_wralea/data'
)

data_sources = [
  'AA2004_charp_ok.vgx',
  'AA2004_ok.vgx',
  'aa2004pastroppetit.vgx',
  'grass_plt.can',
  'grid3D_AA2004.grd',
  'grid3Da_2004.grd',
  'matGridRATP_demo.mat',
  'mmeteo052000.mto',
  'mmeteo082050_1h.mto',
  'mtg_test.txt',
  'MinePommier2004.veg',
  'PommierSuisse2004.veg',
  'skyvaultsoc.skv',
  'vegetationa_2004.vfn',
  'vgxTestTriangles.vgx',
]

py.install_data(
  data_sources,
  install_dir: 'openalea/ratp_wralea/data'
)
