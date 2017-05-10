# -*- coding: utf-8 -*-
from sanic_wtf import ChainRequestParameters


def test_chainrequestparameters():
    r1 = {
        'a': [1, 2, 3],
        'b': [4, 5, 6],
    }

    r2 = {
        'b': [7, 8, 9],
        'd': [10, 11, 12],
    }

    crp = ChainRequestParameters(r1, r2)

    assert crp.get('a') == 1
    assert crp.getlist('a') == [1, 2, 3]
    assert crp.getlist('b') == [4, 5, 6]
    assert crp.get('d') == 10
    assert crp.getlist('d') == [10, 11, 12]

    crp = ChainRequestParameters(r2, r1)

    assert crp.get('a') == 1
    assert crp.getlist('a') == [1, 2, 3]
    assert crp.getlist('b') == [7, 8, 9]
    assert crp.get('d') == 10
    assert crp.getlist('d') == [10, 11, 12]
