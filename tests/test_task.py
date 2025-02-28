from tinytask.task import Signature


def test_signature_composition():
    s1 = Signature(lambda x: x + 1, args=(3,))
    s2 = Signature(lambda x: x * 2)
    s3 = s1 | s2
    assert s3().arg == 8
