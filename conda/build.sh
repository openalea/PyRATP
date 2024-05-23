make pyratp.pyd

mv pyratp.*so $SRC_DIR/src/alinea/pyratp/.
{{ PYTHON }} -m pip install --no-deps --ignore-installed --no-build-isolation . -vv