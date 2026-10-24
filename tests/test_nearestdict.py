from datetime import timedelta

import pytest

from sortedcollections import NearestDict


def test_basic():
    d = NearestDict()

    with pytest.raises(KeyError):
        d[0]

    d[0] = 'a'
    assert d[0] == 'a'
    d[0] = 'b'
    assert d[0] == 'b'


def test_iteration():
    # In sorted order by key
    exp_items = (
        (0, 'a'),
        (1, 'b'),
        (2, 'c'),
    )

    d = NearestDict()
    for k, v in exp_items:
        d[k] = v

    for act, exp in zip(d.items(), exp_items):
        assert act == exp


def test_nearest():
    d = NearestDict(rounding=NearestDict.NEAREST)

    d[0] = 'a'
    d[3] = 'b'
    assert d[-1] == 'a'
    assert d[0] == 'a'
    assert d[1] == 'a'
    assert d[2] == 'b'
    assert d[3] == 'b'
    assert d[4] == 'b'


def test_nearest_prev():
    d = NearestDict(rounding=NearestDict.NEAREST_PREV)

    d[0] = 'a'
    d[3] = 'b'
    with pytest.raises(KeyError):
        d[-1]
    assert d[0] == 'a'
    assert d[1] == 'a'
    assert d[2] == 'a'
    assert d[3] == 'b'
    assert d[4] == 'b'


def test_nearest_next():
    d = NearestDict(rounding=NearestDict.NEAREST_NEXT)

    d[0] = 'a'
    d[3] = 'b'
    assert d[-1] == 'a'
    assert d[0] == 'a'
    assert d[1] == 'b'
    assert d[2] == 'b'
    assert d[3] == 'b'
    with pytest.raises(KeyError):
        d[4]


@pytest.mark.parametrize(
    'rounding',
    [
        NearestDict.NEAREST,
        NearestDict.NEAREST_NEXT,
        NearestDict.NEAREST_PREV,
    ],
)
@pytest.mark.parametrize(
    'keys',
    [
        [timedelta.max],
        [timedelta(0), timedelta.max],
        [timedelta(0), timedelta(days=1)],
    ],
)
def test_lower_boundary_timedelta(rounding, keys):
    mapping = NearestDict(dict.fromkeys(keys, 'first'), rounding=rounding)
    if rounding == NearestDict.NEAREST_PREV:
        with pytest.raises(KeyError, match='No key below'):
            mapping.nearest_key(timedelta.min)
        with pytest.raises(KeyError, match='No key below'):
            mapping[timedelta.min]
    else:
        assert mapping.nearest_key(timedelta.min) is keys[0]
        assert mapping[timedelta.min] == 'first'
    assert list(mapping) == keys
    mapping._check()


@pytest.mark.parametrize(
    'rounding',
    [
        NearestDict.NEAREST,
        NearestDict.NEAREST_NEXT,
        NearestDict.NEAREST_PREV,
    ],
)
def test_exact_boundary_timedelta(rounding):
    keys = [timedelta.min, timedelta.max]
    mapping = NearestDict(dict.fromkeys(keys, 'boundary'), rounding=rounding)
    assert mapping.nearest_key(timedelta.min) is keys[0]
    assert mapping.nearest_key(timedelta.max) is keys[1]
    assert mapping[timedelta.min] == mapping[timedelta.max] == 'boundary'
    mapping._check()


@pytest.mark.parametrize(
    'rounding, expected',
    [
        (NearestDict.NEAREST, 0),
        (NearestDict.NEAREST_NEXT, 0),
        (NearestDict.NEAREST_PREV, None),
    ],
)
def test_lower_boundary_single_numeric_key(rounding, expected):
    mapping = NearestDict({0: 'only'}, rounding=rounding)
    if expected is None:
        with pytest.raises(KeyError):
            mapping.nearest_key(-1)
    else:
        assert mapping.nearest_key(-1) == expected
        assert mapping[-1] == 'only'
