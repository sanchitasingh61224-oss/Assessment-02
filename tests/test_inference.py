import inspect

from scripts import inference


def test_reasoner_uses_input_relation():
    source = inspect.getsource(inference.reasoner)
    assert "relation='spouse'" not in source
