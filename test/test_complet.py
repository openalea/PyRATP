from pytest import fixture
from openalea.core.pkgmanager import PackageManager

""" A unique PackageManager is created for all test of dataflow """

@fixture
def pm():
    _pm = PackageManager()
    _pm.init(verbose=False)
    return _pm

def test_complet(pm):
    factory = pm['demo.ratp']['RATPTuto_Complet']
    cn = factory.instantiate()
    cn.eval_as_expression(6)

def test_can(pm):
    factory = pm['demo.ratp']['RATPTuto_CanFile']
    cn = factory.instantiate()
    cn.eval_as_expression(15)
    result = cn.node(15).get_output(0)
    
    assert len(result) == 170
    assert result.shape == (170,11)
    #assert 199 < result.mean() < 200


#test_complet()
