make pyratp.pyd

echo "MOVE ppyratp.so"

mv pyratp.*so $SRC_DIR/src/alinea/pyratp/.

echo "pip install"
${PYTHON} setup.py install --prefix=${PREFIX} 
