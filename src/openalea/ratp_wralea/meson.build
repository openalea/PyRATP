py_mod = import('python')
py = py_mod.find_installation(pure: false)


python_sources = [
  '__init__.py',
  '__wralea__.py',
  'ExtractColumn.py',
  'ExtractLight.py',
  'ExtractVar.py',
  'Plot3DRATP.py',
  'ratp.py',
  'WidgetUIRATP_Grid.py',
  'WidgetUIRATP_Vege.py',
]

py.install_sources(
  python_sources,
  pure: false,
  subdir: 'openalea/ratp_wralea'
)

