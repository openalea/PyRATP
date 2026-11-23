import os

import numpy

from openalea.ratp import vege3D

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def test_read_vgx():
    # expected values: output of the former QFile/QTextStream based reader
    vege3D.dicoInit()
    res = vege3D.Vege3D.readVGX(os.path.join(data_dir, 'aa2004petit.vgx'), 0.5, 2)
    assert res is not None
    types, x, y, z, s, n = res
    for a in res:
        assert a.shape == (10,)
    numpy.testing.assert_array_equal(types, 0)
    numpy.testing.assert_allclose(x, [-19.3, -17.2, -17.9, -18.3, -17.9, -18.6, -15.5, -15.8, -16.6, -12.3])
    numpy.testing.assert_allclose(y, [-22.3, -26.7, -24.8, -24.0, -27.7, -29.3, -30.9, -32.0, -35.7, -34.5])
    numpy.testing.assert_allclose(z, [-100.9, -103.3, -99.4, -103.2, -100.2, -104.5, -104.2, -108.0, -105.1, -109.1])
    # leaf area: EchX * EchY * allometric coefficient
    numpy.testing.assert_allclose(s, [11.55] * 5 + [23.66] * 5)
    numpy.testing.assert_array_equal(n, 2)


def test_read_vgx_missing_file(tmp_path):
    assert vege3D.Vege3D.readVGX(str(tmp_path / 'missing.vgx'), 0.5, 2) is None
