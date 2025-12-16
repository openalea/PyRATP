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
  'WidgetUiRATP_Grid.py',
  'WidgetUiRATP_Vege.py',
]

py.install_sources(
  python_sources,
  subdir: 'openalea/ratp_wralea'
)

subdir('data') 
subdir('demo') 
