py_mod = import('python')
py = py_mod.find_installation(pure: false)


python_sources = [
  '__init__.py',
  '__wralea__.py',
]

py.install_sources(
  python_sources,
  pure: true,
  subdir: 'openalea/ratp_wralea/demo'
)
